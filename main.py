import argparse
import json
import os
from reddit_scraper import RedditScraper
import os

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
    
    # save raw post to a json file
    print(f"Number of raw posts:{len(raw_posts)}")
    output_path = os.path.join("./data", args.output)
    with open(output_path, "w") as f:
        json.dump(raw_posts, f, indent = 4)

if __name__ == "__main__":
    main()