# Performance Emailer - Daily Notes App

A comprehensive Streamlit web application for logging daily accomplishments, organizing notes with tags, and generating professional performance emails. This project features a modern multi-page architecture with advanced note management capabilities.

## ✨ Latest Features (v2.0)

### 🏷️ Advanced Tagging System
- **Custom tags** with personalized names and colors
- **Tag-based organization** for better note categorization
- **Visual tag indicators** with color-coded display
- **Default tags** (Professional, Personal, Learning) for quick setup
- **Tag management** in Settings with create/delete functionality

### ✏️ Individual Note Editing
- **Edit any note** with inline editing forms
- **Update dates and tags** for existing notes
- **Content modification** without losing note history
- **Save/Cancel functionality** with real-time updates

### 📅 Enhanced Date Management
- **Custom date selection** for notes (not just current timestamp)
- **Date range filtering** - All time, This week, This month, Custom range
- **Backward compatibility** with existing notes
- **Smart date handling** with fallback to creation date

### 🏠 Restructured Application
- **Dedicated Home page** with welcome, stats, and navigation
- **Focused Notes page** with all note functionality
- **Enhanced Analytics** with comprehensive insights
- **Organized navigation** with clear page purposes

## Core Features

- � **User authentication** and session management
- 📝 **Rich note creation** with date and tag selection
- 🔍 **Advanced filtering** by date range and tags
- ✏️ **Individual note editing** with full form support
- 📊 **Analytics dashboard** with usage statistics and charts
- ⚙️ **Settings management** for profile and tags
- 🧾 **AI-powered email generation** for performance summaries
- 🔒 **Secure database** connection with PostgreSQL
- ✅ **Input validation** and comprehensive error handling
- 📱 **Responsive design** with custom styling
- 🧪 **Comprehensive test suite** with 13+ test cases

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
For new installations, run the database initialization script:
```bash
python archive/init_database.py
```

For existing installations upgrading to v2.0, run the tagging migration:
```bash
python archive/migrate_add_tagging.py
```
This will add the new tagging tables and update existing notes with proper date fields.

### 5. Run the Application
Start the Streamlit application:
```bash
streamlit run app.py
```

The application will be available at `http://localhost:8501`

## Usage

### 🏠 Home Page
- **Welcome dashboard** with user statistics and quick metrics
- **Feature highlights** showing latest updates and coming features
- **Navigation guide** with clear descriptions of each page
- **Quick action buttons** to jump directly to key functionality
- **Tips & help sections** with expandable guides for getting started

### 📝 Notes Page
1. **Create Notes**: Select date and tag, then write your accomplishments
2. **Filter Notes**: Use date range (All time, This week, This month, Custom) and tag filters
3. **View Notes**: Browse all your notes with visual tag indicators
4. **Edit Notes**: Click the ✏️ Edit button on any note to modify content, date, or tags
5. **Save Changes**: Use the inline editing form with Save/Cancel options

### 🧾 Summary Page
- **Generate performance emails** using AI from your notes
- **Filter by date range** to create targeted summaries
- **Choose email tone** (professional, friendly, confident)
- **Review and edit** before sending to your manager

### 📊 Analytics Page
- **Comprehensive statistics** including total notes, tagged notes, and activity metrics
- **Tag usage analysis** with charts showing most used tags
- **Activity timeline** displaying note creation patterns over time
- **Content insights** with word counts and averages per note

### ⚙️ Settings Page
- **Email configuration** for manager name and email address
- **Tag management** with create, delete, and color customization
- **Default tag creation** for new users (Professional, Personal, Learning)
- **Visual tag preview** with color-coded display

## Project Structure

This project follows the cookiecutter-streamlit template structure for better organization:

```
performance-emailer/
├── archive/                  # Archived scripts and documentation
│   ├── README.md            # Archive documentation
│   ├── init_database.py     # Database initialization script
│   ├── migrate_add_tagging.py # Tagging system migration script
│   ├── migrate_to_simple_auth.py # Auth migration script (one-time use)
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
│   ├── 0_🧾_Summary.py      # AI-powered email generation
│   ├── 1_📝_Notes.py        # Note creation, editing, and management
│   ├── 2_📊_Analytics.py    # Statistics and insights dashboard
│   └── 3_⚙️_Settings.py     # Profile and tag management
├── src/                      # Source code
│   ├── components/          # Reusable components
│   │   ├── __init__.py
│   │   ├── auth_ui.py       # Authentication components
│   │   └── database.py      # Database operations with tagging support
│   ├── calculations/        # Utility functions
│   │   ├── __init__.py
│   │   └── utils.py         # Validation and utilities
│   └── __init__.py
├── tests/                    # Test suite
│   ├── __init__.py
│   ├── test_database.py     # Database tests
│   ├── test_tagging_system.py # Tagging system tests (13 test cases)
│   └── test_utils.py        # Utility function tests
├── .streamlit/              # Streamlit configuration
│   ├── config.toml          # App configuration
│   └── secrets.toml         # Centralized secrets (not in git)
├── app.py                   # Home page with welcome and navigation
├── requirements.txt         # Python dependencies
├── .gitignore              # Git ignore file
├── TAGGING_FEATURE_GUIDE.md # Comprehensive tagging system documentation
└── README.md               # This file
```

