# Daily Notes App

A well-organized Streamlit web application for logging daily accomplishments and tracking progress throughout the week. This project follows the cookiecutter-streamlit template structure for maintainable and scalable code organization.

## Features

- 👤 User selection and management
- ✍️ Daily note entry with rich text area
- 📅 Weekly notes display for the current week
- 📊 Analytics dashboard with user statistics
- ⚙️ Settings page for user and app management
- 🔒 Secure database connection with AWS RDS PostgreSQL
- ✅ Input validation and error handling
- 📱 Responsive web interface with custom styling
- 🧪 Comprehensive test suite
- 🎨 Custom CSS styling and theming

## Prerequisites

- Python 3.8 or higher
- AWS RDS PostgreSQL database
- Required Python packages (see requirements.txt)
- Git (for version control)

## Setup Instructions


### 0. Create and activate a virtual environment (recommended)

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
```

Windows cmd:

```bat
python -m venv .venv
.\.venv\Scripts\activate.bat
python -m pip install -U pip
```

Git Bash:

```bash
python -m venv .venv
source .venv/Scripts/activate
python -m pip install -U pip
```

### 1. Clone and Navigate to Project
```bash
cd performance-emailer
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Secrets Configuration
The application uses a centralized secrets management system via `.streamlit/secrets.toml`.
Create this file locally and add your own values (never commit real secrets to git):

```toml
[database]
DB_HOST = "<your_db_host>"
DB_NAME = "<your_db_name>"
DB_USER = "<your_db_user>"
DB_PASSWORD = "<your_db_password>"
DB_PORT = "5432"
```

**Important**:
- `.streamlit/secrets.toml` is ignored by git for security
- Never commit secrets to version control; use placeholders in docs
- Update your local secrets.toml and keep it private for both local development and deployment

### 4. Initialize Database
Run the database initialization script to create tables and populate sample users:
```bash
python archive/init_database.py
```

### 5. Run the Application
Start the Streamlit application:
```bash
streamlit run app.py
```

The application will be available at `http://localhost:8501`

## Usage

### Main Page (Home)
1. **Select User**: Choose a user from the dropdown menu
2. **Write Note**: Enter your daily accomplishments in the text area
3. **Save Note**: Click the "Save Note" button to store your entry
4. **View Weekly Notes**: See all notes for the current week in the display area

### Analytics Page
- View user statistics and note counts
- See visual charts of user activity
- Monitor application usage patterns

### Settings Page
- Add new users to the system
- Manage existing users
- Configure application settings
- Test database connectivity

## Project Structure

This project follows the cookiecutter-streamlit template structure for better organization:

```
performance-emailer/
├── archive/                  # Archived scripts and documentation
│   ├── README.md            # Archive documentation
│   ├── init_database.py     # Database initialization script
│   ├── migrate_to_simple_auth.py # Migration script (one-time use)
│   ├── test_simple_auth.py  # Standalone authentication test
│   ├── run_tests.py         # Test runner utility
│   └── SIMPLE_AUTH_GUIDE.md # Implementation guide
├── assets/                   # Static assets
│   ├── css/
│   │   └── custom_style.css  # Custom CSS styling
│   └── images/               # Images and logos
│       └── README.md
├── output/                   # Generated output files
│   └── README.md
├── pages/                    # Multi-page app pages
│   ├── 1_📊_Analytics.py    # Analytics dashboard
│   └── 2_⚙️_Settings.py     # Settings and user management
├── src/                      # Source code
│   ├── components/          # Reusable components
│   │   ├── __init__.py
│   │   └── database.py      # Database operations
│   ├── calculations/        # Utility functions
│   │   ├── __init__.py
│   │   └── utils.py         # Validation and utilities
│   └── __init__.py
├── tests/                    # Test suite
│   ├── __init__.py
│   ├── test_database.py     # Database tests
│   └── test_utils.py        # Utility function tests
├── .streamlit/              # Streamlit configuration
│   ├── config.toml          # App configuration
│   └── secrets.toml         # Centralized secrets (not in git)
├── app.py                   # Main Streamlit application
├── requirements.txt         # Python dependencies
├── .gitignore              # Git ignore file
└── README.md               # This file
```

## Database Schema

### Users Table
- `id` (SERIAL PRIMARY KEY)
- `name` (VARCHAR(100) NOT NULL UNIQUE)
- `created_at` (TIMESTAMP WITHOUT TIME ZONE)

### Notes Table
- `id` (SERIAL PRIMARY KEY)
- `user_id` (INTEGER REFERENCES users(id))
- `content` (TEXT NOT NULL)
- `created_at` (TIMESTAMP WITHOUT TIME ZONE)

## Security Features

- Input sanitization to prevent XSS attacks
- SQL injection protection using parameterized queries
- Environment variable management for sensitive credentials
- Input validation with length and content checks

## Error Handling

The application includes comprehensive error handling for:
- Database connection issues
- Invalid user input
- Network connectivity problems
- Data validation errors

## Troubleshooting

### Database Connection Issues
- Verify your AWS RDS instance is running
- Check security group settings allow connections
- Ensure credentials in `.streamlit/secrets.toml` are correct
- Check that the database name matches your new configuration (`daily_notes_app_db`)

### Application Won't Start
- Verify all dependencies are installed: `pip install -r requirements.txt`
- Check Python version compatibility (3.8+)
- Run database initialization: `python archive/init_database.py`

## Testing

The project includes a comprehensive test suite using pytest:

### Running Tests
```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_utils.py

# Run tests in verbose mode
pytest -v
```

### Test Structure
- `tests/test_utils.py` - Tests for utility functions
- `tests/test_database.py` - Tests for database operations

## Development

### Code Quality Tools
```bash
# Format code with Black
black .

# Lint code with flake8
flake8 src/ tests/

# Type checking with mypy
mypy src/
```

### Adding New Pages
1. Create a new file in the `pages/` directory
2. Follow the naming convention: `N_🔥_PageName.py`
3. Import required modules from `src/`
4. Follow the existing page structure

### Custom Styling
- Edit `assets/css/custom_style.css` for custom styles
- Add images to `assets/images/`
- Update `.streamlit/config.toml` for theme changes

## Archive Folder

The `archive/` folder contains one-time run scripts, migration scripts, and documentation that are not part of the main application but may be useful for reference:

- **Migration scripts**: `migrate_to_simple_auth.py` - Database migration from Firebase to simple auth
- **Setup scripts**: `init_database.py` - Database initialization and sample data creation
- **Test utilities**: `test_simple_auth.py`, `run_tests.py` - Standalone testing scripts
- **Documentation**: `SIMPLE_AUTH_GUIDE.md` - Implementation guide for authentication system

These scripts were moved to the archive to keep the root directory clean while preserving them for future reference or maintenance tasks.

## Future Enhancements

- User authentication and registration
- Note editing and deletion capabilities
- Export notes to PDF or CSV
- Search and filter functionality
- Rich text formatting
- Email notifications
- Data visualization improvements


## Backlog

- Email sending from Summary page (implemented draft → confirm recipient → persist approved email → SMTP send → success/fail feedback). Paused for now while SMTP configuration and delivery paths are finalized.
