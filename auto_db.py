import argparse
import time
import joblib
import numpy as np
from sklearn.cluster import KMeans
from reddit_scraper import RedditScraper
from preprocess import Preprocessor
from snowflake_util import (
    get_connection,
    load_posts_to_staging,
    merge_to_posts,
    set_model_status,
    get_posts_embeddings,
)
import pandas as pd


parser = argparse.ArgumentParser(description="Automation")

parser.add_argument("num_min", type=int, help="Automation frequency in minutes")

args = parser.parse_args()

if args.num_min <= 0:
    raise ValueError("Automation frequency must be positive")

while True:
    print("\n" + "=" * 70)
    print("STARTING AUTOMATION")
    print("=" * 70)

    subreddits = [
        "datascience",
        "tech",
        "math",
        "programming",
        "ArtificialInteligence",
        "shortstories",
    ]
    all_posts = []

    for subreddit in subreddits:
        print(f"\nSubreddit: r/{subreddit}")
        print("=" * 70 + "\n")

        scraper = RedditScraper(subreddit=subreddit)
        raw_posts = scraper.fetch_posts(10)  # Fetch up to 10 posts per subreddit

        if scraper.posts_fetched == 0:
            print(f"No posts fetched from r/{subreddit}. Skipping to next subreddit.")
            continue

        processed_posts = Preprocessor().preprocess_posts(
            raw_posts, subreddit=subreddit
        )
        all_posts.extend(processed_posts)

    if not all_posts:
        print("No posts fetched from any subreddit. Skipping database update.")
    else:
        con = get_connection()

        posts_df = pd.DataFrame(all_posts)
        load_posts_to_staging(posts_df, con)
        num_inserted = merge_to_posts(con)

        if num_inserted > 0:
            set_model_status(con, "TRUE")
            print("\nNew posts inserted. Retraining model...")

            time.sleep(60)

            posts_with_embeddings_df = get_posts_embeddings(con)
            X = posts_with_embeddings_df["EMBEDDING"].to_list()

            y = posts_with_embeddings_df["TOPIC"].to_list()
            labels = np.unique(y)

            model = KMeans(n_clusters=len(labels), init="k-means++", n_init="auto")
            model.fit(X)
            joblib.dump(model, "model/kmeans_model.joblib")

            set_model_status(con, "FALSE")
            print("Model retraining complete.")

        con.close()

    print(
        f"\nAutomation complete. Waiting for {args.num_min} minutes before next run..."
    )
    time.sleep(args.num_min * 60)
