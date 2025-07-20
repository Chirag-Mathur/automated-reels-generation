# Main pipeline runner for all schedulers

def run_all_schedulers():
    """
    Runs all scheduler steps in sequence.
    Schedulers 4 (image generation) and 6 (publishing) are placeholders.
    """
    from app.pipelines.scheduler1_fetch_news import fetch_and_store_rss_news
    from app.pipelines.scheduler2_validate_content import process_fetched_articles
    from app.pipelines.scheduler3_script_gen import process_valid_articles
    from app.pipelines.scheduler5_video_gen import process_script_generated_articles

    print("Running Scheduler 1: News Fetch...")
    fetch_and_store_rss_news()

    print("Running Scheduler 2: Content Validation...")
    process_fetched_articles()

    print("Running Scheduler 3: Script Generation...")
    process_valid_articles()

    print("Running Scheduler 4: Image Generation... (Not implemented)")
    # TODO: Implement and call image generation step

    print("Running Scheduler 5: Video Generation...")
    process_script_generated_articles()

    print("Running Scheduler 6: Publishing... (Not implemented)")
    # TODO: Implement and call publishing step

if __name__ == "__main__":
    run_all_schedulers() 