import boto3
import os

# Initialize DynamoDB client
# IF running locally, you might want to point to specific credentials or Local DynamoDB
# For now, we assume standard AWS credentials or Lambda execution role

dynamodb = boto3.resource('dynamodb')

MOVIES_TABLE_NAME = os.environ.get("MOVIES_TABLE", "movies-table")
RATINGS_TABLE_NAME = os.environ.get("RATINGS_TABLE", "ratings-table")

def get_movies_table():
    return dynamodb.Table(MOVIES_TABLE_NAME)

def get_ratings_table():
    return dynamodb.Table(RATINGS_TABLE_NAME)
