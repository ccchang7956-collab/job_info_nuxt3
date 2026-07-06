#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import xml.etree.ElementTree as ET
import sqlite3
import os
import logging
import io
from dotenv import load_dotenv
from datetime import datetime
import traceback
from pathlib import Path

# --- 設定基礎 Logging ---
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
console_handler.setLevel(logging.INFO)

logger = logging.getLogger()
logger.addHandler(console_handler)
logger.setLevel(logging.INFO)

# --- 設定 ---
TABLE_ALL_DATA = 'job_all_data'
TABLE_OPENINGS = 'job_openings'
TABLE_SYSNAM = 'job_sysnam'
TABLE_LOG = 'job_data_update_log'
UNIQUE_COLUMN = 'view_url'

# --- 函式：載入 .env 設定並取得 SQLite 路徑 ---
def load_env_config():
    """載入 .env 檔案並設定 SQLite 資料庫路徑"""
    # script_dir = backend/scripts/
    script_dir = os.path.abspath(os.path.dirname(__file__))
    # backend_dir = backend/
    backend_dir = os.path.dirname(script_dir)
    
    dotenv_path = os.path.join(backend_dir, '.env')

    loaded = load_dotenv(dotenv_path=dotenv_path, verbose=True)
    if not loaded:
        logging.warning(f".env 檔案未在指定路徑 '{dotenv_path}' 找到或載入。將嘗試從現有環境變數讀取。")

    job_data_url = os.getenv('JOB_DATA_URL')
    
    # SQLite 資料庫路徑 (在 backend/database/data/ 目錄下)
    db_path = os.path.join(backend_dir, 'database', 'data', 'job_info.db')
    
    # 也可以從環境變數讀取
    db_path_env = os.getenv('SQLITE_DB_PATH')
    if db_path_env:
        db_path = db_path_env

    if not job_data_url:
        logging.error("環境變數 'JOB_DATA_URL' 未設定。")
        return None, None

    if not os.path.exists(db_path):
        logging.error(f"SQLite 資料庫檔案不存在: {db_path}")
        return job_data_url, None

    logging.info(f"成功載入設定，使用 SQLite 資料庫: {db_path}")
    return job_data_url, db_path


# --- 函式：從 XML URL 獲取資料 ---
def fetch_xml_data(url):
    """從指定的 URL 獲取 XML 資料"""
    try:
        logging.info(f"嘗試從 {url} 獲取 XML 資料...")
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        response.encoding = 'utf-8'
        logging.info(f"成功從 {url} 獲取資料。")
        return response.text
    except requests.exceptions.RequestException as e:
        logging.error(f"無法從 {url} 獲取資料: {e}")
        return None
    except Exception as e:
        logging.error(f"獲取 XML 資料時發生未預期的錯誤: {e}")
        return None


