# Content Creator App

A professional dark-themed web application for content creation and social media automation.

## Features

- User authentication (login/signup)
- Dashboard interface
- Content ideation, creation, and scheduling (coming soon)
- Cross-platform posting (coming soon)
- Analytics and insights (coming soon)

## Project Structure

```
content-creator-app/
├── app/                       # Main application directory
│   ├── main.py                # FastAPI entry point
│   ├── config.py              # Configuration settings
│   ├── database.py            # Database connection
│   ├── api/                   # API endpoints
│   ├── models/                # Database models
│   ├── services/              # Business logic
│   ├── utils/                 # Utility functions
│   └── static/                # Static files
├── templates/                 # HTML templates
└── scripts/                   # Utility scripts
```

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- MySQL

### Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd content-creator-app
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:
   - Windows:
     ```
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```
     source venv/bin/activate
     ```

4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

5. Set up the database:
   - Create a MySQL database named `content_creator_db`
   - Update the `.env` file with your database credentials

6. Initialize the database:
   ```
   python scripts/init_db.py
   ```

### Running the Application

1. Start the application:
   ```
   python -m app.main
   ```

2. Open your browser and navigate to:
   ```
   http://localhost:8000
   ```

3. Default admin credentials:
   - Username: admin
   - Password: admin123

## Development

### Project Organization

- **API Routes**: Located in `app/api/`
- **Database Models**: Located in `app/models/`
- **Frontend Templates**: Located in `templates/`
- **Static Assets**: Located in `app/static/`

### Adding New Features

1. Create new API routes in `app/api/`
2. Add corresponding templates in `templates/`
3. Add CSS styling in `app/static/css/`
4. Add JavaScript functionality in `app/static/js/`

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- FastAPI for the web framework
- SQLAlchemy for database ORM
- Jinja2 for templating