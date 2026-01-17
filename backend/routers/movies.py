from fastapi import APIRouter
from typing import List
from models import Movie
from db import get_movies_table
from boto3.dynamodb.conditions import Key

router = APIRouter(
    prefix="/movies",
    tags=["movies"]
)

@router.get("/", response_model=List[Movie])
def get_movies(search: str = None):
    table = get_movies_table()
    try:
        if search:
            # Correct Scan: Loop through all pages to search the whole DB
            from boto3.dynamodb.conditions import Attr
            
            scan_kwargs = {
                'FilterExpression': Attr('title').contains(search),
                'ProjectionExpression': "movie_id, title, genres, #y, average_rating",
                'ExpressionAttributeNames': {"#y": "year"}
            }
            
            done = False
            start_key = None
            items = []
            
            while not done:
                if start_key:
                    scan_kwargs['ExclusiveStartKey'] = start_key
                
                response = table.scan(**scan_kwargs)
                items.extend(response.get('Items', []))
                
                start_key = response.get('LastEvaluatedKey', None)
                done = start_key is None
                
                # Prototype safety: Don't return too many matches
                if len(items) > 20: 
                    items = items[:20]
                    break
            
            print(f"Search: '{search}', Found: {len(items)}")
            return items
        
        # Default behavior: Access Pattern: Get some movies
        response = table.scan(Limit=50)
        items = response.get('Items', [])
        return items
    except Exception as e:
        print(f"Error accessing DynamoDB: {e}")
        return []
