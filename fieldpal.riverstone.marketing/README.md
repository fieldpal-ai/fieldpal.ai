# Fieldpal Website - Local Development

This directory contains a static export of the Fieldpal website that can be run locally.

## Quick Start

### Option 1: Using the Python Server Script (Recommended)

1. Navigate to the demo directory:
   ```bash
   cd fieldpal.riverstone.marketing/demo
   ```

2. Run the server:
   ```bash
   python3 serve.py
   ```

3. Open your browser to: http://localhost:8000

### Option 2: Using Python's Built-in HTTP Server

1. Navigate to the demo directory:
   ```bash
   cd fieldpal.riverstone.marketing/demo
   ```

2. Start the server:
   ```bash
   python3 -m http.server 8000
   ```

3. Open your browser to: http://localhost:8000

### Option 3: Using Node.js (if you have it installed)

1. Install http-server globally (if not already installed):
   ```bash
   npm install -g http-server
   ```

2. Navigate to the demo directory:
   ```bash
   cd fieldpal.riverstone.marketing/demo
   ```

3. Start the server:
   ```bash
   http-server -p 8000
   ```

## Directory Structure

- `index.html` - Main HTML file
- `wp-content/` - Contains CSS, JavaScript, and uploaded media files
- `wp-includes/` - Contains jQuery and other dependencies

## Notes

- The site is a static export from WordPress
- Some absolute URLs in the HTML may point to the production domain (`fieldpal.riverstone.marketing`)
- For full functionality, you may need to update URLs in the HTML if you encounter broken links or missing resources

## Troubleshooting

If you see broken links or missing resources:
1. Check the browser console for 404 errors
2. The HTML may contain absolute URLs that need to be updated for local development
3. External resources (like Google Fonts) should load automatically



