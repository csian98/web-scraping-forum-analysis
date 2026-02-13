import argparse
from reddit_scraper import RedditScraper
from preprocess import Preprocessor
import os

parser = argparse.ArgumentParser(description= "Reddit Scraper")
    
parser.add_argument(
    "num_posts",
    type=int,
    help="Number of posts to fetch"
)

args = parser.parse_args()

# Validate input
if args.num_posts <= 0:
    raise ValueError("Number of posts must be positive")

if args.num_posts > 5000:
    raise ValueError("Number of posts must be less than or equal to 5000 to avoid rate limits")

subreddits = ["datascience", "tech", "math", "programming", "ArtificialInteligence", "shortstories"]
remaining = args.num_posts
all_raw_posts = []

print("="*70)
print("REDDIT SCRAPER & PREPROCESSOR")
for subreddit in subreddits:
    if remaining <= 0:
        break
    
    print(f"\nSubreddit: r/{subreddit}")
    print("="*70 + "\n")

    scraper = RedditScraper(subreddit=subreddit)

    print("Fetching posts from Reddit...")
    raw_posts = scraper.fetch_posts(remaining)

    if scraper.posts_fetched == 0:
        print(f"No posts fetched from r/{subreddit}. Skipping to next subreddit.")
        continue

    remaining -= scraper.posts_fetched
    all_raw_posts.extend(raw_posts)

if not all_raw_posts:
    print("No posts fetched from any subreddit.")
    exit()

print(f"\nFetch completed")

print(f"Number of raw posts:{len(all_raw_posts)}")

# ===============Preprocess===================

preprocessor = Preprocessor()

print("\nPreprocessing data...")
processed_posts = preprocessor.preprocess_posts(all_raw_posts)

output_path = os.path.join("./data", "output.json")
preprocessor.save_to_json(processed_posts, output_path)

print(f"\nPreprocessing completed.")