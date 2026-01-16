from fastapi import APIRouter, Depends
from typing import List
from ..models import Movie, RecommendationRequest
from ..services.recommendation_engine import engine
from ..auth import get_current_user

router = APIRouter(
    prefix="/recommendations",
    tags=["recommendations"]
)

@router.post("/", response_model=List[Movie])
def get_recommendations(request: RecommendationRequest, user_id: dict = Depends(get_current_user)):
    # In real app, use user_id from token, not just request body
    # user_uid = user_id['uid'] 
    return engine.get_recommendations(request.user_id, request.num_recommendations)
