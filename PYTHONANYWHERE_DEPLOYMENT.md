# Deploying AI Builder to PythonAnywhere

This guide will walk you through deploying your Django + MongoDB AI Builder application to PythonAnywhere.

## Prerequisites

1. A PythonAnywhere account (sign up at [pythonanywhere.com](https://www.pythonanywhere.com/))
2. Your MongoDB Atlas connection string (or other MongoDB provider)
3. Your Google API key for AI functionality

## Step 1: Sign Up for PythonAnywhere

1. Go to [pythonanywhere.com](https://www.pythonanywhere.com/) and sign up for a free account
2. After signing up, you'll be taken to your dashboard

## Step 2: Upload Your Project

There are two ways to get your code onto PythonAnywhere:

### Option A: Using Git (Recommended)

1. From your PythonAnywhere dashboard, open a Bash console
2. Clone your repository (if it's on GitHub, GitLab, etc.):
   ```bash
   git clone https://github.com/yourusername/ai-builder.git
   ```

### Option B: Manual Upload

1. Create a ZIP file of your project:
   ```bash
   # On your local machine
   zip -r ai-builder.zip ai-builder
   ```
2. From your PythonAnywhere dashboard, go to the Files tab
3. Upload the ZIP file
4. Open a Bash console and unzip the file:
   ```bash
   unzip ai-builder.zip
   ```

## Step 3: Set Up a Virtual Environment

1. In your Bash console, create a virtual environment:
   ```bash
   cd ai-builder
   python -m venv venv
   source venv/bin/activate
   ```

2. Install your project dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Step 4: Configure Environment Variables

1. Create a `.env` file in your project directory:
   ```bash
   nano .env
   ```

2. Add your environment variables:
   ```
   SECRET_KEY=your-secret-key-here
   DEBUG=False
   GOOGLE_API_KEY=your-google-api-key
   MONGO_URI=your-mongodb-atlas-uri
   ```

3. Save and exit (Ctrl+X, then Y, then Enter)

## Step 5: Configure the Web App

1. Go to the Web tab on your PythonAnywhere dashboard
2. Click "Add a new web app"
3. Choose "Manual configuration"
4. Select Python version (3.9)
5. Enter the path to your project directory (e.g., `/home/yourusername/ai-builder`)

## Step 6: Configure WSGI File

1. Click on the WSGI configuration file link in the Web tab
2. Replace the contents with:

```python
import os
import sys

# Add your project directory to the system path
path = '/home/yourusername/ai-builder'
if path not in sys.path:
    sys.path.append(path)

# Set environment variables
os.environ['DJANGO_SETTINGS_MODULE'] = 'ai_builder.settings'

# Import Django and start the WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

3. Replace `yourusername` with your actual PythonAnywhere username
4. Save the file

## Step 7: Configure Static Files

1. In the Web tab, scroll down to "Static files"
2. Add the following mappings:
   - URL: `/static/` → Directory: `/home/yourusername/ai-builder/static`
   - URL: `/media/` → Directory: `/home/yourusername/ai-builder/media`

3. Run the collectstatic command in your Bash console:
   ```bash
   cd ai-builder
   source venv/bin/activate
   python manage.py collectstatic --noinput
   ```

## Step 8: Reload Your Web App

1. Go back to the Web tab
2. Click the "Reload" button for your web app

## Step 9: Check Your Website

Your website should now be live at:
```
https://yourusername.pythonanywhere.com
```

## Troubleshooting

### Error Logs
If your application isn't working correctly, check the error logs:
1. Go to the Web tab
2. Click on the "Error log" link

### Common Issues

1. **Static Files Not Loading**
   - Make sure you've run `collectstatic`
   - Check the static files mappings in the Web tab

2. **Database Connection Issues**
   - Ensure your MongoDB Atlas IP whitelist includes PythonAnywhere's IPs
   - Check your connection string in the `.env` file

3. **WSGI Configuration**
   - Make sure the paths in your WSGI file are correct
   - Ensure the DJANGO_SETTINGS_MODULE is set correctly

4. **Import Errors**
   - Check that all dependencies are installed in your virtual environment
   - Make sure your project structure is correct

## Updating Your Application

To update your application after making changes:

1. If using Git, pull the latest changes:
   ```bash
   cd ai-builder
   git pull
   ```

2. If manually uploading, upload the new files and replace the old ones

3. Install any new dependencies:
   ```bash
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. Run migrations if needed:
   ```bash
   python manage.py migrate
   ```

5. Collect static files if needed:
   ```bash
   python manage.py collectstatic --noinput
   ```

6. Reload your web app from the Web tab

## Additional Resources

- [PythonAnywhere Help Pages](https://help.pythonanywhere.com/)
- [Django on PythonAnywhere](https://help.pythonanywhere.com/pages/Django/)
- [Using MongoDB on PythonAnywhere](https://help.pythonanywhere.com/pages/MongoDB/)
