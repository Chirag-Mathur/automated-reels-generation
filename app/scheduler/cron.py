import time
import schedule
from app.pipelines.scheduler1_fetch_news import fetch_and_store_all_domains

# Schedule the news fetch job every 15 minutes
schedule.every(15).minutes.do(fetch_and_store_all_domains)

def run_scheduler():
    print("Starting cron scheduler for news fetch (every 15 minutes)...")
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    run_scheduler() 