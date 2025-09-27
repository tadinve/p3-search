# Set your project ID and region
export PROJECT_ID=$(gcloud config get-value project)
#!/bin/bash


# Set region
export REGION="us-central1" # Or your preferred region

# Get Project ID from gcloud config. Exit with an error if it's not set.
export PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
if [[ -z "$PROJECT_ID" ]]; then
    echo "ERROR: Google Cloud project ID is not set."
    echo "Please set it by running: gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

echo "🚀 Using Project: $PROJECT_ID in Region: $REGION"

# Enable the necessary APIs for your project
gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  --project=$PROJECT_ID

# Create a repository in Artifact Registry if it doesn't exist
echo "🔎 Checking for Artifact Registry repository 'p3-search-repo'..."
if ! gcloud artifacts repositories describe p3-search-repo --location=$REGION --project=$PROJECT_ID &> /dev/null; then
  echo "🎨 Repository not found. Creating 'p3-search-repo'..."
  gcloud artifacts repositories create p3-search-repo \
    --repository-format=docker \
    --location=$REGION \
    --description="Docker repository for p3-search application" \
    --project=$PROJECT_ID --quiet
else
  echo "✅ Repository 'p3-search-repo' already exists."
fi