# --- 函式：解析 XML 資料 ---
def parse_xml_data(xml_string):
    """解析 XML 字串，提取職缺資訊"""
    jobs = []
    if not xml_string:
        logging.warning("傳入的 XML 字串為空，無法解析。")
        return jobs
    try:
        logging.info("開始解析 XML 資料...")
        root = ET.fromstring(xml_string)
        announce_date_element = root.find('ANNOUNCE_DATE')
        global_announce_date = announce_date_element.text if announce_date_element is not None else None

        job_count = 0
        skipped_count = 0
        for row in root.findall('ROW'):
            job_data = {}
            job_data['announce_date'] = row.findtext('ANNOUNCE_DATE', global_announce_date)
            job_data['org_id'] = row.findtext('ORG_ID')
            job_data['org_name'] = row.findtext('ORG_NAME')
            job_data['person_kind'] = row.findtext('PERSON_KIND')
            job_data['rank'] = row.findtext('RANK')
            job_data['title'] = row.findtext('TITLE')
            job_data['sysnam'] = row.findtext('SYSNAM')

            number_of_text = row.findtext('NUMBER_OF')
            try:
                job_data['number_of'] = int(number_of_text) if number_of_text and number_of_text.isdigit() else None
            except (ValueError, TypeError):
                job_data['number_of'] = None

            job_data['reserve_num'] = row.findtext('RESERVE_NUM')
            job_data['gender_type'] = row.findtext('GENDER_TYPE')
            job_data['work_place_type'] = row.findtext('WORK_PLACE_TYPE')
            job_data['date_from'] = row.findtext('DATE_FROM')
            job_data['date_to'] = row.findtext('DATE_TO')
            job_data['is_handicap'] = row.findtext('IS_HANDICAP')
            job_data['is_original'] = row.findtext('IS_ORIGINAL')
            job_data['is_local_original'] = row.findtext('IS_LOCAL_ORIGINAL')
            job_data['is_traning'] = row.findtext('IS_TRANING')
            job_data['type'] = row.findtext('TYPE')
            job_data['vitae_email'] = row.findtext('VITAE_EMAIL')
            job_data['work_quality'] = row.findtext('WORK_QUALITY')
            job_data['work_item'] = row.findtext('WORK_ITEM')
            job_data['work_address'] = row.findtext('WORK_ADDRESS')
            job_data['contact_method'] = row.findtext('CONTACT_METHOD')
            job_data['url_link'] = row.findtext('URL_LINK')
            job_data['view_url'] = row.findtext('VIEW_URL')

            work_type_text = row.findtext('Work_Type')
            try:
                job_data['work_type'] = int(work_type_text) if work_type_text and work_type_text.isdigit() else None
            except (ValueError, TypeError):
                job_data['work_type'] = None

            job_data['is_transfer'] = row.findtext('IS_TRANSFER')

            if job_data['view_url']:
                jobs.append(job_data)
                job_count += 1
            else:
                logging.warning(f"發現一筆缺少 VIEW_URL 的記錄，已跳過: ORG_NAME={job_data.get('org_name')}, TITLE={job_data.get('title')}")
                skipped_count += 1

        logging.info(f"成功解析 {job_count} 筆職缺資料，跳過 {skipped_count} 筆缺少 view_url 的資料。")
        return jobs
    except ET.ParseError as e:
        logging.error(f"解析 XML 時發生錯誤: {e}")
        return []
    except Exception as e:
        logging.error(f"解析 XML 資料時發生未預期的錯誤: {e}")
        return []


# --- 函式：獲取資料庫中已存在的 view_url ---
def get_existing_view_urls(db_path, table_name):
    """連接 SQLite 資料庫並獲取指定表中所有已存在的 view_url"""
    existing_urls = set()
    connection = None
    try:
        logging.info(f"開始從表格 '{table_name}' 查詢現有的 view_url...")
        connection = sqlite3.connect(db_path)
        # SQLite 優化設定
        connection.execute("PRAGMA journal_mode=WAL;")
        connection.execute("PRAGMA synchronous=NORMAL;")
        connection.execute("PRAGMA cache_size=-64000;")  # 64MB cache
        connection.execute("PRAGMA temp_store=MEMORY;")
        cursor = connection.cursor()
        query = f"SELECT {UNIQUE_COLUMN} FROM {table_name}"
        cursor.execute(query)
        results = cursor.fetchall()
        existing_urls = {row[0] for row in results if row[0]}
        logging.info(f"從表格 '{table_name}' 成功獲取 {len(existing_urls)} 筆現有的 view_url。")
        cursor.close()
        return existing_urls
    except sqlite3.Error as err:
        logging.error(f"從表格 '{table_name}' 查詢 view_url 錯誤: {err}")
        return None
    except Exception as e:
        logging.error(f"從表格 '{table_name}' 獲取現有 URL 時發生未預期錯誤: {e}")
        return None
    finally:
        if connection:
            connection.close()
            logging.debug(f"資料庫連線已關閉 (get_existing_view_urls: {table_name})。")


