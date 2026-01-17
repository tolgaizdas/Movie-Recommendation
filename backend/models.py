from pydantic import BaseModel, computed_field
from typing import List, Optional

class Movie(BaseModel):
    movie_id: str
    title: str
    genres: List[str]
    year: int
    vote_count: int = 0
    vote_total: float = 0.0
    
    @computed_field
    @property
    def average_rating(self) -> float:
        if self.vote_count == 0:
            return 0.0
        return round(self.vote_total / self.vote_count, 1)

class Rating(BaseModel):
    user_id: str
    movie_id: str
    rating: float
    timestamp: int

class RecommendationRequest(BaseModel):
    user_id: str
    num_recommendations: int = 5
