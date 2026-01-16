#!/bin/bash

# Google Cloud Run Deployment Script
# Usage: ./deploy.sh [project-id] [region]

set -e

# Configuration
PROJECT_ID=${1:-"your-project-id"}
REGION=${2:-"us-central1"}
SERVICE_NAME="beacon-ai-backend"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "📦 Building Docker image for linux/amd64..."
docker build --platform linux/amd64 -t ${IMAGE_NAME} .

echo "🚀 Pushing to Google Container Registry..."
docker push ${IMAGE_NAME}

echo "☁️  Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
  --image ${IMAGE_NAME} \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --memory 4Gi \
  --cpu 4 \
  --timeout 300 \
  --max-instances 5 \
  --port 8080 \
  --set-env-vars "DEM_DATA_PATH=/app/data,MAX_RADIUS_KM=20,NUM_AGENTS=500"

echo "✅ Deployment complete!"
echo "Service URL: https://${SERVICE_NAME}-${REGION}-${PROJECT_ID}.a.run.app"
