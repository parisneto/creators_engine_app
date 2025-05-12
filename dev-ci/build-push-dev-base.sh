#!/bin/bash
set -e # Exit on error
set -u # Treat unset variables as an error
# set -o pipefail

echo "--- Starting Base Image Build (dev-ci) ---"
START_TIME=$(date +%s)

# --- Configuration ---
PROJECT_ID="fleet-gamma-448616-m1"
REGION="us-central1"
REPO_NAME="creatorsengine-app-repo"
BASE_IMAGE_NAME="dev-base" # Name for the base image artifact
TAG="latest" # Tag for the base image (e.g., latest, v1.0)

BASE_IMAGE_TAG="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${BASE_IMAGE_NAME}:${TAG}"

# --- Get Absolute Path to Project Root ---
# Assumes this script is run from within the dev-ci directory OR the project root
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
PROJECT_ROOT=$( cd -- "${SCRIPT_DIR}/.." &> /dev/null && pwd ) # Go up one level from dev-ci

echo "Project Root:     $PROJECT_ROOT"
echo "Project ID:       $PROJECT_ID"
echo "Region:           $REGION"
echo "Repo Name:        $REPO_NAME"
echo "Base Image Name:  $BASE_IMAGE_NAME"
echo "Full Base Image Tag: $BASE_IMAGE_TAG"
echo "Script Dir:       $SCRIPT_DIR"
echo "---------------------------------"

# --- Submit Base Build to Cloud Build ---
# Run gcloud from the project root directory
cd "$PROJECT_ROOT"
echo "Submitting build from directory: $(pwd)"

gcloud builds submit . \
  --project=$PROJECT_ID \
  --config=dev-ci/cloudbuild.dev-base.yaml `# Path to config relative to root` \
  --substitutions=_BASE_IMAGE_TAG="$BASE_IMAGE_TAG" \
  --region="$REGION"

echo "---------------------------------"
echo "Base image build submitted."
echo "Image will be pushed to: $BASE_IMAGE_TAG"

END_TIME=$(date +%s)
TOTAL_TIME=$((END_TIME - START_TIME))
echo "Script finished in: $TOTAL_TIME seconds"
echo "--- Base Image Build Complete ---"