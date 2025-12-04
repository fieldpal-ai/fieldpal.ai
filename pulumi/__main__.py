import pulumi
import pulumi_azure_native as azure_native
from pulumi import Config

# Get configuration
config = Config()
project_name = config.get("project_name") or "fieldpal-ai"
location = config.get("location") or "West Europe"
resource_group_name = config.get("resource_group_name") or f"{project_name}-rg"
web_app_name = config.get("web_app_name") or "fieldpal-ai-website"

# Create resource group
resource_group = azure_native.resources.ResourceGroup(
    resource_group_name,
    resource_group_name=resource_group_name,
    location=location
)

# Create storage account for website content and images
# Azure storage account names must be lowercase, 3-24 chars, alphanumeric only
storage_account_name = f"{project_name.replace('-', '')}stor"[:24].lower()
storage_account = azure_native.storage.StorageAccount(
    f"{project_name}storage",
    account_name=storage_account_name,
    resource_group_name=resource_group.name,
    location=resource_group.location,
    kind=azure_native.storage.Kind.STORAGE_V2,
    sku=azure_native.storage.SkuArgs(
        name=azure_native.storage.SkuName.STANDARD_LRS
    ),
    access_tier=azure_native.storage.AccessTier.HOT
)

# Create blob container for website content
blob_container = azure_native.storage.BlobContainer(
    f"{project_name}-container",
    account_name=storage_account.name,
    container_name="website-content",
    resource_group_name=resource_group.name,
    public_access=azure_native.storage.PublicAccess.NONE
)

# Get storage account keys
storage_account_keys = azure_native.storage.list_storage_account_keys_output(
    account_name=storage_account.name,
    resource_group_name=resource_group.name
)

# Create App Service Plan
app_service_plan = azure_native.web.AppServicePlan(
    f"{project_name}-plan",
    resource_group_name=resource_group.name,
    location=resource_group.location,
    kind="Linux",
    reserved=True,  # Required for Linux
    sku=azure_native.web.SkuDescriptionArgs(
        name="B1",  # Basic tier
        tier="Basic",
        capacity=1
    )
)

# Create Web App
# Azure App Service names must be globally unique, lowercase, and use hyphens
# Normalize the name: lowercase, replace spaces with hyphens
normalized_web_app_name = web_app_name.replace(" ", "-").lower()
web_app = azure_native.web.WebApp(
    f"{project_name}-app",  # Pulumi resource identifier
    resource_group_name=resource_group.name,
    location=resource_group.location,
    server_farm_id=app_service_plan.id,
    name=normalized_web_app_name,  # Actual Azure App Service name
    site_config=azure_native.web.SiteConfigArgs(
        linux_fx_version="PYTHON|3.11",
        app_settings=[
            azure_native.web.NameValuePairArgs(
                name="AZURE_STORAGE_CONNECTION_STRING",
                value=pulumi.Output.all(
                    storage_account.name,
                    storage_account_keys.keys[0].value
                ).apply(lambda args: f"DefaultEndpointsProtocol=https;AccountName={args[0]};AccountKey={args[1]};EndpointSuffix=core.windows.net")
            ),
            azure_native.web.NameValuePairArgs(
                name="AZURE_STORAGE_CONTAINER",
                value="website-content"
            ),
            azure_native.web.NameValuePairArgs(
                name="AUTH0_DOMAIN",
                value=config.require("auth0_domain")
            ),
            azure_native.web.NameValuePairArgs(
                name="AUTH0_AUDIENCE",
                value=config.require("auth0_audience")
            ),
            azure_native.web.NameValuePairArgs(
                name="AUTH0_CLIENT_ID",
                value=config.get("auth0_client_id", "")
            ),
            azure_native.web.NameValuePairArgs(
                name="AUTH0_CLIENT_SECRET",
                value=config.get("auth0_client_secret", "")
            ),
            azure_native.web.NameValuePairArgs(
                name="AUTH0_CALLBACK_URL",
                value=config.get("auth0_callback_url", "")
            ),
            azure_native.web.NameValuePairArgs(
                name="POSTHOG_PROJECT_API_KEY",
                value=config.get("posthog_project_api_key", "")
            ),
            azure_native.web.NameValuePairArgs(
                name="POSTHOG_HOST",
                value=config.get("posthog_host", "https://us.i.posthog.com")
            ),
            azure_native.web.NameValuePairArgs(
                name="SENDGRID_API_KEY",
                value=config.get_secret("sendgrid_api_key") or ""
            ),
            azure_native.web.NameValuePairArgs(
                name="SENDGRID_FROM_EMAIL",
                value=config.get("sendgrid_from_email", "no-reply@fieldpal.ai")
            ),
            azure_native.web.NameValuePairArgs(
                name="WEBSITES_ENABLE_APP_SERVICE_STORAGE",
                value="false"
            ),
            azure_native.web.NameValuePairArgs(
                name="SCM_DO_BUILD_DURING_DEPLOYMENT",
                value="true"
            ),
            azure_native.web.NameValuePairArgs(
                name="WEBSITES_PORT",
                value="8000"
            )
        ],
        app_command_line="python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2"
    ),
    https_only=True
)

# Export outputs
pulumi.export("resource_group_name", resource_group.name)
pulumi.export("storage_account_name", storage_account.name)
pulumi.export("web_app_name", web_app.name)
pulumi.export("web_app_url", web_app.default_host_name.apply(lambda host: f"https://{host}"))

# Export Auth0 configuration (for local development)
pulumi.export("auth0_domain", config.get("auth0_domain", ""))
pulumi.export("auth0_audience", config.get("auth0_audience", ""))
pulumi.export("auth0_client_id", config.get("auth0_client_id", ""))
pulumi.export("auth0_callback_url", config.get("auth0_callback_url", ""))

# Export PostHog configuration (for local development)
pulumi.export("posthog_project_api_key", config.get("posthog_project_api_key", ""))
pulumi.export("posthog_host", config.get("posthog_host", "https://us.i.posthog.com"))