## Database Schema

### App Users Table (`app_users`)
- `id` (SERIAL PRIMARY KEY)
- `username` (VARCHAR(50) NOT NULL UNIQUE)
- `display_name` (VARCHAR(100) NOT NULL)
- `email` (VARCHAR(255))
- `manager_name` (VARCHAR(100)) - For email generation
- `manager_email` (VARCHAR(255)) - For email generation
- `created_at` (TIMESTAMP WITHOUT TIME ZONE)

### Notes Table (`notes`)
- `id` (SERIAL PRIMARY KEY)
- `user_id` (INTEGER REFERENCES app_users(id))
- `content` (TEXT NOT NULL)
- `note_date` (DATE DEFAULT CURRENT_DATE) - Custom date selection
- `created_at` (TIMESTAMP WITHOUT TIME ZONE)

### Tags Table (`tags`)
- `id` (SERIAL PRIMARY KEY)
- `user_id` (INTEGER REFERENCES app_users(id))
- `name` (VARCHAR(50) NOT NULL)
- `color` (VARCHAR(7) DEFAULT '#1f77b4') - Hex color code
- `created_at` (TIMESTAMP WITHOUT TIME ZONE)
- `UNIQUE(user_id, name)` - Unique tag names per user

### Note Tags Junction Table (`note_tags`)
- `id` (SERIAL PRIMARY KEY)
- `note_id` (INTEGER REFERENCES notes(id) ON DELETE CASCADE)
- `tag_id` (INTEGER REFERENCES tags(id) ON DELETE CASCADE)
- `created_at` (TIMESTAMP WITHOUT TIME ZONE)
- `UNIQUE(note_id, tag_id)` - One tag per note (expandable to multiple)

### Sent Emails Table (`sent_emails`)
- `id` (SERIAL PRIMARY KEY)
- `user_id` (INTEGER REFERENCES app_users(id))
- `to_email` (VARCHAR(255) NOT NULL)
- `subject` (TEXT NOT NULL)
- `body` (TEXT NOT NULL)
- `status` (VARCHAR(32) DEFAULT 'queued')
- `error_message` (TEXT)
- `created_at` (TIMESTAMP WITHOUT TIME ZONE)
- `updated_at` (TIMESTAMP WITHOUT TIME ZONE)

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
- `tests/test_tagging_system.py` - Comprehensive tagging system tests (13 test cases)
  - Tag creation and validation
  - Note saving with tags
  - Individual note editing
  - Tag filtering and retrieval
  - Error handling and edge cases

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

## Recent Implementations ✅

- ✅ **User authentication and session management** - Complete with secure login system
- ✅ **Individual note editing capabilities** - Full inline editing with date and tag updates
- ✅ **Advanced search and filter functionality** - Date range and tag-based filtering
- ✅ **Tagging system** - Custom tags with colors and organization
- ✅ **Enhanced data visualization** - Analytics dashboard with charts and insights
- ✅ **Multi-page architecture** - Organized navigation with dedicated functionality pages

## Future Enhancements

- **Multiple tags per note** - Expand from single tag to multiple tag support
- **Bulk note operations** - Edit multiple notes simultaneously
- **Export functionality** - Export notes to PDF, CSV, or other formats
- **Rich text formatting** - Enhanced text editor with formatting options
- **Email notifications** - Automated reminders and summaries
- **Advanced analytics** - More detailed insights and reporting
- **Mobile app** - Native mobile application
- **Team collaboration** - Share notes and collaborate with team members
- **Integration APIs** - Connect with other productivity tools

## Current Development Status

### ✅ Completed (v2.0)
- Advanced tagging system with colors and management
- Individual note editing with inline forms
- Date range filtering and custom date selection
- Restructured multi-page application architecture
- Comprehensive analytics dashboard
- Enhanced user interface and navigation

### 🔄 In Progress
- Email sending from Summary page (implemented draft → confirm recipient → persist approved email → SMTP send → success/fail feedback). Paused while SMTP configuration and delivery paths are finalized.

### 📋 Planned
- Multiple tags per note support
- Bulk editing operations
- Enhanced mobile responsiveness
