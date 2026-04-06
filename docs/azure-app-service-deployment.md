# Azure App Service Deployment Guide

This guide explains how to deploy the Foundry IQ Comparison Demo to Azure App Service.

## Prerequisites

- Azure subscription
- Azure CLI installed (`az --version`)
- Azure resources configured (Foundry Agent Service, AI Search, etc.)
- Local testing completed successfully

## Architecture

```
Azure App Service (Backend)    Azure App Service (Frontend)
      ↓                               ↓
FastAPI (Python 3.11)          Next.js (Node.js 18)
      ↓                               ↓
Foundry Agent Service  ←─────────────┘
      ↓
Azure AI Search + Foundry IQ
```

## Deployment Options

### Option 1: Azure CLI Quick Deploy (Recommended for Testing)

#### Backend Deployment

1. Navigate to backend directory:
```bash
cd backend
```

2. Create `startup.txt` for App Service:
```bash
echo "gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app" > startup.txt
```

3. Add `gunicorn` to requirements.txt:
```bash
echo "gunicorn==21.2.0" >> requirements.txt
```

4. Deploy to App Service:
```bash
az webapp up \
  --runtime PYTHON:3.11 \
  --sku B1 \
  --name foundry-iq-backend-demo \
  --resource-group foundry-iq-demo-rg \
  --location japaneast
```

5. Configure environment variables:
```bash
az webapp config appsettings set \
  --name foundry-iq-backend-demo \
  --resource-group foundry-iq-demo-rg \
  --settings \
    FOUNDRY_AGENT_ENDPOINT="your-endpoint" \
    FOUNDRY_AGENT_API_KEY="your-key" \
    CLASSIC_RAG_AGENT_NAME="classic-rag-agent" \
    FOUNDRY_IQ_AGENT_NAME="foundry-iq-agent" \
    MOCK_MODE="false" \
    BACKEND_HOST="0.0.0.0" \
    BACKEND_PORT="8000"
```

6. Enable logging:
```bash
az webapp log config \
  --name foundry-iq-backend-demo \
  --resource-group foundry-iq-demo-rg \
  --application-logging filesystem \
  --level information
```

#### Frontend Deployment

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Build the frontend:
```bash
npm run build
```

3. Create production `package.json` script (if not exists):
Ensure `package.json` has:
```json
{
  "scripts": {
    "start": "next start"
  }
}
```

4. Deploy to App Service:
```bash
az webapp up \
  --runtime NODE:18-lts \
  --sku B1 \
  --name foundry-iq-frontend-demo \
  --resource-group foundry-iq-demo-rg \
  --location japaneast
```

5. Configure environment variables:
```bash
az webapp config appsettings set \
  --name foundry-iq-frontend-demo \
  --resource-group foundry-iq-demo-rg \
  --settings \
    NEXT_PUBLIC_BACKEND_URL="https://foundry-iq-backend-demo.azurewebsites.net"
```

### Option 2: Azure Portal Deployment

#### Backend (Python)

1. Go to Azure Portal → Create App Service
2. Configuration:
   - **Runtime**: Python 3.11
   - **OS**: Linux
   - **Region**: Japan East (or your preferred region)
   - **SKU**: B1 or higher

3. Deploy code:
   - Use GitHub Actions, Azure DevOps, or Local Git
   - Set startup command: `gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app`

4. Configure Application Settings (Environment Variables):
   - `FOUNDRY_AGENT_ENDPOINT`
   - `FOUNDRY_AGENT_API_KEY`
   - `CLASSIC_RAG_AGENT_NAME`
   - `FOUNDRY_IQ_AGENT_NAME`
   - `MOCK_MODE=false`

#### Frontend (Node.js)

1. Go to Azure Portal → Create App Service
2. Configuration:
   - **Runtime**: Node 18 LTS
   - **OS**: Linux
   - **Region**: Japan East (or same as backend)
   - **SKU**: B1 or higher

