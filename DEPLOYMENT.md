# Deployment Guide

This guide walks you through deploying FieldPal.ai to Azure using Pulumi.

## Prerequisites

1. **Azure Account**: You need an active Azure subscription
2. **Pulumi CLI**: Install from [pulumi.com](https://www.pulumi.com/docs/get-started/install/)
3. **Azure CLI**: Install from [azure.com](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
4. **Python 3.11+**: Required for both the application and Pulumi

## Setup Steps

### 1. Install Dependencies

```bash
# Install application dependencies
pip install -r requirements.txt

# Install Pulumi dependencies
cd pulumi
pip install -r requirements.txt
```

### 2. Configure Azure

```bash
# Login to Azure
az login

# Set your subscription (optional, if you have multiple)
az account set --subscription <subscription-id>

# Verify you're logged in
az account show
```

### 3. Configure Pulumi

```bash
cd pulumi

# Login to Pulumi (or use Pulumi Cloud)
pulumi login

# Create a new stack (or use existing)
pulumi stack init dev

# Configure required settings
pulumi config set auth0_domain your-auth0-domain.auth0.com
pulumi config set auth0_audience your-api-identifier

# Optional: Configure project name and location
pulumi config set project_name fieldpal-ai
pulumi config set location "UK South"
```

### 4. Preview Deployment

```bash
# Preview what will be created
pulumi preview
```

### 5. Deploy

```bash
# Deploy the infrastructure
pulumi up
```

This will create:
- Resource Group
- Storage Account (for images and content)
- App Service Plan
- Web App

### 6. Deploy Application Code

After the infrastructure is created, you need to deploy your application code. You can do this via:

**Option A: Azure CLI**
```bash
# Get the web app name from Pulumi output
pulumi stack output web_app_name

# Deploy using Azure CLI
az webapp up --name <web-app-name> --resource-group <resource-group-name> --runtime "PYTHON:3.11"
```

**Option B: GitHub Actions / Azure DevOps**
Set up CI/CD pipeline to automatically deploy on push.

**Option C: Local Git Deployment**
```bash
# Configure local git deployment
az webapp deployment source config-local-git \
  --name <web-app-name> \
  --resource-group <resource-group-name>

# Add the remote and push
git remote add azure <deployment-url>
git push azure main
```

### 7. Verify Deployment

```bash
# Get the web app URL
pulumi stack output web_app_url

# Visit the URL in your browser
```

## Post-Deployment Configuration

### 1. Set up Auth0

1. Create an Auth0 account at [auth0.com](https://auth0.com)
2. Create a new API in Auth0 Dashboard
3. Note your Domain and API Identifier
4. Update the Pulumi config with these values (they're already set if you followed step 3)

### 2. Configure Storage Container

The storage container is created automatically, but you may want to:
- Set up CORS rules if serving images directly
- Configure public access if needed
- Set up lifecycle management policies

### 3. Set up Custom Domain (Optional)

```bash
# Add custom domain to web app
az webapp config hostname add \
  --webapp-name <web-app-name> \
  --resource-group <resource-group-name> \
  --hostname yourdomain.com
```

## Updating the Deployment

To update your deployment:

```bash
cd pulumi
pulumi up
```

## Destroying Resources

To remove all resources (be careful!):

```bash
cd pulumi
pulumi destroy
```

## Troubleshooting

### Web App Not Starting

1. Check application logs:
```bash
az webapp log tail --name <web-app-name> --resource-group <resource-group-name>
```

2. Check application settings are correct:
```bash
az webapp config appsettings list --name <web-app-name> --resource-group <resource-group-name>
```

### Storage Connection Issues

1. Verify connection string is set correctly in App Settings
2. Check storage account exists and container is created
3. Verify storage account keys are correct

### Auth0 Issues

1. Verify AUTH0_DOMAIN and AUTH0_AUDIENCE are set correctly
2. Check Auth0 API configuration
3. Verify token audience matches API identifier

## Cost Optimization

- Use Basic tier for development (B1)
- Consider using Standard tier for production
- Set up auto-shutdown for development environments
- Use Azure Cost Management to monitor spending

