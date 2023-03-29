import time
import feedparser
import requests
import sys
from datetime import datetime

DATADOG_STATUS_FEED_URL = "https://status.datadoghq.com/history.rss"
INTERVAL_SECONDS = 60 * 5  # 5分ごとにチェック
WEBHOOK_URL = "https://hooks.slack.com/services/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"  # 通知を送信するWebhook URL
LOG_FILE_PATH = "/root/develop/python/excute.log"  # ログファイルのパスを指定

error_count = 0 #except処理のエラー回数初期値を定義
max_errors = 3  #except処理のエラー回数最大値を定義

def send_notification(message):
    payload = {"text": message}
    requests.post(WEBHOOK_URL, json=payload)

def main():
    with open(LOG_FILE_PATH, "a") as f:
        original_stdout = sys.stdout
        try:
            sys.stdout = f  # 標準出力をログファイルにリダイレクト
            print("Script started")

            last_checked_time = datetime.utcnow()
            print(last_checked_time)

            while True:
                try:
                    feed = feedparser.parse(DATADOG_STATUS_FEED_URL)
                    for entry in feed.entries:
                        entry_time = datetime.fromtimestamp(time.mktime(entry.published_parsed))
                        print(entry_time)
                        if entry_time > last_checked_time:
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
