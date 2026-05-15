import time
import subprocess
import sys
from datetime import datetime, timedelta

def get_seconds_until_next_5th_minute():
    now = datetime.now()
    # 目標為每小時的 05 分 00 秒
    target = now.replace(minute=5, second=0, microsecond=0)
    
    # 如果現在時間已經超過這個小時的 05 分，就將目標設為「下一個小時的 05 分」
    if now >= target:
        target += timedelta(hours=1)
        
    return (target - now).total_seconds()

if __name__ == "__main__":
    print("啟動 Python 輕量級排程器...", flush=True)
    print("設定執行時間：每小時的第 5 分鐘", flush=True)
    
    while True:
        sleep_seconds = get_seconds_until_next_5th_minute()
        # 額外加上 1 秒的緩衝，避免作業系統 time.sleep() 提早幾毫秒醒來導致在同一分鐘內重複執行
        sleep_seconds += 1.0
        
        next_run_time = datetime.now() + timedelta(seconds=sleep_seconds)
        
        print(f"下次執行時間：{next_run_time.strftime('%Y-%m-%d %H:%M:%S')}", flush=True)
        print(f"系統將進入休眠 {int(sleep_seconds)} 秒...\n", flush=True)
        
        # 暫停直到指定時間
        time.sleep(sleep_seconds)
        
        # 執行原本的腳本
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 開始執行 sync_jobs.py...", flush=True)
        result = subprocess.run([sys.executable, "scripts/sync_jobs.py"])
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 執行完畢，結束代碼: {result.returncode}\n", flush=True)