# --- 函式：將新工作插入 job_all_data ---
def insert_new_jobs_to_all_data(db_path, new_jobs):
    """將新的工作列表插入 job_all_data"""
    if not new_jobs:
        logging.info(f"沒有新的職缺需要插入 {TABLE_ALL_DATA}。")
        return 0

    inserted_count = 0
    connection = None
    try:
        logging.info(f"準備將 {len(new_jobs)} 筆新職缺插入 {TABLE_ALL_DATA}...")
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        sql = f"""
            INSERT INTO {TABLE_ALL_DATA} (
                announce_date, org_id, org_name, person_kind, rank, title, sysnam,
                number_of, reserve_num, gender_type, work_place_type, date_from, date_to,
                is_handicap, is_original, is_local_original, is_traning, type,
                vitae_email, work_quality, work_item, work_address, contact_method,
                url_link, view_url, work_type, is_transfer
            ) VALUES (
                :announce_date, :org_id, :org_name, :person_kind, :rank,
                :title, :sysnam, :number_of, :reserve_num, :gender_type,
                :work_place_type, :date_from, :date_to, :is_handicap,
                :is_original, :is_local_original, :is_traning, :type,
                :vitae_email, :work_quality, :work_item, :work_address,
                :contact_method, :url_link, :view_url, :work_type,
                :is_transfer
            )
        """
        cursor.executemany(sql, new_jobs)
        connection.commit()
        inserted_count = cursor.rowcount
        logging.info(f"成功插入 {inserted_count} 筆新職缺資料到 {TABLE_ALL_DATA}。")
        cursor.close()
        return inserted_count
    except sqlite3.Error as err:
        logging.error(f"插入資料到 {TABLE_ALL_DATA} 錯誤: {err}")
        if connection:
            try:
                connection.rollback()
                logging.info("交易已回滾。")
            except sqlite3.Error as rb_err:
                logging.error(f"Rollback 錯誤: {rb_err}")
        return -1
    except Exception as e:
        logging.error(f"插入新工作到 {TABLE_ALL_DATA} 時發生未預期錯誤: {e}")
        if connection:
            try:
                connection.rollback()
                logging.info("交易已回滾。")
            except sqlite3.Error as rb_err:
                logging.error(f"Rollback 錯誤: {rb_err}")
        return -1
    finally:
        if connection:
            connection.close()
            logging.debug(f"資料庫連線已關閉 (insert_new_jobs_to_all_data)。")


# --- 函式：獲取 job_sysnam 中的有效 sysnam ---
def get_valid_sysnams(db_path):
    """從 job_sysnam 表獲取所有有效的 sysnam"""
    valid_sysnams = set()
    connection = None
    try:
        logging.info(f"開始從 {TABLE_SYSNAM} 查詢有效的 sysnam...")
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        query = f"SELECT sysnam FROM {TABLE_SYSNAM} WHERE sysnam IS NOT NULL AND sysnam != ''"
        cursor.execute(query)
        results = cursor.fetchall()
        valid_sysnams = {row[0] for row in results}
        logging.info(f"從 {TABLE_SYSNAM} 成功獲取 {len(valid_sysnams)} 個有效的 sysnam。")
        cursor.close()
        return valid_sysnams
    except sqlite3.Error as err:
        logging.error(f"從 {TABLE_SYSNAM} 查詢 sysnam 錯誤: {err}")
        return None
    except Exception as e:
        logging.error(f"獲取有效 sysnam 時發生未預期錯誤: {e}")
        return None
    finally:
        if connection:
            connection.close()
            logging.debug("資料庫連線已關閉 (get_valid_sysnams)。")


