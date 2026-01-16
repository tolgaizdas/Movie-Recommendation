from pydantic import BaseModel
from typing import List, Optional

class Movie(BaseModel):
    movie_id: str
    title: str
    genres: List[str]
    year: int
    average_rating: float = 0.0

class Rating(BaseModel):
    user_id: str
    movie_id: str
    rating: float
    timestamp: int

class RecommendationRequest(BaseModel):
    user_id: str
    num_recommendations: int = 5
