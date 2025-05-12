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
# exec streamlit run main.py
exec streamlit run main.py --server.port=8080 --server.address=0.0.0.0 --server.enableCORS=false --server.enableXsrfProtection=false
