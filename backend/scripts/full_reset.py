import boto3
import time
import os

MOVIES_TABLE_NAME = os.environ.get("MOVIES_TABLE", "movies-table")
RATINGS_TABLE_NAME = os.environ.get("RATINGS_TABLE", "ratings-table")
REGION = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")

dynamodb = boto3.resource('dynamodb', region_name=REGION)

def delete_table(table_name):
    table = dynamodb.Table(table_name)
    try:
        print(f"Deleting {table_name}...")
        table.delete()
        table.wait_until_not_exists()
        print(f"Deleted {table_name}.")
    except Exception as e:
        if "ResourceNotFoundException" in str(e):
            print(f"{table_name} does not exist.")
        else:
            print(f"Error deleting {table_name}: {e}")

def create_movies_table():
    try:
        print(f"Creating {MOVIES_TABLE_NAME}...")
        table = dynamodb.create_table(
            TableName=MOVIES_TABLE_NAME,
            KeySchema=[{'AttributeName': 'movie_id', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'movie_id', 'AttributeType': 'S'}],
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        )
        table.wait_until_exists()
        print(f"Table {MOVIES_TABLE_NAME} created.")
    except Exception as e:
        print(f"Error creating {MOVIES_TABLE_NAME}: {e}")

def create_ratings_table():
    try:
        print(f"Creating {RATINGS_TABLE_NAME}...")
        table = dynamodb.create_table(
            TableName=RATINGS_TABLE_NAME,
            KeySchema=[
                {'AttributeName': 'user_id', 'KeyType': 'HASH'},
                {'AttributeName': 'movie_id', 'KeyType': 'RANGE'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'user_id', 'AttributeType': 'S'},
                {'AttributeName': 'movie_id', 'AttributeType': 'S'}
            ],
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        )
        table.wait_until_exists()
        print(f"Table {RATINGS_TABLE_NAME} created.")
    except Exception as e:
        print(f"Error creating {RATINGS_TABLE_NAME}: {e}")

if __name__ == "__main__":
    delete_table(MOVIES_TABLE_NAME)
    delete_table(RATINGS_TABLE_NAME)
    create_movies_table()
    create_ratings_table()
