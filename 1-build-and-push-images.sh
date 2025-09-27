#!/bin/bash
# Exit on error, treat unset variables as errors, and fail on pipe errors.
set -euo pipefail

# --- Configuration ---
# Get Project ID from gcloud config. Exit with an error if it's not set.
export PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
if [[ -z "$PROJECT_ID" ]]; then
    echo "ERROR: Google Cloud project ID is not set."
    echo "Please set it by running: gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

# Set the region for deployment
export REGION="us-central1"

#Build the vector-store image
echo "🚀 Building and pushing vector-store image..."
gcloud builds submit ./vector-store \
  --tag ${REGION}-docker.pkg.dev/${PROJECT_ID}/p3-search-repo/vector-store:latest \
  --project=$PROJECT_ID --quiet

# Build the api-backend image
echo "🚀 Building and pushing api-backend image..."
gcloud builds submit ./api-backend \
  --tag ${REGION}-docker.pkg.dev/${PROJECT_ID}/p3-search-repo/api-backend:latest \
  --project=$PROJECT_ID --quiet

# Build the streamlit-ui image
echo "🚀 Building and pushing streamlit-ui image..."
gcloud builds submit ./streamlit-ui \
  --tag ${REGION}-docker.pkg.dev/${PROJECT_ID}/p3-search-repo/streamlit-ui:latest \
  --project=$PROJECT_ID --quiet

echo "✅ All images built and pushed successfully!"
