from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from models import Rating, Movie
from db import get_ratings_table, get_movies_table
from auth import get_current_user
import time
from decimal import Decimal

router = APIRouter(
    prefix="/ratings",
    tags=["ratings"]
)

class RatingRequest(BaseModel):
    movie_id: str
    rating: float

@router.post("/")
def rate_movie(request: RatingRequest, user: dict = Depends(get_current_user)):
    user_id = user.get('uid')
    if not user_id:
        raise HTTPException(status_code=401, detail="User ID not found")

    ratings_table = get_ratings_table()
    movies_table = get_movies_table()
    
    # Check for existing rating to handle atomic updates correctly
    old_rating = 0.0
    existing_rating = ratings_table.get_item(Key={'user_id': user_id, 'movie_id': request.movie_id})
    
    if 'Item' in existing_rating:
        old_rating = float(existing_rating['Item']['rating'])
    
    # Save rating to DynamoDB
    item = {
        'user_id': user_id,
        'movie_id': request.movie_id,
        'rating': Decimal(str(request.rating)),
        'timestamp': int(time.time())
    }
    
    try:
        ratings_table.put_item(Item=item)
        
        # Update Movie Aggregation
        rating_val = float(request.rating)
        
        if 'Item' in existing_rating:
             # User is updating their rating. Count stays same, Total changes by difference.
             diff = rating_val - old_rating
             # Avoid DB call if no change
             if diff != 0:
                 movies_table.update_item(
                    Key={'movie_id': request.movie_id},
                    UpdateExpression="SET vote_total = vote_total + :diff",
                    ExpressionAttributeValues={':diff': Decimal(str(diff))}
                )
        else:
            # New Rating. Count +1, Total +Rating
            movies_table.update_item(
                Key={'movie_id': request.movie_id},
                UpdateExpression="SET vote_count = vote_count + :inc, vote_total = vote_total + :val",
                ExpressionAttributeValues={':inc': 1, ':val': Decimal(str(rating_val))}
            )

        return {"message": "Rating saved and aggregated successfully"}
    except Exception as e:
        print(f"Error saving rating: {e}")
        raise HTTPException(status_code=500, detail="Failed to save rating")

@router.delete("/{movie_id}")
def delete_rating(movie_id: str, user: dict = Depends(get_current_user)):
    user_id = user.get('uid')
    if not user_id:
        raise HTTPException(status_code=401, detail="User ID not found")

    ratings_table = get_ratings_table()
    movies_table = get_movies_table()
    
    # Get rating value before deleting to update aggregation
    resp = ratings_table.get_item(Key={'user_id': user_id, 'movie_id': movie_id})
    if 'Item' not in resp:
        raise HTTPException(status_code=404, detail="Rating not found")
        
    rating_val = float(resp['Item']['rating'])
    
    try:
        ratings_table.delete_item(
            Key={
                'user_id': user_id,
                'movie_id': movie_id
            }
        )
        
        # Decrement Aggregation
        movies_table.update_item(
            Key={'movie_id': movie_id},
            UpdateExpression="SET vote_count = vote_count - :dec, vote_total = vote_total - :val",
            ExpressionAttributeValues={':dec': 1, ':val': Decimal(str(rating_val))}
        )
        
        return {"message": "Rating removed/deleted successfully"}
    except Exception as e:
        print(f"Error deleting rating: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete rating")

@router.get("/", response_model=List[dict])
def get_user_ratings(user: dict = Depends(get_current_user)):
    user_id = user.get('uid')
    if not user_id:
        raise HTTPException(status_code=401, detail="User ID not found")

    ratings_table = get_ratings_table()
    movies_table = get_movies_table()
    
    try:
        # 1. Get all ratings for user
        response = ratings_table.query(
            KeyConditionExpression='user_id = :uid',
            ExpressionAttributeValues={
                ':uid': user_id
            }
        )
        ratings = response.get('Items', [])
        
        if not ratings:
            return []
            
        # 2. Get details for each movie (BatchGetItem is better but simple loop is okay for <100 items for prototype)
        # Using BatchGetItem is robust.
        # However, DynamoDB BatchGetItem requires Keys.
        
        # Let's use a simple approach: Fetch all movie IDs then batch get.
        from boto3.dynamodb.conditions import Key
        
        results = []
        for r in ratings:
             # Fetch individual movie (Optimization: Could use BatchGetItem here)
             movie_resp = movies_table.get_item(Key={'movie_id': r['movie_id']})
             movie = movie_resp.get('Item')
             
             if movie:
                 # Use Pydantic model to compute average_rating
                 movie_obj = Movie(**movie)
                 dump = movie_obj.model_dump()
                 dump['my_rating'] = r['rating']
                 results.append(dump)
                 
        return results

    except Exception as e:
        print(f"Error fetching ratings: {e}")
        return []
