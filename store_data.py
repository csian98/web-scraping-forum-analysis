import argparse
from reddit_scraper import RedditScraper
from preprocess import Preprocessor
from snowflake_util import get_connection, load_posts_to_staging, merge_to_posts
import os
import pandas as pd

parser = argparse.ArgumentParser(description="Reddit Scraper")

parser.add_argument("num_posts", type=int, help="Number of posts to fetch")

args = parser.parse_args()

# Validate input
if args.num_posts <= 0:
    raise ValueError("Number of posts must be positive")

if args.num_posts > 5000:
    raise ValueError(
        "Number of posts must be less than or equal to 5000 to avoid rate limits"
    )

subreddits = [
    "datascience",
    "tech",
    "math",
    "programming",
    "ArtificialInteligence",
    "shortstories",
]
posts_per_subreddit = args.num_posts // len(subreddits)
all_posts = []

print("=" * 70)
print("REDDIT SCRAPER & PREPROCESSOR")
for subreddit in subreddits:
    if posts_per_subreddit <= 0:
        break

    print(f"\nSubreddit: r/{subreddit}")
    print("=" * 70 + "\n")

    scraper = RedditScraper(subreddit=subreddit)

    print("Fetching posts from Reddit...")
    raw_posts = scraper.fetch_posts(posts_per_subreddit)

    if scraper.posts_fetched == 0:
        print(f"No posts fetched from r/{subreddit}. Skipping to next subreddit.")
        continue

    processed_posts = Preprocessor().preprocess_posts(raw_posts, subreddit=subreddit)

    all_posts.extend(processed_posts)

if not all_posts:
    print("No posts fetched from any subreddit.")
    exit()

print(f"\nFetch completed")

print(f"Number of raw posts:{len(all_posts)}")
print(f"\nPreprocessing completed.")

posts_df = pd.DataFrame(all_posts)
posts_df.to_csv("data/raw_posts.csv", index=False)

con = get_connection()
load_posts_to_staging(posts_df, con)
merge_to_posts(con)
con.close()
