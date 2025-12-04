# LINE_AI/Line_ai_webhook_router.py
import os
import logging
import json
import httpx
from fastapi import APIRouter, Request, Header, HTTPException
from linebot.v3 import WebhookParser
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration, ApiClient, MessagingApi, ReplyMessageRequest,
    TextMessage,
    QuickReply, QuickReplyItem, MessageAction,
    FlexMessage # 使用 FlexMessage
)
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from typing import List, Optional, Dict, Any # Added

from . import Line_ai_openrouter_service as ai_service
from . import Line_ai_db_service as db_service
from . import Line_ai_text_formatter as text_formatter

from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)
router = APIRouter()

LINE_BOT_CHANNEL_SECRET = os.getenv("LINE_AI_BOT_CHANNEL_SECRET")
LINE_BOT_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_AI_BOT_CHANNEL_ACCESS_TOKEN")

parser = None
line_messaging_api = None

if not LINE_BOT_CHANNEL_SECRET or not LINE_BOT_CHANNEL_ACCESS_TOKEN:
    logger.critical("CRITICAL: LINE Bot credentials not loaded!")
else:
    try:
        parser = WebhookParser(LINE_BOT_CHANNEL_SECRET)
        line_config = Configuration(access_token=LINE_BOT_CHANNEL_ACCESS_TOKEN)
        api_client = ApiClient(line_config)
        line_messaging_api = MessagingApi(api_client)
        logger.info(f"[{__name__}] LINE AI Bot webhook parser and API initialized successfully.")
    except Exception as e:
        logger.error(f"[{__name__}] Error initializing LINE SDK for AI Bot: {e}", exc_info=True)

user_conversations: Dict[str, Dict[str, Any]] = {} # Type hint for clarity

def send_reply_message_objects(reply_token: str, messages: list):
    if not line_messaging_api:
        logger.error(f"[{__name__}.send_reply_message_objects] line_messaging_api is None.")
        return
    try:
        logger.debug(f"[{__name__}.send_reply_message_objects] Sending {len(messages)} message objects.")
        for i, msg_obj in enumerate(messages):
           try:
               if hasattr(msg_obj, 'to_dict'):
                   logger.debug(f"Message {i} to_dict: {json.dumps(msg_obj.to_dict(), ensure_ascii=False, indent=2)}")
               else:
                   logger.debug(f"Message {i} (raw object, no to_dict): {msg_obj}")
           except Exception as e_todict:
               logger.error(f"Error converting message {i} to dict: {e_todict}")

        line_messaging_api.reply_message(
            ReplyMessageRequest(reply_token=reply_token, messages=messages)
        )
        logger.info(f"[{__name__}.send_reply_message_objects] Successfully sent reply. Msgs: {len(messages)}")
    except Exception as e:
        logger.error(f"[{__name__}.send_reply_message_objects] Error sending reply (Token: {reply_token}): {e}", exc_info=True)
        try:
            failed_messages_dict = [m.to_dict() if hasattr(m, 'to_dict') else str(m) for m in messages]
            logger.error(f"Failed messages (dict format or str): {json.dumps(failed_messages_dict, ensure_ascii=False)}")
        except Exception as ex_dict:
            logger.error(f"Could not convert failed messages to dict: {ex_dict}")


