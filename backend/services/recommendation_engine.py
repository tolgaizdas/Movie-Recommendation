import pandas as pd
from typing import List
from ..models import Movie
from ..db import get_movies_table, get_ratings_table
# from sklearn.metrics.pairwise import cosine_similarity (Removed for lambda size optimization)
import time

class RecommendationEngine:
    def __init__(self):
        self.last_fetch = 0
        self.cached_ratings_df = None
        self.movies_cache = {}

    def _fetch_data(self):
        # Redis Caching Implementation
        import redis
        import pickle
        import os

        REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
        REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
        
        try:
            r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, socket_timeout=1)
            # Try to get data from Redis
            cached_data = r.get('ratings_dataframe')
            if cached_data:
                print("Cache Hit! Loading ratings from Redis...")
                self.cached_ratings_df = pickle.loads(cached_data)
                return
        except Exception as e:
            print(f"Redis error: {e}")

        # Cache Miss - Fetch from DynamoDB (Source of Truth)
        if self.cached_ratings_df is not None and time.time() - self.last_fetch < 600:
             return

        print("Cache Miss. Fetching ratings from DynamoDB...")
        ratings_table = get_ratings_table()
        
        # Scan all ratings
        response = ratings_table.scan(ProjectionExpression="user_id, movie_id, rating")
        items = response.get('Items', [])
        while 'LastEvaluatedKey' in response:
            response = ratings_table.scan(
                ProjectionExpression="user_id, movie_id, rating",
                ExclusiveStartKey=response['LastEvaluatedKey']
            )
            items.extend(response.get('Items', []))
            
        print(f"Fetched {len(items)} ratings from DB.")
        
        # Convert to DataFrame
        self.cached_ratings_df = pd.DataFrame(items)
        if not self.cached_ratings_df.empty:
            self.cached_ratings_df['rating'] = pd.to_numeric(self.cached_ratings_df['rating'])
            
            # Save to Redis (TTL 1 hour)
            try:
                r.setex('ratings_dataframe', 3600, pickle.dumps(self.cached_ratings_df))
                print("Saved ratings to Redis cache.")
            except Exception as e:
                print(f"Failed to save to Redis: {e}")
        
        self.last_fetch = time.time()

    def _get_movie_details(self, movie_ids: List[str]) -> List[Movie]:
        movies_table = get_movies_table()
        results = []
        for mid in movie_ids:
            # Check memory cache first
            if mid in self.movies_cache:
                results.append(self.movies_cache[mid])
                continue
            
            # Fetch from DB
            resp = movies_table.get_item(Key={'movie_id': str(mid)})
            if 'Item' in resp:
                item = resp['Item']
                movie = Movie(**item)
                self.movies_cache[mid] = movie
                results.append(movie)
        return results

    def get_recommendations(self, user_id: str, k: int = 5) -> List[Movie]:
        self._fetch_data()
        
        if self.cached_ratings_df is None or self.cached_ratings_df.empty:
            return []

        # Pivot to User-Item Matrix
        # Rows: Users, Cols: Movies
        user_movie_matrix = self.cached_ratings_df.pivot_table(
            index='user_id', 
            columns='movie_id', 
            values='rating'
        ).fillna(0)
        
        # Check if user exists in matrix
        # Note: If user is new (no ratings), we can't do CF efficiently this way.
        # Fallback to popular items or empty.
        if user_id not in user_movie_matrix.index:
            print(f"User {user_id} not found in ratings matrix. Returning popular movies (Mock).")
            # Fallback logic: return top rated movies generally
            top_movies = self.cached_ratings_df.groupby('movie_id')['rating'].mean().sort_values(ascending=False).head(k)
            print(f"Top movies found: {top_movies.index.tolist()}")
            details = self._get_movie_details(top_movies.index.tolist())
            print(f"Details found: {len(details)}")
            return details

        # Item-Based CF: Compute item similarity
        # Transpose so rows are movies
        item_user_matrix = user_movie_matrix.T
        
        # This is computationally intensive (9000x9000 matrix).
        # For PROTOTYPE verify if this times out. 
        # Alternatively, use User-Based CF (600 users is smaller).
        
        # Let's try User-Based CF for speed (600x600 matrix is tiny)
        
        # Manual Cosine Similarity using Numpy avoiding scikit-learn (huge dependency)
        # Cosine Sim(A, B) = Dot(A, B) / (Norm(A) * Norm(B))
        import numpy as np
        
        # 1. Normalize the matrix (L2 norm)
        # Using pure numpy for performance
        matrix_values = user_movie_matrix.values
        norm = np.linalg.norm(matrix_values, axis=1, keepdims=True)
        # Avoid division by zero
        norm[norm == 0] = 1e-10
        normalized_matrix = matrix_values / norm
        
        # 2. Compute similarity (Dot product of normalized vectors)
        user_similarity = np.dot(normalized_matrix, normalized_matrix.T)
        
        user_sim_df = pd.DataFrame(user_similarity, index=user_movie_matrix.index, columns=user_movie_matrix.index)
        
        # Find similar users
        similar_users = user_sim_df[user_id].sort_values(ascending=False).iloc[1:6] # Top 5 similar users
        
        recommended_movies = set()
        watched_movies = set(user_movie_matrix.loc[user_id][user_movie_matrix.loc[user_id] > 0].index)
        
        for similar_user in similar_users.index:
            # Get movies rated highly by similar user
            user_ratings = user_movie_matrix.loc[similar_user]
            top_rated = user_ratings[user_ratings > 4].index.tolist()
            
            for movie in top_rated:
                if movie not in watched_movies:
                    recommended_movies.add(movie)
                    if len(recommended_movies) >= k:
                        break
            if len(recommended_movies) >= k:
                break
                
        return self._get_movie_details(list(recommended_movies)[:k])
 
engine = RecommendationEngine()