3. Deploy code:
   - Build locally: `npm run build`
   - Deploy using GitHub Actions, Azure DevOps, or Local Git
   - Startup command: `npm start`

4. Configure Application Settings:
   - `NEXT_PUBLIC_BACKEND_URL=https://your-backend-name.azurewebsites.net`

### Option 3: GitHub Actions CI/CD

#### Setup

1. Create `.github/workflows/deploy-backend.yml`:
```yaml
name: Deploy Backend to Azure App Service

on:
  push:
    branches: [ main ]
    paths: [ 'backend/**' ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt

      - name: Deploy to Azure Web App
        uses: azure/webapps-deploy@v2
        with:
          app-name: foundry-iq-backend-demo
          publish-profile: ${{ secrets.AZURE_WEBAPP_PUBLISH_PROFILE_BACKEND }}
          package: ./backend
```

2. Create `.github/workflows/deploy-frontend.yml`:
```yaml
name: Deploy Frontend to Azure App Service

on:
  push:
    branches: [ main ]
    paths: [ 'frontend/**' ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install and build
        run: |
          cd frontend
          npm ci
          npm run build

      - name: Deploy to Azure Web App
        uses: azure/webapps-deploy@v2
        with:
          app-name: foundry-iq-frontend-demo
          publish-profile: ${{ secrets.AZURE_WEBAPP_PUBLISH_PROFILE_FRONTEND }}
          package: ./frontend
```

3. Get publish profiles and add to GitHub Secrets:
```bash
# Backend
az webapp deployment list-publishing-profiles \
  --name foundry-iq-backend-demo \
  --resource-group foundry-iq-demo-rg \
  --xml

# Frontend
az webapp deployment list-publishing-profiles \
  --name foundry-iq-frontend-demo \
  --resource-group foundry-iq-demo-rg \
  --xml
```

Add these as `AZURE_WEBAPP_PUBLISH_PROFILE_BACKEND` and `AZURE_WEBAPP_PUBLISH_PROFILE_FRONTEND` in GitHub Secrets.

## Post-Deployment Configuration

### Enable CORS (Backend)

```bash
az webapp cors add \
  --name foundry-iq-backend-demo \
  --resource-group foundry-iq-demo-rg \
  --allowed-origins "https://foundry-iq-frontend-demo.azurewebsites.net"
```

### Configure Logging

```bash
# Backend
az webapp log tail \
  --name foundry-iq-backend-demo \
  --resource-group foundry-iq-demo-rg

# Frontend
az webapp log tail \
  --name foundry-iq-frontend-demo \
  --resource-group foundry-iq-demo-rg
```

### Configure Custom Domain (Optional)

```bash
# Map custom domain
az webapp config hostname add \
  --webapp-name foundry-iq-frontend-demo \
  --resource-group foundry-iq-demo-rg \
  --hostname demo.yourdomain.com

# Enable HTTPS
az webapp config ssl bind \
  --name foundry-iq-frontend-demo \
  --resource-group foundry-iq-demo-rg \
  --certificate-thumbprint <thumbprint> \
  --ssl-type SNI
```

## Performance Optimization

### Backend Optimizations

1. **Enable Always On** (prevents cold starts):
```bash
az webapp config set \
  --name foundry-iq-backend-demo \
  --resource-group foundry-iq-demo-rg \
  --always-on true
```

2. **Scale up if needed**:
```bash
az appservice plan update \
  --name your-app-service-plan \
  --resource-group foundry-iq-demo-rg \
  --sku P1V2
```

3. **Worker count** (adjust in startup command):
```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
# Adjust -w based on app service plan cores
```

### Frontend Optimizations

1. **Enable compression**:
```bash
az webapp config set \
  --name foundry-iq-frontend-demo \
  --resource-group foundry-iq-demo-rg \
  --http20-enabled true
```

2. **CDN integration** (optional):
- Set up Azure CDN
- Configure CDN endpoint for static assets

