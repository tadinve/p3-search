#!/bin/bash
# Exit on error, treat unset variables as errors, and fail on pipe errors.
# This line is crucial to prevent race conditions during deployment.
export PROJECT_ID=$(gcloud config get-value project)
export REGION="us-central1" # Or your preferred region
./3-delete-cloud-run-services.sh

set -euox pipefail

gcloud config set project p3-search
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

echo "🚀 Starting deployment to Cloud Run for project '$PROJECT_ID' in region '$REGION'..."

# --- 1. Deploy vector-store ---
echo "Deploying vector-store service..."
gcloud run deploy vector-store \
  --image "${REGION}-docker.pkg.dev/${PROJECT_ID}/p3-search-repo/vector-store:latest" \
  --memory 2Gi \
  --cpu 2 \
  --port 8001 \
  --allow-unauthenticated \
  --region "$REGION" \
  --project "$PROJECT_ID" \
  --quiet

# --- 2. Deploy api-backend ---
echo "Deploying api-backend service..."
VECTOR_STORE_URL=$(gcloud run services describe vector-store --platform managed --region "$REGION" --project "$PROJECT_ID" --format 'value(status.url)')
gcloud run deploy api-backend \
  --image "${REGION}-docker.pkg.dev/${PROJECT_ID}/p3-search-repo/api-backend:latest" \
  --memory 1Gi \
  --cpu 1 \
  --port 8000 \
  --set-env-vars="VECTOR_STORE_URL=$VECTOR_STORE_URL" \
  --allow-unauthenticated \
  --region "$REGION" \
  --project "$PROJECT_ID" \
  --quiet

# --- 3. Deploy streamlit-ui ---
echo "Deploying streamlit-ui service..."
API_BASE_URL=$(gcloud run services describe api-backend --platform managed --region "$REGION" --project "$PROJECT_ID" --format 'value(status.url)')
UI_URL=$(gcloud run deploy streamlit-ui \
  --image "${REGION}-docker.pkg.dev/${PROJECT_ID}/p3-search-repo/streamlit-ui:latest" \
  --memory 1Gi \
  --cpu 1 \
  --port 8501 \
  --set-env-vars="API_BASE_URL=$API_BASE_URL" \
  --allow-unauthenticated \
  --region "$REGION" \
  --project "$PROJECT_ID" \
  --quiet \
  --format 'value(status.url)')



gcloud run services list --platform managed --format="table(
    name:label=SERVICE,
    region:label=REGION,
    status.url:label=URL,
    spec.template.spec.containers[0].ports[0].containerPort:label='CONTAINER PORT'
)"


echo "✅ Deployment successful!"
echo "➡️ Your application is available at: $UI_URL"