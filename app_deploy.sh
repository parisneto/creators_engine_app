#!/bin/zsh
set -e   # exit on any error
START_TIME=$(date +%s)

# mdmdeploy.sh (at top)
./app_build.sh || exit 1
# …then your gcloud run deploy…


# --- Set your specific details ---
export PROJECT_ID="fleet-gamma-448616-m1"
export REGION="us-central1"
# export REGION="us-east1"
# <<< CHOOSE & CREATE a repository name for your manual Streamlit builds >>>
export AR_REPO_NAME="creatorsengine-app-repo" # https://console.cloud.google.com/artifacts/docker/fleet-gamma-448616-m1/us-central1/ytdr-repo?cloudshell=true&invt=AbuCfg&project=fleet-gamma-448616-m1
# export AR_REPO_NAME="creatorsengine-app-repo" # RECOMMENDED: Use a new repo for manual builds
# OR use the existing one if you prefer: export AR_REPO_NAME="cloud-run-source-deploy"

export CLOUD_RUN_SERVICE_NAME="ai-labs-creatorsengine-app" # Keep the same service name to update it
# export IMAGE_NAME="streamlit-filter-ui-app" # Give your Streamlit app image a distinct name
export IMAGE_NAME="creators-engine-ia-app-image" # Give your Streamlit app image a distinct name
export LOCAL_APP_DIR="/Users/parisneto/github/yta_mdm_production/apps/ce_app.lab/" # Your local Streamlit code directory

# IMPORTANT: Find your service account email in the GCP Console under IAM & Admin -> Service Accounts
export SERVICE_ACCOUNT_EMAIL="streamlit-app-runner@fleet-gamma-448616-m1.iam.gserviceaccount.com" # <--- REPLACE THIS

# --- Generated variables (usually don't need to change) ---
export IMAGE_TAG="${REGION}-docker.pkg.dev/${PROJECT_ID}/${AR_REPO_NAME}/${IMAGE_NAME}:latest"

# --- Display the full image tag to verify ---
echo "Project ID: ${PROJECT_ID}"
echo "Region: ${REGION}"
echo "Cloud Run Service: ${CLOUD_RUN_SERVICE_NAME}"
echo "Local App Dir: ${LOCAL_APP_DIR}"
echo "Artifact Registry Repo: ${AR_REPO_NAME}"
echo "Image Name: ${IMAGE_NAME}"
echo "Full image tag to be built/deployed: ${IMAGE_TAG}"
echo "Service Account to be used: ${SERVICE_ACCOUNT_EMAIL}"
echo "-----------------------------------------------------"
echo "ACTION: Make sure the Service Account email above is correct!"
echo "ACTION: If using AR_REPO_NAME='streamlit-repo', ensure it's created"
echo "-----------------------------------------------------"




# # --- Command to create 'streamlit-repo' ---
# # Only run this if you set AR_REPO_NAME="streamlit-repo" above AND it doesn't exist yet
# gcloud artifacts repositories create "${AR_REPO_NAME}" \
#   --repository-format=docker \
#   --location="${REGION}" \
#   --description="Repository for manually built Streamlit App Images" \
#   --project="${PROJECT_ID}"

# cd "${LOCAL_APP_DIR}"


# --- Navigate to the App Directory ---
echo "Changing directory to: ${LOCAL_APP_DIR}"
cd "${LOCAL_APP_DIR}" || exit # Exit if cd fails

# --- Verify cloudbuild.yaml and Dockerfile exist ---
if [ ! -f cloudbuild.yaml ]; then
    echo "ERROR: cloudbuild.yaml not found in ${LOCAL_APP_DIR}"
    exit 1
fi
 if [ ! -f .devcontainer/Dockerfile.prod ]; then
    echo "ERROR: Dockerfile not found in ${LOCAL_APP_DIR}/.devcontainer"
    exit 1
fi
echo "cloudbuild.yaml and .devcontainer/Dockerfile.prod found."

# --- Deploy/Update the Cloud Run Service ---
# (The deploy command remains the same as it uses the IMAGE_TAG variable)
  # --memory 512Mi \
echo "Deploying image ${IMAGE_TAG} to service ${CLOUD_RUN_SERVICE_NAME}"
gcloud run deploy "${CLOUD_RUN_SERVICE_NAME}" \
  --image "${IMAGE_TAG}" \
  --platform managed \
  --region "${REGION}" \
  --service-account "${SERVICE_ACCOUNT_EMAIL}" \
  --allow-unauthenticated \
  --project="${PROJECT_ID}" \
  --port 8080 \
  --memory 1Gi \
  --no-cpu-boost \
  --cpu 2 \
  --min-instances 0 \
  --max-instances 2 \
  --timeout 60s \
  --concurrency 80 \
  --update-secrets /secrets/vision.json=creators-engine-vision-service-account:latest \
  --set-env-vars=GOOGLE_APPLICATION_CREDENTIALS=/secrets/vision.json

echo "Build and Deploy script finished."


# --- Calculate and echo total time spent running this script ---
END_TIME=$(date +%s)
TOTAL_TIME=$((END_TIME - START_TIME))
echo "Total time spent running this script: $TOTAL_TIME seconds"

exit



# gcloud run deploy mdm-creatorsengine-app \
# --image=us-central1-docker.pkg.dev/fleet-gamma-448616-m1/ytdr-repo/mdm-creatorsengine-app-image:latest \
# --concurrency=1 \
# --cpu=0.5 \
# --set-env-vars='GOOGLE_APPLICATION_CREDENTIALS=/secrets/vision.json' \
# --set-secrets=/secrets/vision.json=creators-engine-vision-service-account:latest \
# --no-cpu-boost \
# --region=us-central1 \
# --project=fleet-gamma-448616-m1 \
#  && gcloud run services update-traffic mdm-creatorsengine-app --to-latest
