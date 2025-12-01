# FieldPal.ai

A modern Python web application built with FastAPI, featuring Azure Blob Storage integration, Auth0 authentication, and an admin panel for content management.

## Features

- **FastAPI** - Modern, fast web framework
- **Azure Blob Storage** - For storing images and content
- **Auth0 Authentication** - Secure admin panel access
- **Admin Panel** - Content and image management interface
- **Pulumi** - Infrastructure as Code for Azure deployment

## Project Structure

```
fieldpal.ai/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── auth.py              # Auth0 authentication
│   ├── core/
│   │   ├── __init__.py
│   │   └── templates.py     # Template rendering helper
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── home.py          # Home page route
│   │   ├── about.py         # About page route
│   │   ├── contact.py       # Contact page route
│   │   ├── admin.py         # Admin panel routes
│   │   └── api.py           # API endpoints
│   └── services/
│       ├── __init__.py
│       └── azure_storage.py # Azure Blob Storage service
├── templates/
│   ├── base.html            # Base template
│   ├── home.html            # Home page
│   ├── about.html           # About page
│   ├── contact.html         # Contact page
│   ├── 404.html             # Custom 404 page
│   └── admin/
│       ├── base.html        # Admin base template
│       ├── dashboard.html   # Admin dashboard
│       ├── content.html     # Content management
│       └── images.html      # Image management
├── static/
│   └── css/                 # Static CSS files
├── pulumi/
│   ├── __init__.py
│   ├── main.py              # Pulumi infrastructure code
│   ├── Pulumi.yaml
│   └── Pulumi.dev.yaml      # Development configuration
├── requirements.txt
├── .env.example
└── README.md
```

## Setup

### Prerequisites

- Python 3.11+
- Azure account with subscription
- Auth0 account
- Pulumi CLI installed

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd fieldpal.ai
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Set up Auth0:
   - Create an Auth0 account
   - Create an API in Auth0
   - Get your domain and audience identifier
   - Update `.env` with these values

6. Set up Azure Storage:
   - Create a storage account in Azure
   - Get the connection string
   - Update `.env` with the connection string

## Running Locally

```bash
python -m app.main
# Or
uvicorn app.main:app --reload
```

The application will be available at `http://localhost:8003`

## Deployment with Pulumi

### Prerequisites

1. Install Pulumi CLI:
```bash
curl -fsSL https://get.pulumi.com | sh
```

2. Login to Pulumi:
```bash
pulumi login
```

3. Configure Azure credentials:
```bash
az login
az account set --subscription <subscription-id>
```

### Deploy

1. Navigate to the pulumi directory:
```bash
cd pulumi
```

2. Install Pulumi Azure Native provider:
```bash
pulumi plugin install resource azure-native
```

3. Configure Pulumi:
```bash
pulumi config set auth0_domain <your-auth0-domain>
pulumi config set auth0_audience <your-api-identifier>
```

4. Preview the deployment:
```bash
pulumi preview
```

5. Deploy:
```bash
pulumi up
```

After deployment, Pulumi will output the web app URL.

## Admin Panel

Access the admin panel at `/admin` (requires Auth0 authentication).

The admin panel allows you to:
- Manage website content (home, about, contact pages)
- Upload and manage images
- View dashboard with quick access to all features

## API Endpoints

### Public Endpoints

- `GET /` - Home page
- `GET /about` - About page
- `GET /contact` - Contact page
- `POST /contact/submit` - Submit contact form
- `GET /api/content/{page}` - Get content for a page

### Protected Endpoints (Require Auth0 token)

- `GET /admin` - Admin dashboard
- `GET /admin/content` - Content management
- `GET /admin/images` - Image management
- `PUT /api/content/{page}` - Update page content
- `POST /api/images/upload` - Upload image
- `GET /api/images` - List images
- `DELETE /api/images/{image_name}` - Delete image

## Environment Variables

- `AUTH0_DOMAIN` - Your Auth0 domain
- `AUTH0_AUDIENCE` - Your Auth0 API identifier
- `AZURE_STORAGE_CONNECTION_STRING` - Azure Storage connection string
- `AZURE_STORAGE_CONTAINER` - Container name (default: website-content)

## License

[Your License Here]

