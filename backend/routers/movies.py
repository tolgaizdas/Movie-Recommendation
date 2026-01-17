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
            # DynamoDB 'contains' is case-sensitive. 
            # For case-insensitive search without a separate index, we scan and filter in Python.
            # Dataset is small (~10k movies, <1MB projected), so this is performant for a prototype.
            
            scan_kwargs = {
                'ProjectionExpression': "movie_id, title, genres, #y, average_rating",
                'ExpressionAttributeNames': {"#y": "year"}
            }
            
            done = False
            start_key = None
            items = []
            search_lower = search.lower()
            
            while not done:
                if start_key:
                    scan_kwargs['ExclusiveStartKey'] = start_key
                
                response = table.scan(**scan_kwargs)
                chunk = response.get('Items', [])
                
                for item in chunk:
                    if search_lower in item.get('title', '').lower():
                        items.append(item)
                        if len(items) >= 20: 
                            break
                            
                if len(items) >= 20:
                    break
                
                start_key = response.get('LastEvaluatedKey', None)
                done = start_key is None
            
            print(f"Search: '{search}', Found: {len(items)}")
            return items
        
        # Default behavior: Access Pattern: Get some movies
        response = table.scan(Limit=50)
        items = response.get('Items', [])
        return items
    except Exception as e:
        print(f"Error accessing DynamoDB: {e}")
        return []
