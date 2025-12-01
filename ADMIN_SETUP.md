# Admin Panel Setup Guide

## How to Access the Admin Panel

1. **Navigate to the admin panel URL:**
   ```
   http://localhost:8003/admin
   ```

2. **You will be redirected to Auth0 login** (if not already authenticated)

3. **After logging in**, you'll be redirected back to the admin dashboard

## Auth0 Configuration

To use the admin panel, you need to configure Auth0:

### 1. Create an Auth0 Account
- Go to [auth0.com](https://auth0.com) and create a free account

### 2. Create an Application
1. In Auth0 Dashboard, go to **Applications** → **Applications**
2. Click **Create Application**
3. Choose **Regular Web Application**
4. Note your:
   - **Domain** (e.g., `your-tenant.auth0.com`)
   - **Client ID**
   - **Client Secret**

### 3. Create an API
1. Go to **Applications** → **APIs**
2. Click **Create API**
3. Set:
   - **Name**: FieldPal Admin API (or any name)
   - **Identifier**: `https://fieldpal.ai/api` (or any unique identifier)
   - **Signing Algorithm**: RS256
4. Note the **Identifier** (this is your `AUTH0_AUDIENCE`)

### 4. Configure Application Settings
1. Go back to your Application
2. Under **Application URIs**, set:
   - **Allowed Callback URLs**: `http://localhost:8003/auth/callback`
   - **Allowed Logout URLs**: `http://localhost:8003`
   - **Allowed Web Origins**: `http://localhost:8003`

### 5. Update Your .env File

Create a `.env` file in the project root with:

```env
# Auth0 Configuration
AUTH0_DOMAIN=your-tenant.auth0.com
AUTH0_CLIENT_ID=your-client-id
AUTH0_CLIENT_SECRET=your-client-secret
AUTH0_AUDIENCE=https://fieldpal.ai/api
AUTH0_CALLBACK_URL=http://localhost:8003/auth/callback

# Azure Storage (optional for local dev)
AZURE_STORAGE_CONNECTION_STRING=
AZURE_STORAGE_CONTAINER=website-content
```

## Admin Panel Features

Once logged in, you can access:

- **Dashboard** (`/admin`) - Overview and quick links
- **Content Management** (`/admin/content`) - Edit website content
- **Image Management** (`/admin/images`) - Upload and manage images

## Logout

To logout, visit:
```
http://localhost:8003/auth/logout
```

## Troubleshooting

### "Auth0 is not configured" error
- Make sure your `.env` file exists and has all Auth0 variables set
- Restart the application after updating `.env`

### "Invalid authentication credentials" error
- Check that your Auth0 Client ID and Secret are correct
- Verify the callback URL matches exactly in Auth0 settings
- Make sure the API identifier matches your `AUTH0_AUDIENCE`

### Redirect loop
- Check that your callback URL is whitelisted in Auth0
- Verify `AUTH0_CALLBACK_URL` in `.env` matches Auth0 settings