## Monitoring and Diagnostics

### Application Insights

1. Create Application Insights:
```bash
az monitor app-insights component create \
  --app foundry-iq-insights \
  --location japaneast \
  --resource-group foundry-iq-demo-rg
```

2. Connect to App Service:
```bash
az webapp config appsettings set \
  --name foundry-iq-backend-demo \
  --resource-group foundry-iq-demo-rg \
  --settings \
    APPLICATIONINSIGHTS_CONNECTION_STRING="your-connection-string"
```

### Key Metrics to Monitor

- Response time (p50, p95, p99)
- Request rate
- Error rate
- Token usage (custom metric)
- Agent execution time

## Security Considerations

### Network Security

1. **Restrict access to backend** (optional):
```bash
az webapp config access-restriction add \
  --name foundry-iq-backend-demo \
  --resource-group foundry-iq-demo-rg \
  --priority 100 \
  --rule-name "Allow-Frontend" \
  --action Allow \
  --ip-address "frontend-outbound-ip/32"
```

### Secrets Management

**Use Azure Key Vault** for sensitive credentials:

1. Create Key Vault:
```bash
az keyvault create \
  --name foundry-iq-keyvault \
  --resource-group foundry-iq-demo-rg \
  --location japaneast
```

2. Store secrets:
```bash
az keyvault secret set \
  --vault-name foundry-iq-keyvault \
  --name FoundryAgentApiKey \
  --value "your-api-key"
```

3. Enable Managed Identity:
```bash
az webapp identity assign \
  --name foundry-iq-backend-demo \
  --resource-group foundry-iq-demo-rg
```

4. Grant access:
```bash
az keyvault set-policy \
  --name foundry-iq-keyvault \
  --object-id <managed-identity-object-id> \
  --secret-permissions get list
```

5. Reference in App Settings:
```bash
az webapp config appsettings set \
  --name foundry-iq-backend-demo \
  --resource-group foundry-iq-demo-rg \
  --settings \
    FOUNDRY_AGENT_API_KEY="@Microsoft.KeyVault(SecretUri=https://foundry-iq-keyvault.vault.azure.net/secrets/FoundryAgentApiKey/)"
```

## Cost Estimation

**Basic Setup (B1 tier):**
- Backend App Service: ~$13/month
- Frontend App Service: ~$13/month
- Application Insights: ~$2-10/month (depending on usage)
- **Total: ~$28-36/month**

**Production Setup (P1V2 tier):**
- Backend App Service: ~$70/month
- Frontend App Service: ~$70/month
- Application Insights: ~$10-50/month
- **Total: ~$150-190/month**

Plus Azure AI Search and Foundry Agent Service costs (varies by usage).

## Troubleshooting

### Backend won't start
- Check logs: `az webapp log tail`
- Verify startup command
- Ensure all dependencies in `requirements.txt`
- Check environment variables are set

### Frontend won't start
- Verify `npm start` works locally after `npm run build`
- Check `NEXT_PUBLIC_BACKEND_URL` is set correctly
- Ensure backend URL is accessible from frontend

### CORS errors
- Add frontend URL to backend CORS settings
- Verify CORS middleware in backend code

### High latency
- Check App Service plan tier
- Enable Always On
- Consider scaling up or out
- Review Application Insights for bottlenecks

## Cleanup

To delete all resources:
```bash
az group delete \
  --name foundry-iq-demo-rg \
  --yes \
  --no-wait
```

## Next Steps

- Set up monitoring and alerts
- Configure auto-scaling
- Implement caching (Redis)
- Set up staging environment
- Configure CI/CD pipelines

## References

- [Azure App Service Documentation](https://docs.microsoft.com/azure/app-service/)
- [Deploy Python to Azure](https://docs.microsoft.com/azure/app-service/quickstart-python)
- [Deploy Node.js to Azure](https://docs.microsoft.com/azure/app-service/quickstart-nodejs)
