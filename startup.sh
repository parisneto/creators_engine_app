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
export OPENAI_API_KEY="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"



# exec streamlit run main.py
exec streamlit run main.py --server.port=8080 --server.address=0.0.0.0 --server.enableCORS=false --server.enableXsrfProtection=false