# --- 函式：將正式職缺插入 job_openings ---
def insert_official_jobs_to_openings(db_path, official_jobs):
    """將篩選出的正式職缺插入 job_openings (INSERT OR REPLACE)"""
    if not official_jobs:
        logging.info(f"沒有正式職缺需要插入或更新到 {TABLE_OPENINGS}。")
        return 0

    affected_count = 0
    connection = None
    try:
        logging.info(f"準備將 {len(official_jobs)} 筆正式職缺插入或更新到 {TABLE_OPENINGS}...")
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        # SQLite 使用 INSERT OR REPLACE 替代 MySQL 的 ON DUPLICATE KEY UPDATE
        sql = f"""
            INSERT OR REPLACE INTO {TABLE_OPENINGS} (
                announce_date, org_id, org_name, person_kind, rank, title, sysnam,
                number_of, reserve_num, gender_type, work_place_type, date_from, date_to,
                is_handicap, is_original, is_local_original, is_traning, type,
                vitae_email, work_quality, work_item, work_address, contact_method,
                url_link, view_url, work_type, is_transfer
            ) VALUES (
                :announce_date, :org_id, :org_name, :person_kind, :rank,
                :title, :sysnam, :number_of, :reserve_num, :gender_type,
                :work_place_type, :date_from, :date_to, :is_handicap,
                :is_original, :is_local_original, :is_traning, :type,
                :vitae_email, :work_quality, :work_item, :work_address,
                :contact_method, :url_link, :view_url, :work_type,
                :is_transfer
            )
        """
        cursor.executemany(sql, official_jobs)
        connection.commit()
        affected_count = cursor.rowcount
        logging.info(f"成功處理 (插入或更新) {affected_count} 筆正式職缺資料到 {TABLE_OPENINGS}。")
        cursor.close()
        return affected_count
    except sqlite3.Error as err:
        logging.error(f"插入/更新資料到 {TABLE_OPENINGS} 錯誤: {err}")
        if connection:
            try:
                connection.rollback()
                logging.info("交易已回滾。")
            except sqlite3.Error as rb_err:
                logging.error(f"Rollback 錯誤: {rb_err}")
        return -1
    except Exception as e:
        logging.error(f"處理正式職缺到 {TABLE_OPENINGS} 時發生未預期錯誤: {e}")
        if connection:
            try:
                connection.rollback()
                logging.info("交易已回滾。")
            except sqlite3.Error as rb_err:
                logging.error(f"Rollback 錯誤: {rb_err}")
        return -1
    finally:
        if connection:
            connection.close()
            logging.debug(f"資料庫連線已關閉 (insert_official_jobs_to_openings)。")


# --- 函式：記錄執行結果到 job_data_update_log ---
def log_update_result(db_path, action, start_time, end_time, new_records=0, updated_records=0, status='Unknown', error_msg=None, remarks=None):
    """將執行結果記錄到 job_data_update_log 表"""
    connection = None
    remarks_str = str(remarks) if remarks is not None else None
    max_remarks_len = 65530
    if remarks_str and len(remarks_str) > max_remarks_len:
        remarks_str = remarks_str[:max_remarks_len] + "\n... [截斷]"
        logging.warning(f"日誌 remarks 內容過長，已被截斷。 Action: {action}")

    try:
        if not db_path:
            logging.error(f"無法記錄日誌到 {TABLE_LOG}，缺少資料庫路徑。 Action: {action}")
            return

        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        sql = f"""
            INSERT INTO {TABLE_LOG} (
                action, start_time, end_time, new_records, updated_records,
                status, error_message, remarks
            ) VALUES (
                ?, ?, ?, ?, ?, ?, ?, ?
            )
        """
        log_data = (
            action,
            start_time.strftime('%Y-%m-%d %H:%M:%S') if start_time else None,
            end_time.strftime('%Y-%m-%d %H:%M:%S') if end_time else None,
            new_records if new_records >= 0 else 0,
            updated_records if updated_records >= 0 else 0,
            status,
            str(error_msg)[:65535] if error_msg else None,
            remarks_str
        )
        cursor.execute(sql, log_data)
        connection.commit()
        cursor.close()
    except sqlite3.Error as err:
        print(f"CRITICAL: 記錄日誌到 {TABLE_LOG} 時發生資料庫錯誤: {err}. Action: {action}, Status: {status}")
        print(f"Original Error Message: {error_msg}")
    except Exception as e:
        print(f"CRITICAL: 記錄日誌時發生未預期錯誤: {e}. Action: {action}, Status: {status}")
        print(f"Original Error Message: {error_msg}")
    finally:
        if connection:
            connection.close()


