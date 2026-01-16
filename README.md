# Serverless Movie Recommendation App 🎬

A full-stack, serverless application that provides personalized movie recommendations using Collaborative Filtering.

## 🏗 Architecture

The application caches data from DynamoDB into memory (replacing Redis for the serverless Lambda context) and performs recommendation logic on-the-fly.

*   **Frontend**: React, Vite, TailwindCSS (Local)
*   **Auth**: Firebase Authentication
*   **Backend**: FastAPI (Python) running on AWS Lambda
*   **Database**: AWS DynamoDB (Movies & Ratings)
*   **Infrastructure**: AWS SAM (Serverless Application Model)

## 🛠 Tech Stack

| Component | Technology | Reasoning |
|-----------|------------|-----------|
| **Frontend** | React + Vite | Fast, modern UI development. |
| **Styling** | TailwindCSS | Rapid UI scaffolding with a premium look. |
| **Backend** | FastAPI | High-performance Python framework. |
| **Compute** | AWS Lambda | Serverless, cost-effective scaling. |
| **Data** | DynamoDB | NoSQL database for handling regular structured data. |
| **Math** | NumPy | Efficient matrix operations for Cosine Similarity. |

## ✨ Features

1.  **Personalized Recommendations**: Uses User-Based Collaborative Filtering to find users with similar taste and suggests movies they liked.
2.  **My List**:
    *   Search for movies (Case-insensitive, partial match).
    *   Rate movies (1-5 stars).
    *   Remove ratings (manages your profile).
3.  **Cold Start Handling**: New users receive popularity-based recommendations until they rate enough movies.

## 📂 Project Structure

```bash
├── backend/          # FastAPI application
│   ├── routers/      # API endpoints (movies, ratings, recommendations)
│   ├── services/     # Logic (Recommendation Engine)
│   ├── scripts/      # Utility scripts (Import data, Create tables)
│   └── main.py       # App entry point
├── frontend/         # React application
│   ├── src/          # Components and Pages
│   └── .env          # API Configuration
└── infra/            # AWS SAM Infrastructure code
    └── template.yaml # CloudFormation template
```

## ⚡️ How to Run Locally

### 1. Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### 2. Frontend
```bash
cd frontend
npm install
npm run dev
```

## ☁️ Deployment

The project is deployed using AWS SAM.

```bash
cd infra
sam build --use-container
sam deploy --guided
```

This compiles the Python backend (stripping heavy dependencies like scikit-learn for Lambda compatibility) and creates the CloudFormation stack.
