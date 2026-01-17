import boto3
import os
import time

# Use environment variables or defaults matching template.yaml
MOVIES_TABLE_NAME = os.environ.get("MOVIES_TABLE", "movies-table")
RATINGS_TABLE_NAME = os.environ.get("RATINGS_TABLE", "ratings-table")
REGION = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")

dynamodb = boto3.resource('dynamodb', region_name=REGION)

def create_movies_table():
    try:
        table = dynamodb.create_table(
            TableName=MOVIES_TABLE_NAME,
            KeySchema=[
                {'AttributeName': 'movie_id', 'KeyType': 'HASH'}  # Partition key
            ],
            AttributeDefinitions=[
                {'AttributeName': 'movie_id', 'AttributeType': 'S'}
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        print(f"Creating {MOVIES_TABLE_NAME}...")
        table.wait_until_exists()
        print(f"Table {MOVIES_TABLE_NAME} created successfully.")
    except Exception as e:
        if "ResourceInUseException" in str(e):
            print(f"Table {MOVIES_TABLE_NAME} already exists.")
        else:
            print(f"Error creating {MOVIES_TABLE_NAME}: {e}")

def create_ratings_table():
    try:
        table = dynamodb.create_table(
            TableName=RATINGS_TABLE_NAME,
            KeySchema=[
                {'AttributeName': 'user_id', 'KeyType': 'HASH'},  # Partition key
                {'AttributeName': 'movie_id', 'KeyType': 'RANGE'}  # Sort key
            ],
            AttributeDefinitions=[
                {'AttributeName': 'user_id', 'AttributeType': 'S'},
                {'AttributeName': 'movie_id', 'AttributeType': 'S'}
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        print(f"Creating {RATINGS_TABLE_NAME}...")
        table.wait_until_exists()
        print(f"Table {RATINGS_TABLE_NAME} created successfully.")
    except Exception as e:
        if "ResourceInUseException" in str(e):
            print(f"Table {RATINGS_TABLE_NAME} already exists.")
        else:
            print(f"Error creating {RATINGS_TABLE_NAME}: {e}")

if __name__ == "__main__":
    create_movies_table()
    create_ratings_table()
