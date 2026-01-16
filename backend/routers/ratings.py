from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from ..models import Rating, Movie
from ..db import get_ratings_table, get_movies_table
from ..auth import get_current_user
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

    table = get_ratings_table()
    
    # Save rating to DynamoDB
    item = {
        'user_id': user_id,
        'movie_id': request.movie_id,
        'rating': Decimal(str(request.rating)),
        'timestamp': int(time.time())
    }
    
    try:
        table.put_item(Item=item)
        return {"message": "Rating saved successfully"}
    except Exception as e:
        print(f"Error saving rating: {e}")
        raise HTTPException(status_code=500, detail="Failed to save rating")

@router.delete("/{movie_id}")
def delete_rating(movie_id: str, user: dict = Depends(get_current_user)):
    user_id = user.get('uid')
    if not user_id:
        raise HTTPException(status_code=401, detail="User ID not found")

    table = get_ratings_table()
    
    try:
        table.delete_item(
            Key={
                'user_id': user_id,
                'movie_id': movie_id
            }
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
                 results.append({
                     **movie,
                     'my_rating': r['rating']
                 })
                 
        return results

    except Exception as e:
        print(f"Error fetching ratings: {e}")
        return []
