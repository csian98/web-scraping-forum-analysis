import argparse
import json
import os
from reddit_scraper import RedditScraper
import os
from preprocess import Preprocessor

def main():
    '''
    Example usage:
    python3 main.py 500 --output output.json --subreddit datascience
    '''
    parser = argparse.ArgumentParser(description= "Reddit Scraper")
    
    parser.add_argument(
        "num_posts",
        type=int,
        help="Number of posts to fetch"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        default="output.json",
        help="Output filename"
    )
    
    parser.add_argument(
        "--subreddit",
        type=str,
        default="datascience",
        help="Subreddit to scrape"
    )
    
    args = parser.parse_args()
    
    # Validate input
    if args.num_posts <= 0:
        print("Error: Number of posts must be positive")
        return
    
    print("="*70)
    print("REDDIT SCRAPER & PREPROCESSOR")
    print(f"Subreddit: r/{args.subreddit}")
    print("="*70 + "\n")
    
    scraper = RedditScraper(subreddit=args.subreddit)

    print("Fetching posts from Reddit...")
    raw_posts = scraper.fetch_posts(args.num_posts)
    
    if not raw_posts:
        print("No posts fetched.")
        return
    
    print(f"\nFetch completed")
    
    print(f"Number of raw posts:{len(raw_posts)}")

    # ===============Preprocess===================

    preprocessor = Preprocessor()
    
    print("\nPreprocessing data...")
    processed_posts = preprocessor.preprocess_posts(raw_posts)
    
    output_path = os.path.join("./data", args.output)
    preprocessor.save_to_json(processed_posts, output_path)
    
    print(f"\nPreprocessing completed.")

if __name__ == "__main__":
    main()