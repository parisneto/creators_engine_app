#!/bin/bash
set -e

PROJECT_ID="fleet-gamma-448616-m1"
REGION="us-central1"
REPO_NAME=creatorsengine-app-repo
IMAGE_TAG="$REGION-docker.pkg.dev/$PROJECT_ID/$REPO_NAME/dev-app:$(date +%s)"

SERVICE_ACCOUNT_EMAIL="streamlit-app-runner@fleet-gamma-448616-m1.iam.gserviceaccount.com"

echo "Building and pushing Docker image..."
gcloud builds submit --tag "$IMAGE_TAG" .

echo "Deploying to Cloud Run..."
gcloud run deploy creatorsengine-dev \
  --image "$IMAGE_TAG" \
  --region "$REGION" \
  --platform managed \
  --service-account "$SERVICE_ACCOUNT_EMAIL" \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 2 \
  --no-cpu-boost \
  --min-instances 0 \
  --max-instances 2 \
  --timeout 60s \
  --concurrency 80 \
  --port 8080 \
  --update-secrets /secrets/vision.json=creators-engine-vision-service-account:latest \
  --set-env-vars=GOOGLE_APPLICATION_CREDENTIALS=/secrets/vision.json \
  --project "$PROJECT_ID"

echo "Deployment complete."
