#!/bin/zsh
START_TIME=$(date +%s)
# --- Set your specific details ---
export PROJECT_ID="fleet-gamma-448616-m1"
export REGION="us-central1"
# export REGION="southamerica-east1"
# export REGION="us-east1" ERROR: (gcloud.builds.submit) FAILED_PRECONDITION: failed precondition: due to quota restrictions, cannot run builds in this region, see https://cloud.google.com/build/docs/locations#restricted_regions_for_some_projects

# <<< CHOOSE & CREATE a repository name for your manual Streamlit builds >>>
export AR_REPO_NAME="creatorsengine-app-repo" # https://console.cloud.google.com/artifacts/docker/fleet-gamma-448616-m1/us-central1/ytdr-repo?cloudshell=true&invt=AbuCfg&project=fleet-gamma-448616-m1
# export AR_REPO_NAME="streamlit-repo" # RECOMMENDED: Use a new repo for manual builds
# OR use the existing one if you prefer: export AR_REPO_NAME="cloud-run-source-deploy"

export CLOUD_RUN_SERVICE_NAME="ai-labs-creatorsengine-app" # Keep the same service name to update it
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
echo "ACTION: If using AR_REPO_NAME='streamlit-repo', ensure it's created (see step 2)!"
echo "-----------------------------------------------------"
echo "CONFIRM: gcloud config set builds/use_kaniko True "
echo "REVIEW: gcloud config set builds/kaniko_cache_ttl <number_of_hours> "
echo "-----------------------------------------------------"
gcloud config list builds/use_kaniko
gcloud config list builds/kaniko_cache_ttl

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


# --- Submit the build using cloudbuild.yaml ---
echo "Submitting build using cloudbuild.yaml to build image: ${IMAGE_TAG}"
# Use --config and pass the tag via --substitutions
gcloud builds submit --config cloudbuild.yaml \
  --region="${REGION}" \
  --substitutions=_IMAGE_TAG="${IMAGE_TAG}" \
  . --project="${PROJECT_ID}" # '.' is still the source context directory

# --- Calculate and echo total time spent running this script ---
END_TIME=$(date +%s)
TOTAL_TIME=$((END_TIME - START_TIME))

# echo "The final size of the built image is:"
# # Get image size
# # docker image ls -s "${IMAGE_TAG}"
# # gcloud artifacts docker images list "${IMAGE_TAG}" --project="${PROJECT_ID}"
# # gcloud artifacts docker images list us-central1-docker.pkg.dev/fleet-gamma-448616-m1/ytdr-repo/mdm-creatorsengine-app --project="fleet-gamma-448616-m1"
# gcloud artifacts docker images list \
#   "${REGION}-docker.pkg.dev/${PROJECT_ID}/${AR_REPO_NAME}/${IMAGE_NAME}" \
#   --project="${PROJECT_ID}"

echo "Total time spent running this script: $TOTAL_TIME seconds"

exit