# --- 主執行流程 ---
if __name__ == "__main__":
    logging.info("--- 開始執行職缺同步作業 (SQLite 版本) ---")
    overall_start_time = datetime.now()

    # 1. 載入設定
    xml_url, db_path = load_env_config()

    # --- Setup Log Capturing Handler ---
    log_stream = io.StringIO()
    capture_handler = logging.StreamHandler(log_stream)
    capture_handler.setFormatter(log_formatter)
    capture_handler.setLevel(logging.INFO)

    if not xml_url or not db_path:
        logging.critical("設定載入失敗，程式終止。")
        log_update_result(db_path, "初始化", overall_start_time, datetime.now(), status='失敗', error_msg="無法載入設定或找到 SQLite 資料庫", remarks="初始化錯誤，未開始主要流程。")
        exit(1)

    logger.addHandler(capture_handler)

    # --- Step 1: 新增職缺資料處理 ---
    action_step1 = "新增職缺資料處理"
    start_time_step1 = datetime.now()
    status_step1 = "成功"
    error_msg_step1 = None
    new_records_step1 = 0
    new_jobs_inserted_list = []
    log_contents_step1 = ""

    try:
        logging.info(f"--- 開始執行步驟: {action_step1} ---")
        # 2. 獲取 XML 資料
        xml_content = fetch_xml_data(xml_url)
        if not xml_content:
            raise Exception("無法獲取 XML 資料")

        # 3. 解析 XML 資料
        all_jobs_from_xml = parse_xml_data(xml_content)
        if not all_jobs_from_xml and xml_content:
            logging.warning("XML 內容存在但未解析到任何有效職缺資料。")
            status_step1 = "警告"
            error_msg_step1 = "XML 內容存在但未解析到任何有效職缺資料"

        # 4. 獲取 job_all_data 中現有的 view_url
        existing_urls_in_all_data = get_existing_view_urls(db_path, TABLE_ALL_DATA)
        if existing_urls_in_all_data is None:
            raise Exception(f"無法從 {TABLE_ALL_DATA} 獲取現有職缺 URL")

        # 5. 比對找出新的職缺
        new_jobs_to_insert = []
        urls_from_xml = set()
        logging.info("開始比對 XML 資料與資料庫現有資料...")
        for job in all_jobs_from_xml:
            view_url = job.get(UNIQUE_COLUMN)
            if view_url:
                urls_from_xml.add(view_url)
                if view_url not in existing_urls_in_all_data:
                    new_jobs_to_insert.append(job)
                    logging.debug(f"找到新職缺: {view_url}")

        logging.info(f"XML 中共有 {len(urls_from_xml)} 筆不同的職缺。")
        logging.info(f"找到 {len(new_jobs_to_insert)} 筆新的職缺需要插入 {TABLE_ALL_DATA}。")

        # 6. 插入新職缺到 job_all_data
        if new_jobs_to_insert:
            inserted_count = insert_new_jobs_to_all_data(db_path, new_jobs_to_insert)
            if inserted_count >= 0:
                new_records_step1 = inserted_count
                new_jobs_inserted_list = [job for job in new_jobs_to_insert if job[UNIQUE_COLUMN] not in existing_urls_in_all_data]
                logging.info(f"步驟 1: 實際插入 {new_records_step1} 筆資料到 {TABLE_ALL_DATA}。")
            else:
                raise Exception(f"插入新職缺到 {TABLE_ALL_DATA} 失敗")
        else:
            logging.info(f"步驟 1: 沒有發現新的職缺需要插入 {TABLE_ALL_DATA}。")

        logging.info(f"--- 步驟執行完畢: {action_step1} ---")

    except Exception as e:
        status_step1 = "失敗"
        error_msg_step1 = f"{e}\n{traceback.format_exc()}"
        logging.error(f"{action_step1} 執行失敗: {e}", exc_info=False)

    finally:
        logger.removeHandler(capture_handler)
        log_contents_step1 = log_stream.getvalue()
        log_stream.close()

        end_time_step1 = datetime.now()
        log_update_result(db_path, action_step1, start_time_step1, end_time_step1,
                          new_records=new_records_step1, updated_records=0,
                          status=status_step1, error_msg=error_msg_step1,
                          remarks=log_contents_step1)

    # --- Step 2: 篩選正式職缺 ---
    action_step2 = "篩選正式職缺"
    start_time_step2 = datetime.now()
    status_step2 = "成功"
    error_msg_step2 = None
    official_records_processed = 0
    log_contents_step2 = ""

    if status_step1 == "成功" and new_jobs_inserted_list:
        log_stream_step2 = io.StringIO()
        capture_handler_step2 = logging.StreamHandler(log_stream_step2)
        capture_handler_step2.setFormatter(log_formatter)
        capture_handler_step2.setLevel(logging.INFO)
        logger.addHandler(capture_handler_step2)

        try:
            logging.info(f"--- 開始執行步驟: {action_step2} ---")
            # 7. 獲取 job_sysnam 中的有效 sysnam
            valid_sysnams_set = get_valid_sysnams(db_path)
            if valid_sysnams_set is None:
                raise Exception(f"無法從 {TABLE_SYSNAM} 獲取有效的 sysnam")

            # 8. 從新插入的職缺中篩選出正式職缺
            official_jobs_to_process = []
            logging.info(f"開始從 {len(new_jobs_inserted_list)} 筆新插入的職缺中篩選正式職缺...")
            for job in new_jobs_inserted_list:
                sysnam_value = job.get('sysnam')
                if sysnam_value and sysnam_value in valid_sysnams_set:
                    official_jobs_to_process.append(job)
                    logging.debug(f"找到符合條件的正式職缺: view_url={job.get('view_url')}, sysnam={sysnam_value}")

            logging.info(f"從 {len(new_jobs_inserted_list)} 筆新職缺中篩選出 {len(official_jobs_to_process)} 筆正式職缺。")

            # 9. 將正式職缺插入 job_openings
            if official_jobs_to_process:
                affected_count = insert_official_jobs_to_openings(db_path, official_jobs_to_process)
                if affected_count >= 0:
                    official_records_processed = affected_count
                    logging.info(f"步驟 2: 實際處理 (插入/更新) {official_records_processed} 筆資料到 {TABLE_OPENINGS}。")
                else:
                    raise Exception(f"處理正式職缺到 {TABLE_OPENINGS} 失敗")
            else:
                logging.info(f"步驟 2: 沒有符合條件的正式職缺需要處理到 {TABLE_OPENINGS}。")

            logging.info(f"--- 步驟執行完畢: {action_step2} ---")

        except Exception as e:
            status_step2 = "失敗"
            error_msg_step2 = f"{e}\n{traceback.format_exc()}"
            logging.error(f"{action_step2} 執行失敗: {e}", exc_info=False)

        finally:
            logger.removeHandler(capture_handler_step2)
            log_contents_step2 = log_stream_step2.getvalue()
            log_stream_step2.close()

            end_time_step2 = datetime.now()
            log_update_result(db_path, action_step2, start_time_step2, end_time_step2,
                              new_records=0,
                              updated_records=official_records_processed,
                              status=status_step2, error_msg=error_msg_step2,
                              remarks=log_contents_step2)
    elif status_step1 != "成功":
        skip_remark = f"由於步驟 '{action_step1}' 未成功，跳過此步驟。"
        logging.warning(skip_remark)
        log_update_result(db_path, action_step2, start_time_step2, datetime.now(),
                          status='跳過', remarks=skip_remark)
    else:
        no_exec_remark = f"由於步驟 '{action_step1}' 未插入新紀錄，無需執行此步驟。"
        logging.info(no_exec_remark)
        log_update_result(db_path, action_step2, start_time_step2, datetime.now(),
                          status='無需執行', remarks=no_exec_remark)

    overall_end_time = datetime.now()
    logging.info(f"--- 職缺同步作業執行完畢 (總耗時: {overall_end_time - overall_start_time}) ---")

    # =========================================================================
    # Step 3: IndexNow 推送 + Sitemap 快取失效
    # 當有新職缺入庫時，主動通知搜尋引擎並清除 sitemap 快取
    # =========================================================================
    if new_jobs_inserted_list:
        _push_indexnow_and_invalidate_cache(new_jobs_inserted_list, db_path)


