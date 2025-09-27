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

# Set the region where services are deployed
export REGION="us-central1"

echo "🚀 Deleting Cloud Run services for project '$PROJECT_ID' in region '$REGION'..."

# It's good practice to delete in reverse order of deployment.
# The '|| true' part prevents the script from exiting if a service doesn't exist.

# --- 1. Delete streamlit-ui ---
echo "Deleting streamlit-ui service..."
gcloud run services delete streamlit-ui --region "$REGION" --project "$PROJECT_ID" --quiet || true

# --- 2. Delete api-backend ---
echo "Deleting api-backend service..."
gcloud run services delete api-backend --region "$REGION" --project "$PROJECT_ID" --quiet || true

# --- 3. Delete vector-store ---
echo "Deleting vector-store service..."
gcloud run services delete vector-store --region "$REGION" --project "$PROJECT_ID" --quiet || true

echo "✅ All specified Cloud Run services have been requested for deletion."