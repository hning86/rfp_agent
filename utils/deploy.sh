#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Determine the directory containing the script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Load environment variables from rfp_agent/.env if it exists
ENV_FILE="$PROJECT_ROOT/rfp_agent/.env"
if [ -f "$ENV_FILE" ]; then
    echo "Loading environment variables from $ENV_FILE..."
    export $(grep -v '^#' "$ENV_FILE" | xargs)
fi

# Fallback defaults if not set in .env
PROJECT="${GOOGLE_CLOUD_PROJECT:-ninghai-ccai}"
REGION="${GOOGLE_CLOUD_LOCATION:-us-central1}"
AGENT_ENGINE_ID="2853791775741444096"
#AGENT_ENGINE_ID="3375681566935089152"

echo "Deploying rfp_agent to Vertex AI Agent Engine..."
echo "Project: $PROJECT"
echo "Region: $REGION"
echo "Agent Engine ID (Update): $AGENT_ENGINE_ID"

# Verify gcloud auth application-default is valid
if ! gcloud auth application-default print-access-token &>/dev/null; then
    echo "Error: Google Cloud application-default credentials are not configured or expired."
    echo "Please run 'gcloud auth application-default login' first."
    exit 1
fi

# Run the deployment command via uv
uv run adk deploy agent_engine \
    --project="$PROJECT" \
    --region="$REGION" \
    --adk_app_object="app" \
    --agent_engine_id="$AGENT_ENGINE_ID" \
    "$PROJECT_ROOT/rfp_agent"

echo "Deployment successfully completed!"
