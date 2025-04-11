# Growthzi - AI Website Builder

Growthzi is a powerful AI-powered website builder that creates professional, custom websites in minutes. Using advanced AI technology, it generates complete websites based on your business description, eliminating the need for coding or design expertise.

## Features

- 🚀 Lightning Fast Creation - Generate complete websites in minutes
- 🎨 Beautiful, Modern Design - Professional layouts and responsive designs
- 💡 Smart Content Generation - AI-powered content creation
- 🔒 Secure Authentication - User registration and login system
- 📱 Responsive Design - Works perfectly on all devices

## Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.13 or higher
- pip (Python package installer)
- Git (optional, for cloning the repository)

## Installation Steps

1. **Clone the Repository** (if using Git):
   ```bash
   git clone https://github.com/ayshillu/ai_website_builder.git
   cd ai-builder
   ```

2. **Create a Virtual Environment**:
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Required Packages**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables**:
   Create a `.env` file in the project root with the following variables:
   ```
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   GOOGLE_API_KEY=your-google-ai-api-key
   ```

5. **Initialize the Database**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create a Superuser** (optional):
   ```bash
   python manage.py createsuperuser
   ```

## Running the Application

1. **Start the Development Server**:
   ```bash
   python manage.py runserver
   ```

2. **Access the Application**:
   Open your web browser and navigate to:
   ```
   http://localhost:8000
   ```

## Project Structure

```
ai-builder/
├── ai_builder/          # Project settings
├── main/               # Main application
│   ├── migrations/     # Database migrations
│   ├── static/         # Static files (CSS, JS, images)
│   ├── templates/      # HTML templates
│   ├── models.py       # Database models
│   ├── views.py        # View functions
│   └── urls.py         # URL configurations
├── manage.py           # Django management script
├── requirements.txt    # Python dependencies
└── .env               # Environment variables
```

## Key Features Implementation

### AI Website Generation
- Uses Google's Generative AI to create website content
- Customizable business information input
- Responsive and modern design templates

### User Authentication
- Secure user registration and login
- JWT-based authentication for API endpoints
- Session management for web interface

### Website Management
- Create, view, update, and delete generated websites
- Custom domain support
- Responsive design across all devices

## Troubleshooting

1. **Database Issues**:
   - Ensure all migrations are applied: `python manage.py migrate`
   - Check database settings in `settings.py`

2. **Static Files Not Loading**:
   - Run `python manage.py collectstatic`
   - Check `STATIC_ROOT` and `STATIC_URL` settings

3. **API Key Issues**:
   - Verify your Google AI API key in `.env`
   - Ensure the key has necessary permissions

## Deployment

### Deploying to Heroku

1. **Install the Heroku CLI**:
   Download and install from [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli)

2. **Login to Heroku**:
   ```bash
   heroku login
   ```

3. **Create a new Heroku app**:
   ```bash
   heroku create your-app-name
   ```

4. **Add MongoDB Add-on or Configure MongoDB Atlas**:
   ```bash
   # If using MongoDB Atlas, set the environment variable
   heroku config:set MONGO_URI=your-mongodb-atlas-uri
   ```

5. **Configure Environment Variables**:
   ```bash
   heroku config:set SECRET_KEY=your-secret-key
   heroku config:set DEBUG=False
   heroku config:set GOOGLE_API_KEY=your-google-api-key
   ```

6. **Deploy the Application**:
   ```bash
   git add .
   git commit -m "Prepare for Heroku deployment"
   git push heroku main
   ```

7. **Run Migrations**:
   ```bash
   heroku run python manage.py migrate
   ```

8. **Create a Superuser** (optional):
   ```bash
   heroku run python manage.py createsuperuser
   ```

9. **Open the Application**:
   ```bash
   heroku open
   ```

### Important Notes for Deployment

- This application requires a MongoDB database. You can use MongoDB Atlas for a cloud-hosted solution.
- Make sure to set all required environment variables in your hosting platform.
- For production, always set `DEBUG=False` and use a strong, unique `SECRET_KEY`.
- The application uses WhiteNoise for serving static files in production.

## Support

For any issues or questions, please:
1. Check the troubleshooting guide above
2. Review the error messages in the console
3. Contact support at [support email]

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Django Framework
- Google Generative AI
- Bootstrap 5
- All contributors and supporters 