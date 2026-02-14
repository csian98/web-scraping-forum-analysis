import re
import hashlib
from datetime import datetime
from typing import List, Dict
import json
import emoji
from sklearn.feature_extraction.text import TfidfVectorizer


class Preprocessor:
    def __init__(self):
        pass

    def preprocess_posts(self, posts: List[Dict], subreddit: str) -> List[Dict]:
        """
        - Remove HTML tags and special characters
        - Filter out promoted/advertisement posts
        - Convert timestamps
        - Mask usernames for privacy
        - Extract relevant fields
        """
        processed_posts = []

        print(f"\nPreprocessing posts from r/{subreddit}...")

        for post in posts:
            # Skip ads/promoted posts
            if post.get("promoted") or post.get("is_sponsored"):
                continue

            # Skip advertisment
            if (
                post.get("author") == "AutoModerator"
                and "promoted" in post.get("title", "").lower()
            ):
                continue

            processed_post = {
                "post_id": post.get("id", ""),
                "title": self._clean_text(post.get("title", "")),
                "selftext": self._clean_text(post.get("selftext", "")),
                "author_hash": self._mask_username(post.get("author", "")),
                "score": post.get("score", 0),
                "upvote_ratio": post.get("upvote_ratio", 0),
                "num_comments": post.get("num_comments", 0),
                "created_utc": self._convert_timestamp(post.get("created_utc", 0)),
                "url": post.get("url", ""),
                "permalink": f"https://www.reddit.com{post.get('permalink', '')}",
                "is_self": post.get("is_self", False),
                "link_flair_text": post.get("link_flair_text", ""),
                "domain": post.get("domain", ""),
                "subreddit": subreddit,
                "is_video": post.get("is_video", False),
                "over_18": post.get("over_18", False),
            }

            processed_posts.append(processed_post)

        filtered_count = len(posts) - len(processed_posts)
        print(
            f"Processed {len(processed_posts)} posts (filtered out {filtered_count} promoted/ads)"
        )

        post_text = [
            f"{post['title']} {post['selftext']}".strip() for post in processed_posts
        ]

        keywords = self._extract_keywords(post_text)

        for post, kw in zip(processed_posts, keywords):
            post["keywords"] = kw

        return processed_posts

    def _extract_keywords(self, texts, top_k=5):
        vectorizer = TfidfVectorizer(
            stop_words="english", max_df=0.9, min_df=2, ngram_range=(1, 2)
        )
        tfidf = vectorizer.fit_transform(texts)
        feature_names = vectorizer.get_feature_names_out()

        keywords_per_doc = []
        for row in tfidf:
            indices = row.toarray()[0].argsort()[-top_k:][::-1]
            keywords = [feature_names[i] for i in indices]
            keywords_per_doc.append(keywords)

        return keywords_per_doc

    def _clean_text(self, text: str) -> str:
        """Remove HTML tags, special characters, and clean text"""
        if not text:
            return ""

        # Remove HTML tags
        text = re.sub(r"<[^>]+>", "", text)

        # Decode HTML entities
        text = text.replace("&amp;", "&")
        text = text.replace("&lt;", "<")
        text = text.replace("&gt;", ">")
        text = text.replace("&quot;", '"')
        text = text.replace("&#x200B;", "")  # Zero-width space
        text = text.replace("&nbsp;", " ")

        # Remove excessive whitespace
        text = re.sub(r"\s+", " ", text)
        text = text.strip()

        text = re.sub(r"https?://\S+|www\.\S+", "", text)
        text = re.sub(r"[^a-zA-Z0-9\s]", "", text)
        text = emoji.replace_emoji(text, replace="")

        return text

    def _mask_username(self, username: str) -> str:
        """Hash username for privacy protection"""

        if not username or username == "[deleted]":
            return "deleted_user"

        # Create hash of username
        hash_object = hashlib.sha256(username.encode())
        hash_hex = hash_object.hexdigest()

        return f"user_{hash_hex[:8]}"

    def _convert_timestamp(self, unix_timestamp: float) -> str:
        if not unix_timestamp:
            return ""

        dt = datetime.fromtimestamp(unix_timestamp)
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    def save_to_json(self, posts: List[Dict], filepath: str):
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(posts, f, indent=2, ensure_ascii=False)

        print(f"Saved {len(posts)} posts to {filepath}")
