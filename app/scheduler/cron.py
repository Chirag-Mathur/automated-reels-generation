import time
import schedule
from app.pipelines.scheduler1_fetch_news import fetch_and_store_all_domains
from app.pipelines.scheduler3_script_gen import process_valid_articles
from app.pipelines.scheduler5_video_gen import process_script_generated_articles
from app.pipelines.scheduler6_publish import process_video_generated_articles

# Schedule the news fetch job every 15 minutes
schedule.every(15).minutes.do(fetch_and_store_all_domains)
# Schedule the script generation job every 2 hours
schedule.every(2).hours.do(process_valid_articles)

def run_sequential_video_and_publish():
    process_script_generated_articles()
    process_video_generated_articles()

# Schedule the video generation and publishing jobs at specific times
schedule.every().day.at("09:00").do(run_sequential_video_and_publish)
schedule.every().day.at("13:00").do(run_sequential_video_and_publish)
schedule.every().day.at("18:00").do(run_sequential_video_and_publish)
schedule.every().day.at("21:00").do(run_sequential_video_and_publish)

def run_scheduler():
    print("Starting cron scheduler for news fetch (every 15 minutes) and script generation (every 20 minutes)...")
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    run_scheduler() 