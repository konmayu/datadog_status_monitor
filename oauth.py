import os
import time
import feedparser
import requests
import sys
from datetime import datetime
from dotenv import load_dotenv

# .envをロード
load_dotenv()

DATADOG_STATUS_FEED_URL = "https://status.datadoghq.com/history.rss"
INTERVAL_SECONDS = 60 * 5  # 5分ごとにチェック
WEBHOOK_URL = os.getenv("DATADOG_WEBHOOK_URL")
SLACK_API_TOKEN = os.getenv("SLACK_API_TOKEN")
SLACK_CHANNEL = "C050KA3RP27"


error_count = 0 #except処理のエラー回数初期値を定義
max_errors = 3  #except処理のエラー回数最大値を定義

def send_notification(message):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {SLACK_API_TOKEN}",
    }

    data = {
        "channel": SLACK_CHANNEL,
        "text": message,
    }

    response = requests.post("https://slack.com/api/chat.postMessage", json=data, headers=headers)

    if response.status_code != 200:
        print(f"Error sending message to Slack: {response.status_code} - {response.text}")

def main():
    # 出力するログファイルの設定を記述
    script_dir = os.path.dirname(os.path.abspath(__file__))
    current_date = datetime.now().strftime("%y%m%d_%S")
    log_file_name = f"excute_{current_date}.log"
    log_file_path = os.path.join(script_dir, log_file_name)

    with open(log_file_path, "a") as f:
        original_stdout = sys.stdout
        try:
            sys.stdout = f  # 標準出力をログファイルにリダイレクト
            print("Script started")
            # スクリプト実行開始を通知る
            send_notification(f"script is started, LogFileName is {log_file_name} and path {log_file_path}")

            last_checked_time = datetime.utcnow()
            print(last_checked_time)

            while True:
                try:
                    feed = feedparser.parse(DATADOG_STATUS_FEED_URL)
                    for entry in feed.entries:
                        entry_time = datetime.fromtimestamp(time.mktime(entry.published_parsed))
                        print(entry_time)
                        if entry_time > last_checked_time:
                        #if entry_time < last_checked_time:
                            send_notification(f"{entry_time} : Datadog Status Update: {entry.title} - {entry.link}")
                            print(f"Notification sent at {datetime.now()}")
                except Exception as e:
                    print(f"Error while checking feed: {e}")
                    error_count += 1
                    if error_count >= max_errors:
                        send_notification("Error count reached the maximum limit. Please check the script.")
                        print("Too many errors, exiting...")
                        break

                last_checked_time = datetime.utcnow()
                time.sleep(INTERVAL_SECONDS)
        finally:
            sys.stdout = original_stdout

if __name__ == "__main__":
    main()
