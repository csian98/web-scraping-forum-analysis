import requests
import time
from typing import List, Dict, Optional


class RedditScraper:
    
    def __init__(self, subreddit: str = "datascience"):
        self.subreddit = subreddit
        self.base_url = f"https://www.reddit.com/r/{subreddit}.json"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.posts_fetched = 0
        self.max_posts_per_request = 100 # Reddit API limits: ~100 posts per request
        self.request_delay = 2  # seconds between requests to avoid rate limiting
        
    def fetch_posts(self, num_posts: int) -> List[Dict]:

        all_posts = []
        after = None  # Pagination token
        self.posts_fetched = 0
        
        while self.posts_fetched < num_posts:

            posts_remaining = num_posts - self.posts_fetched
            limit = min(self.max_posts_per_request, posts_remaining)
            
            try:
                # Fetch batch with timeout handling
                batch_posts, after = self._fetch_batch(limit, after)
                
                if not batch_posts:
                    print("No more posts available")
                    break
                
                all_posts.extend(batch_posts)
                self.posts_fetched += len(batch_posts)
                
                print(f"Fetched {self.posts_fetched}/{num_posts} posts...")
                
                if after is None:
                    print("Reached end of available posts")
                    break
                
                # Delay
                time.sleep(self.request_delay)
                
            except Exception as e:
                print(e)
                break
        
        print(f"Total posts fetched: {len(all_posts)}")
        return all_posts
    
    def _fetch_batch(self, limit: int, after: Optional[str] = None) -> tuple:
        params = {
            'limit': limit,
            'raw_json': 1  # Prevents HTML encoding
        }
        
        if after:
            params['after'] = after
        
        try:
           
            response = requests.get(
                self.base_url,
                headers=self.headers,
                params=params,
                timeout=30  # 30 second timeout per request
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Extract posts from response
            posts = []
            children = data.get('data', {}).get('children', [])
            
            for child in children:
                post_data = child.get('data', {})
                posts.append(post_data)
            
            # Get pagination token for next request
            next_after = data.get('data', {}).get('after')
            
            return posts, next_after
            
        except requests.exceptions.Timeout:
            print("Request timeout - retrying with shorter timeout...")
            time.sleep(5)
            return self._fetch_batch(limit, after)
        
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            raise