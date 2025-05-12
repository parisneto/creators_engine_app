#!/bin/bash
set -e # Exit on error
set -u # Treat unset variables as an error
# set -o pipefail

echo "--- Starting Fast Dev App Build & Deploy (dev-ci) ---"
START_TIME=$(date +%s)
echo "START_TIME : $START_TIME"
# --- Configuration ---
PROJECT_ID="fleet-gamma-448616-m1"
REGION="us-central1"
REPO_NAME="creatorsengine-app-repo"
BASE_IMAGE_NAME="dev-base"       # Name of the base image artifact to USE
DEV_APP_IMAGE_NAME="dev-app"   # Name for the frequently built app image artifact
# SERVICE_NAME="creatorsengine-dev" # Your DEV Cloud Run service name
SERVICE_NAME="ai-labs-creatorsengine-app" # Your DEV Cloud Run service name
SERVICE_ACCOUNT_EMAIL="streamlit-app-runner@fleet-gamma-448616-m1.iam.gserviceaccount.com"
BASE_TAG="latest" # The tag of the base image to use (must exist)

# --- Get Absolute Path to Project Root ---
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
PROJECT_ROOT=$( cd -- "${SCRIPT_DIR}/.." &> /dev/null && pwd ) # Go up one level from dev-ci
echo "---------------------------------"
echo "Script Dir:       $SCRIPT_DIR"
echo "Project Root:    $PROJECT_ROOT"
echo "---------------------------------"


# --- Generate Unique Tag for the Dev App Image ---
cd "$PROJECT_ROOT" # Change to root dir for git commands & build context
echo "Working directory: $(pwd)"

if [[ -n "$(git status --porcelain)" ]]; then
  echo "WARNING: Uncommitted changes detected. Using timestamp for tag."
  COMMIT_SHA=$(date +%Y%m%d-%H%M%S)
elif [[ -n "$(git rev-parse --short HEAD 2>/dev/null)" ]]; then
  COMMIT_SHA=$(git rev-parse --short HEAD)
else
  echo "WARNING: Not a git repo or no commits. Using timestamp for tag."
  COMMIT_SHA=$(date +%Y%m%d-%H%M%S)
fi

# --- Define Full Image Tags ---
BASE_IMAGE_TAG="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${BASE_IMAGE_NAME}:${BASE_TAG}"
DEV_APP_IMAGE_TAG="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${DEV_APP_IMAGE_NAME}:${COMMIT_SHA}"

echo "Project Root:        $PROJECT_ROOT"
echo "Project ID:          $PROJECT_ID"
echo "Region:              $REGION"
echo "Repo Name:           $REPO_NAME"
echo "Service Name:        $SERVICE_NAME"
echo "Base Image Tag Used: $BASE_IMAGE_TAG"
echo "Dev App Image Tag:   $DEV_APP_IMAGE_TAG"
echo "---------------------------------"

# --- Step 1: Submit Fast Build using cloudbuild.dev-app.yaml ---
echo "Submitting Cloud Build (using dev-ci/cloudbuild.dev-app.yaml)..."
# Submit from project root '.' as build context
gcloud beta builds submit . \
  --project=$PROJECT_ID \
  --config=dev-ci/cloudbuild.dev-app.yaml `# Path to config relative to root` \
  --region="$REGION" \
  --substitutions=_DEV_APP_IMAGE_TAG="$DEV_APP_IMAGE_TAG",_BASE_IMAGE_TAG="$BASE_IMAGE_TAG"

BUILD_END_TIME=$(date +%s)
echo "Cloud Build finished in $((BUILD_END_TIME - START_TIME)) seconds."
echo "---------------------------------"

# memory 512Mi or 1Gi
# --- Step 2: Deploy the new image to Cloud Run ---
echo "Deploying image $DEV_APP_IMAGE_TAG to Cloud Run service $SERVICE_NAME..."
gcloud run deploy "$SERVICE_NAME" \
  --project="$PROJECT_ID" \
  --image="$DEV_APP_IMAGE_TAG" \
  --region="$REGION" \
  --platform=managed \
  --service-account="$SERVICE_ACCOUNT_EMAIL" \
  --allow-unauthenticated \
  --memory=1Gi \
  --cpu=2 \
  --no-cpu-boost \
  --min-instances=0 \
  --max-instances=2 \
  --timeout=60s \
  --concurrency=80 \
  --port=8080 \
  --update-secrets=/secrets/vision.json=creators-engine-vision-service-account:latest \
  --set-env-vars=GOOGLE_APPLICATION_CREDENTIALS=/secrets/vision.json \
  --quiet

DEPLOY_END_TIME=$(date +%s)
echo "Cloud Run deployment finished in $((DEPLOY_END_TIME - BUILD_END_TIME)) seconds."
echo "---------------------------------"

# --- Finished ---
END_TIME=$(date +%s)
TOTAL_TIME=$((END_TIME - START_TIME))
echo "Fast DEV App Build & Deploy script finished successfully."
echo "Total time: $TOTAL_TIME seconds"
echo "--- All Done (dev-ci) ---"

# # --- Calculate and echo total time spent running this script ---
# END_TIME=$(date +%s)
# TOTAL_TIME=$((END_TIME - START_TIME))
# echo "Total time spent running this script: $TOTAL_TIME seconds"