async def handle_user_interaction(user_id: str, reply_token: str, user_message: str, client: Optional[httpx.AsyncClient] = None):
    logger.info(f"[{__name__}.handle_user_interaction] User: {user_id}, Msg: '{user_message}'")
    
    current_state = user_conversations.get(user_id)

    if current_state and current_state.get("status") == "pending_confirmation":
        confirmed_criteria: Dict[str, Optional[List[str]]] = current_state.get("criteria", {"job_series": None, "location": None})
        
        if user_message.strip().lower() in ["是", "好", "對", "yes", "ok", "確認"]:
            logger.info(f"[{__name__}.handle_user_interaction] User {user_id} confirmed: {confirmed_criteria}")
            
            sysnam_list_to_query = confirmed_criteria.get("job_series")
            location_list_to_query = confirmed_criteria.get("location")

            all_potential_listings = await db_service.query_job_openings_from_db(
                sysnam_list=sysnam_list_to_query,
                location_list=location_list_to_query
            )
            
            messages_to_reply = []
            flex_message_wrapper_dict = text_formatter.create_job_flex_message_dict(all_potential_listings)

            if flex_message_wrapper_dict:
                if flex_message_wrapper_dict.get("type") == "text_message_special":
                    messages_to_reply.append(
                        TextMessage(text=flex_message_wrapper_dict.get("text", "查詢時發生錯誤，請稍後再試."))
                    )
                elif flex_message_wrapper_dict.get("type") == "flex":
                    flex_contents_from_formatter = flex_message_wrapper_dict.get("contents")
                    alt_text_from_formatter = flex_message_wrapper_dict.get("altText", "為您查詢到的職缺資訊")

                    logger.debug(f"[{__name__}.handle_user_interaction] Preparing FlexMessage. AltText: '{alt_text_from_formatter}'")
                    try:
                        logger.debug(f"[{__name__}.handle_user_interaction] flex_contents_from_formatter (raw from formatter): {json.dumps(flex_contents_from_formatter, ensure_ascii=False, indent=2)}")
                    except Exception as e_dump:
                        logger.error(f"Error dumping flex_contents_from_formatter: {e_dump}")
                        logger.debug(f"[{__name__}.handle_user_interaction] flex_contents_from_formatter (raw type): {type(flex_contents_from_formatter)}")

                    if flex_contents_from_formatter:
                        is_carousel = isinstance(flex_contents_from_formatter, dict) and \
                                      flex_contents_from_formatter.get("type") == "carousel"
                        
                        valid_structure = True
                        if is_carousel:
                            carousel_internal_contents = flex_contents_from_formatter.get("contents")
                            if not isinstance(carousel_internal_contents, list) or not carousel_internal_contents:
                                logger.error(f"[{__name__}.handle_user_interaction] Invalid Carousel structure: 'contents' list is missing or empty. Raw: {json.dumps(flex_contents_from_formatter, ensure_ascii=False, indent=2) if isinstance(flex_contents_from_formatter, dict) else str(flex_contents_from_formatter)}")
                                messages_to_reply.append(TextMessage(text="抱歉，生成職缺列表時發生內部錯誤 (Carousel structure error)。"))
                                valid_structure = False
                        
                        if valid_structure:
                            try:
                                flex_message_object = FlexMessage.from_dict(flex_message_wrapper_dict)
                                messages_to_reply.append(flex_message_object)
                                logger.debug(f"[{__name__}.handle_user_interaction] Successfully created FlexMessage object from dict.")
                            except Exception as e_flex_creation:
                                logger.error(f"[{__name__}.handle_user_interaction] Error creating FlexMessage from dict: {e_flex_creation}", exc_info=True)
                                logger.error(f"Failed dict for FlexMessage.from_dict: {json.dumps(flex_message_wrapper_dict, ensure_ascii=False, indent=2)}")
                                messages_to_reply.append(
                                    TextMessage(text="抱歉，準備職缺訊息時發生內部錯誤 (Flex creation error)。")
                                )
                    else:
                        logger.warning(f"[{__name__}.handle_user_interaction] Flex contents missing in wrapper_dict for user {user_id}, though type was 'flex'.")
                        messages_to_reply.append(
                            TextMessage(text="抱歉，無法正確顯示職缺資訊，請稍後再試。")
                        )
                else: 
                    logger.error(f"Unknown message type from text_formatter: {flex_message_wrapper_dict.get('type')}")
                    messages_to_reply.append(
                        TextMessage(text="處理職缺資訊時發生內部錯誤。")
                    )
            else: 
                # Format no results message based on query criteria
                search_terms_msg_parts = []
                if sysnam_list_to_query and any(sysnam_list_to_query):
                    search_terms_msg_parts.append(f"職系「{'、'.join(sysnam_list_to_query)}」")
                if location_list_to_query and any(location_list_to_query):
                    search_terms_msg_parts.append(f"地點「{'、'.join(location_list_to_query)}」")
                
                no_results_text = f"抱歉，目前找不到符合 { ' 及 '.join(search_terms_msg_parts) } 的有效職缺。" if search_terms_msg_parts else "抱歉，目前找不到符合您條件的有效職缺。"
                messages_to_reply.append(
                    TextMessage(text=no_results_text)
                )

            if not messages_to_reply:
                 logger.warning(f"[{__name__}.handle_user_interaction] messages_to_reply is empty before sending for user {user_id}.")
                 messages_to_reply.append(TextMessage(text="查詢完畢，但目前沒有訊息可顯示。"))

            send_reply_message_objects(reply_token, messages_to_reply)
            if user_id in user_conversations: del user_conversations[user_id]

        elif user_message.strip().lower() in ["否", "不對", "取消", "no", "cancel"]:
            logger.info(f"[{__name__}.handle_user_interaction] User {user_id} cancelled confirmation.")
            send_reply_message_objects(reply_token, [
                TextMessage(text="好的，已取消查詢。如果您想重新開始，請告訴我您想找的職系和地點。")
            ])
            if user_id in user_conversations: del user_conversations[user_id]
        else:
            logger.info(f"[{__name__}.handle_user_interaction] User {user_id} new input while pending confirmation, restarting flow.")
            if user_id in user_conversations: del user_conversations[user_id] # Clear old state
            await process_new_query(user_id, reply_token, user_message, client) # Process as new query
    else:
        await process_new_query(user_id, reply_token, user_message, client)

