set -euo pipefail


# Definição de variáveis
RESOURCE_GROUP="assistente-cdc-rg"
LOCATION="brazilsouth"
ENV_NAME="assistente-cdc-env"
ACR_NAME="assistentecdcregistry"     # precisa ser único globalmente, sem hífen
BACKEND_APP="assistente-cdc-api"
FRONTEND_APP="assistente-cdc-front"
BACKEND_DIR="./api"
FRONTEND_DIR="./frontend"

# Definir chaves antes de rodar
: "${GROQ_KEY:?Definir chave de api da Groq antes de rodar (export GROQ_KEY=...)}"
: "${PINECONE_KEY:?Definir chave de api do pinecone antes de rodar (export PINECONE_KEY=...)}"

echo "Verificando login na Azure"
az account show > /dev/null ||

# Criando grupos de recursos
echo "==> Criando grupo de recursos: $RESOURCE_GROUP"
az group create \
  --name "$RESOURCE_GROUP" \
  --location "$LOCATION" \
  --output none

# Criando ACR
echo "Criando Azure Container Registry: $ACR_NAME"
az acr create \
  --resource-group "$RESOURCE_GROUP" \
  --name "$ACR_NAME" \
  --sku Basic \
  --output none


echo "Habilitando admin user do ACR"
az acr update --name "$ACR_NAME" --admin-enabled true --output none

ACR_USERNAME=$(az acr credential show --name "$ACR_NAME" --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --name "$ACR_NAME" --query passwords[0].value -o tsv)


echo "Autenticando no ACR"
az acr login --name "$ACR_NAME"

# Criando ambiente do container apps
echo "==> Criando ambiente do Container Apps: $ENV_NAME"
az containerapp env create \
  --name "$ENV_NAME" \
  --resource-group "$RESOURCE_GROUP" \
  --location "$LOCATION" \
  --output none


# Build do backend mais deploy
echo "Buildando imagem do backend localmente"
docker build -t "$ACR_NAME.azurecr.io/backend:latest" "$BACKEND_DIR"

echo "Enviando imagem do backend pro ACR"
docker push "$ACR_NAME.azurecr.io/backend:latest"

echo "Fazendo deploy do backend no Container Apps"
az containerapp create \
  --name "$BACKEND_APP" \
  --resource-group "$RESOURCE_GROUP" \
  --environment "$ENV_NAME" \
  --image "$ACR_NAME.azurecr.io/backend:latest" \
  --registry-server "$ACR_NAME.azurecr.io" \
  --registry-username "$ACR_USERNAME" \
  --registry-password "$ACR_PASSWORD" \
  --target-port 8080 \
  --ingress external \
  --secrets \
    groq-key="$GROQ_KEY" \
    pinecone-key="$PINECONE_KEY" \
  --env-vars \
    GROQ_API_KEY=secretref:groq-key \
    PINECONE_API_KEY=secretref:pinecone-key \
  --output none

BACKEND_URL=$(az containerapp show \
  --name "$BACKEND_APP" \
  --resource-group "$RESOURCE_GROUP" \
  --query properties.configuration.ingress.fqdn \
  --output tsv)

echo "Backend disponível em: https://$BACKEND_URL"


# Build do frontend mais deploy
echo "Buildando imagem do frontend localmente (apontando para a api do backend)"
docker build \
  --build-arg VITE_API_BASE_URL="https://$BACKEND_URL/api" \ 
  -t "$ACR_NAME.azurecr.io/frontend:latest" \
  "$FRONTEND_DIR"

echo "Enviando imagem do frontend pro ACR"
docker push "$ACR_NAME.azurecr.io/frontend:latest"

echo "Fazendo deploy do frontend no Container Apps"
az containerapp create \
  --name "$FRONTEND_APP" \
  --resource-group "$RESOURCE_GROUP" \
  --environment "$ENV_NAME" \
  --image "$ACR_NAME.azurecr.io/frontend:latest" \
  --registry-server "$ACR_NAME.azurecr.io" \
  --registry-username "$ACR_USERNAME" \
  --registry-password "$ACR_PASSWORD" \
  --target-port 80 \
  --ingress external \
  --output none

FRONTEND_URL=$(az containerapp show \
  --name "$FRONTEND_APP" \
  --resource-group "$RESOURCE_GROUP" \
  --query properties.configuration.ingress.fqdn \
  --output tsv)
 