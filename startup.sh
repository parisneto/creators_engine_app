#!/bin/sh
# startup.sh

# Exit immediately if a command exits with a non-zero status.
set -e

# Run the data retriever script first
# Assumes WORKDIR is /app in the Dockerfile
echo "--- Running data retriever script ---"
python /app/utils/dataretriever.py
echo "--- Data retriever script finished ---"

# Now, execute the main application (Streamlit)
# Use "exec" to replace the shell process with the streamlit process.
# This ensures signals (like SIGTERM from Cloud Run) are passed correctly.
echo "--- Starting Streamlit ---"
# CMD ["/opt/python/bin/streamlit", "run", "main.py", "--server.port=8080", "--server.address=0.0.0.0", "--server.enableCORS=false", "--server.enableXsrfProtection=false"]

# temporary test
#export OPENAI_API_KEY="sk-proj-vkPn5AOFHOCd  EXAMPLE ADD TO ENV or Dockerfile etc..
# Secret created :
# projects/948268285269/secrets/creators-engine-openai-apikey
# Secrete Reference :
# projects/fleet-gamma-448616-m1/secrets/creators-engine-openai-apikey/versions/latest
# gcloud run deploy YOUR_SERVICE_NAME \
#   --image YOUR_IMAGE \
#   --platform managed \
#   --region YOUR_REGION \
#   --set-secrets OPENAI_API_KEY=projects/fleet-gamma-448616-m1/secrets/creators-engine-openai-apikey/versions/latest


# exec streamlit run main.py
exec streamlit run main.py --server.port=8080 --server.address=0.0.0.0 --server.enableCORS=false --server.enableXsrfProtection=false
