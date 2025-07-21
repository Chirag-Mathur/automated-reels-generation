import time
import schedule
from app.pipelines.scheduler1_fetch_news import fetch_and_store_all_domains, fetch_and_store_rss_news
from app.pipelines.scheduler3_script_gen import process_valid_articles
from app.pipelines.scheduler5_video_gen import process_script_generated_articles
from app.pipelines.scheduler6_publish import process_video_generated_articles
from app.pipelines.scheduler2_validate_content import process_fetched_articles

# Schedule the news fetch job every 15 minutes
schedule.every(15).minutes.do(fetch_and_store_rss_news)
# Schedule the scheduler2 validation job every 19 minutes
schedule.every(19).minutes.do(process_fetched_articles)
# Schedule the script generation job every 2 hours
schedule.every(2).hours.do(process_valid_articles)

# def run_sequential_video_and_publish():
#     process_script_generated_articles()
#     process_video_generated_articles()

# # Schedule the video generation and publishing jobs at specific UTC times
# schedule.every().day.at("03:30").do(run_sequential_video_and_publish)
# schedule.every().day.at("07:30").do(run_sequential_video_and_publish)
# schedule.every().day.at("12:30").do(run_sequential_video_and_publish)
# schedule.every().day.at("15:30").do(run_sequential_video_and_publish)

def run_scheduler():
    print("Starting cron scheduler for news fetch (every 15 minutes) and script generation (every 20 minutes)...")
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    run_scheduler() 
