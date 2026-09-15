export PROJECT_ID="assistente-cdc"
export REGION="southamerica-east1"
export REPO="assistente-cdc-repo"
export GH_USER="Pablo-Sant"
export GH_REPO="RAG_CDC"

set -euo pipefail

gcloud config set project $PROJECT_ID

# Ativar APIs
gcloud services enable run.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com \
  iamcredentials.googleapis.com

# Artifact Registry
gcloud artifacts repositories create $REPO \
  --repository-format=docker \
  --location=$REGION

# Secrets (rode um por chave, substituindo o valor)
echo -n "$PINECONE_API_KEY" | gcloud secrets create PINECONE_API_KEY --data-file=-
echo -n "$GROQ_API" | gcloud secrets create GROQ_API_KEY --data-file=-

# Service Account
gcloud iam service-accounts create github-deployer \
  --display-name="GitHub Actions Deployer"

export SA_EMAIL="github-deployer@${PROJECT_ID}.iam.gserviceaccount.com"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" --role="roles/run.admin"
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" --role="roles/artifactregistry.writer"
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" --role="roles/iam.serviceAccountUser"
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${SA_EMAIL}" --role="roles/secretmanager.secretAccessor"

# Workload Identity Federation
gcloud iam workload-identity-pools create "github-pool" \
  --location="global" --display-name="GitHub Pool"

gcloud iam workload-identity-pools providers create-oidc "github-provider" \
  --location="global" \
  --workload-identity-pool="github-pool" \
  --display-name="GitHub Provider" \
  --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository" \
  --issuer-uri="https://token.actions.githubusercontent.com"

gcloud iam service-accounts add-iam-policy-binding "${SA_EMAIL}" \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/$(gcloud projects describe $PROJECT_ID --format='value(projectNumber)')/locations/global/workloadIdentityPools/github-pool/attribute.repository/${GH_USER}/${GH_REPO}"