def _push_indexnow_and_invalidate_cache(new_jobs: list, db_path: str):
    """推送新職缺 URL 到 IndexNow，並呼叫後端 API 清除 sitemap 快取。"""
    import re
    try:
        # 從 db_path 往上找 .env（backend/ 目錄）
        backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(db_path)))
        dotenv_path = os.path.join(backend_dir, '.env')
        load_dotenv(dotenv_path=dotenv_path, verbose=False)
    except Exception:
        pass

    indexnow_key = os.getenv("INDEXNOW_KEY", "")
    site_domain = os.getenv("SITE_DOMAIN", "https://opendgpa.shibaalin.com").rstrip("/")
    backend_url = os.getenv("BACKEND_URL", "http://localhost:8002")

    # ── 清除 sitemap 快取 ──────────────────────────────────────────────────
    try:
        resp = requests.post(f"{backend_url}/api/seo/invalidate-cache", timeout=10)
        if resp.status_code == 200:
            logging.info("Sitemap cache invalidated via API.")
        else:
            logging.warning(f"Sitemap cache invalidation returned {resp.status_code}")
    except Exception as e:
        logging.warning(f"Could not invalidate sitemap cache: {e}")

    # ── IndexNow 推送 ──────────────────────────────────────────────────────
    if not indexnow_key:
        logging.info("INDEXNOW_KEY not set, skipping IndexNow push.")
        return

    # Add root folder to sys.path to allow importing from app
    import sys
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir) # backend/
    if project_root not in sys.path:
        sys.path.append(project_root)

    from app.Utils.FormatUtils import format_place
    from urllib.parse import quote

    # 從已插入的職缺中提取 ID（從 view_url 取 id 或直接用 rowid）
    job_ids = []
    places_set = set()
    sysnams_set = set()

    for job in new_jobs:
        # view_url 格式通常為 https://web3.dgpa.gov.tw/want03front/AP/...?id=XXXXX
        view_url = job.get("view_url", "")
        # 優先用 id 欄位（若有）
        job_id = job.get("id")
        if job_id:
            job_ids.append(job_id)
        elif view_url:
            # 嘗試從 view_url 提取 id 參數
            match = re.search(r'[?&]id=(\d+)', view_url, re.IGNORECASE)
            if match:
                job_ids.append(match.group(1))

        # 提取縣市
        place_type = job.get("work_place_type")
        if place_type:
            formatted_place = format_place(place_type)
            # 去除行政區保留縣市名 (例如: 臺北市信義區 -> 臺北市)
            match_place = re.match(r'^[^縣市]+[縣市]', formatted_place)
            if match_place:
                places_set.add(match_place.group(0))

        # 提取職系
        sysnam = job.get("sysnam")
        if sysnam and sysnam != "無":
            sysnams_set.add(sysnam)

    if not job_ids:
        logging.info("No job IDs found for IndexNow push.")
        return

    # 構建 URL 列表
    urls = [f"{site_domain}/job/{job_id}" for job_id in job_ids[:400]]  # 職缺 ID 限制 400 筆，預留空間給分類頁面
    for p in places_set:
        urls.append(f"{site_domain}/places/{quote(p.lower())}")
    for s in sysnams_set:
        urls.append(f"{site_domain}/sysnams/{quote(s.lower())}")

    # 去重且最多限額 500 筆
    urls = list(set(urls))[:500]

    host = re.sub(r'^https?://', '', site_domain)
    payload = {
        "host": host,
        "key": indexnow_key,
        "keyLocation": f"{site_domain}/{indexnow_key}.txt",
        "urlList": urls
    }

    try:
        resp = requests.post(
            "https://api.indexnow.org/IndexNow",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=20
        )
        if resp.status_code in (200, 202):
            logging.info(f"IndexNow: successfully pushed {len(urls)} URLs (status={resp.status_code})")
        else:
            logging.warning(f"IndexNow push returned {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        logging.warning(f"IndexNow push failed: {e}")