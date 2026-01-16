from fastapi import APIRouter
from typing import List
from ..models import Movie
from ..db import get_movies_table
from boto3.dynamodb.conditions import Key

router = APIRouter(
    prefix="/movies",
    tags=["movies"]
)

@router.get("/", response_model=List[Movie])
def get_movies():
    # In a real app, we would support pagination using LastEvaluatedKey
    # For prototype, we just scan for a few items or return mock data
    table = get_movies_table()
    try:
        response = table.scan(Limit=20)
        items = response.get('Items', [])
        # Provide some mock data if DB is valid but empty (common in prototypes)
        if not items:
            return [
                Movie(movie_id="1", title="The Matrix", genres=["Action", "Sci-Fi"], year=1999, average_rating=4.8),
                Movie(movie_id="2", title="Inception", genres=["Action", "Sci-Fi"], year=2010, average_rating=4.7),
                Movie(movie_id="3", title="Interstellar", genres=["Adventure", "Sci-Fi"], year=2014, average_rating=4.6),
            ]
        return items
    except Exception as e:
        print(f"Error accessing DynamoDB: {e}")
        # Fallback for local testing without valid AWS credentials
        return [
             Movie(movie_id="1", title="The Matrix", genres=["Action", "Sci-Fi"], year=1999, average_rating=4.8),
             Movie(movie_id="2", title="Inception", genres=["Action", "Sci-Fi"], year=2010, average_rating=4.7),
        ]