def _format_criteria_for_display(criteria_list: Optional[List[str]], prefix: str) -> str:
    if not criteria_list or not any(criteria_list): # Check if list is None or empty
        return ""
    return f"{prefix}「{ '、'.join(criteria_list) }」"

async def process_new_query(user_id: str, reply_token: str, user_message: str, client: Optional[httpx.AsyncClient] = None):
    logger.info(f"[{__name__}.process_new_query] User: {user_id}, New query: '{user_message}'")
    
    # Criteria will be Dict[str, Optional[List[str]]]
    criteria = await ai_service.get_job_search_criteria_from_ai(user_message, client=client)
    logger.info(f"[{__name__}.process_new_query] AI criteria: {criteria} for user {user_id}")

    extracted_job_series: Optional[List[str]] = criteria.get("job_series")
    extracted_location: Optional[List[str]] = criteria.get("location")

    # Check if both are None or empty lists
    no_job_series = not (extracted_job_series and any(extracted_job_series))
    no_location = not (extracted_location and any(extracted_location))

    if no_job_series and no_location:
        reply_text = "抱歉，我不太明白您的意思。\n請您提供想找的「職系」或「工作地點縣市」。\n例如：「我想找土木工程及資訊處理」或「在桃園市或新竹市的行政職缺」"
        send_reply_message_objects(reply_token, [
            TextMessage(text=reply_text)
        ])
    else:
        confirmation_parts = []
        job_series_display = _format_criteria_for_display(extracted_job_series, "職系")
        if job_series_display:
            confirmation_parts.append(job_series_display)
        
        location_display = _format_criteria_for_display(extracted_location, "地點")
        if location_display:
            confirmation_parts.append(location_display)
        
        criteria_text = " 及 ".join(confirmation_parts)
        confirmation_message_text = f"請問您是想查詢 {criteria_text} 的相關職缺嗎？"
        
        user_conversations[user_id] = {"status": "pending_confirmation", "criteria": criteria}
        
        quick_reply_buttons = QuickReply(items=[
            QuickReplyItem(action=MessageAction(label="是", text="是")),
            QuickReplyItem(action=MessageAction(label="否，重新輸入", text="否")) # "否" will trigger a new query with that text.
        ])
        
        confirmation_message_obj = TextMessage(
            text=confirmation_message_text,
            quick_reply=quick_reply_buttons
        )
        
        send_reply_message_objects(reply_token, [confirmation_message_obj])

@router.post("/webhook", tags=["LINE AI Bot Service"])
async def line_ai_bot_webhook_endpoint(request: Request, x_line_signature: str = Header(None, alias="X-Line-Signature")):
    if not parser or not line_messaging_api:
        logger.error(f"[{__name__}] LINE SDK not initialized.")
        raise HTTPException(status_code=503, detail="LINE Bot service unavailable.")

    if not x_line_signature:
        logger.warning(f"[{__name__}] Missing X-Line-Signature header")
        raise HTTPException(status_code=400, detail="X-Line-Signature missing")

    body = await request.body()
    body_str = body.decode('utf-8')

    try:
        events = parser.parse(body_str, x_line_signature)
    except InvalidSignatureError:
        logger.error(f"[{__name__}] Invalid signature.", exc_info=True)
        raise HTTPException(status_code=400, detail="Invalid signature")
    except Exception as e:
        logger.error(f"[{__name__}] Error parsing events: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal error during parsing.")

    # Retrieve shared HTTP client
    client = getattr(request.app.state, "http_client", None)

    for event in events:
        if isinstance(event, MessageEvent) and isinstance(event.message, TextMessageContent):
            user_id = event.source.user_id if event.source else "UnknownUser"
            reply_token = event.reply_token
            user_message_text = event.message.text
            
            try:
                await handle_user_interaction(user_id, reply_token, user_message_text, client=client)
            except Exception as e_handler:
                logger.error(f"[{__name__}] Unhandled error in handle_user_interaction (User: {user_id}): {e_handler}", exc_info=True)
                # Clear state on unhandled error to prevent inconsistent states
                if user_id in user_conversations:
                    del user_conversations[user_id]
                try: # Try to send an error message to user
                    send_reply_message_objects(reply_token, [
                        TextMessage(text="抱歉，處理您的請求時發生未預期的錯誤，請稍後再試。")
                    ])
                except Exception as e_send_error:
                    logger.error(f"[{__name__}] Failed to send error message to user {user_id}: {e_send_error}")
        else:
            logger.info(f"[{__name__}] Ignored event type {type(event).__name__}")
    return "OK"