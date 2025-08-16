# 🏷️ Tagging Feature Guide

This guide explains the new tagging functionality added to the Daily Notes Performance Emailer application.

## Overview

The tagging system allows users to:
- **Categorize notes** with custom tags (e.g., "Professional", "Personal", "Learning")
- **Select custom dates** for notes (not just the current timestamp)
- **Filter notes** by tags in the weekly view
- **Manage personal tags** through the Settings page
- **Organize notes** for better performance email generation

## Features

### 🗓️ Custom Date Selection
- When creating a note, users can select any date (not just today)
- Notes are organized by their selected date rather than creation timestamp
- Useful for logging accomplishments that happened on different days

### 🏷️ Tag Management
- **Create custom tags** with personalized names and colors
- **Default tags** available: Professional, Personal, Learning
- **Unique tags per user** - each user manages their own tag set
- **Color-coded tags** for visual organization

### 📝 Enhanced Note Creation
- **Date picker** to select when the accomplishment occurred
- **Tag dropdown** to categorize the note
- **Optional tagging** - notes can be saved without tags
- **Single tag per note** (multiple tags planned for future)

### 📊 Improved Note Display
- **Date range filtering** - All time, This week, This month, or Custom range
- **Tag filtering** to show notes with specific tags
- **Visual tag indicators** with custom colors
- **Enhanced note titles** showing date and tags
- **Note count display** showing filtered results
- **All notes shown by default** instead of just current week

### ⚙️ Settings Page Integration
- **Tag management section** in Settings
- **Add new tags** with custom names and colors
- **Delete unused tags** with confirmation
- **Create default tags** button for new users
- **Visual tag preview** with color coding

### ✏️ Note Editing Features
- **Individual note editing** directly from weekly notes view
- **Edit button** on each note for quick access
- **Update dates and tags** for existing notes without losing content
- **Backward compatibility** with notes created before tagging system

## Database Schema

### New Tables

#### `tags` Table
```sql
CREATE TABLE tags (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES app_users(id) ON DELETE CASCADE,
    name VARCHAR(50) NOT NULL,
    color VARCHAR(7) DEFAULT '#1f77b4',
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, name)
);
```

#### `note_tags` Junction Table
```sql
CREATE TABLE note_tags (
    id SERIAL PRIMARY KEY,
    note_id INTEGER REFERENCES notes(id) ON DELETE CASCADE,
    tag_id INTEGER REFERENCES tags(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(note_id, tag_id)
);
```

### Modified Tables

#### `notes` Table (Updated)
```sql
-- Added column:
ALTER TABLE notes ADD COLUMN note_date DATE DEFAULT CURRENT_DATE;
```

## API Methods

### Tag Management
- `get_user_tags(user_id)` - Retrieve all tags for a user
- `create_tag(user_id, name, color)` - Create a new tag
- `delete_tag(user_id, tag_id)` - Delete a tag
- `create_default_tags(user_id)` - Create default tags for new users

### Enhanced Note Operations
- `save_note_with_tag(user_id, content, note_date, tag_id)` - Save note with optional tag and date
- `get_weekly_notes(user_id)` - Get weekly notes with tag information
- `get_notes_with_tags(user_id, tag_id, limit)` - Get notes filtered by tag
- `get_all_notes_for_user(user_id, limit)` - Get all notes with tag information
- `update_note_with_tag(note_id, user_id, content, note_date, tag_id)` - Update existing note
- `get_note_by_id(note_id, user_id)` - Get specific note with tag information

## Migration

### For Existing Installations

1. **Run the migration script**:
   ```bash
   python migrate_add_tagging.py
   ```

2. **The migration will**:
   - Add `note_date` column to existing notes
   - Create `tags` and `note_tags` tables
   - Add necessary indexes for performance
   - Update existing notes with proper dates

3. **Backup recommended** before running migration

### For New Installations

The new schema is automatically created when running `db_manager.create_tables()`.

## Usage Examples

### Creating a Tagged Note
```python
# Save a note with a tag and custom date
note_id = db_manager.save_note_with_tag(
    user_id=1,
    content="Completed project milestone",
    note_date="2024-01-15",
    tag_id=2  # Professional tag
)
```

### Filtering Notes by Tag
```python
# Get all professional notes
professional_notes = db_manager.get_notes_with_tags(
    user_id=1,
    tag_id=2,  # Professional tag ID
    limit=50
)
```

### Managing Tags
```python
# Create a new tag
tag_id = db_manager.create_tag(
    user_id=1,
    name="Project Alpha",
    color="#ff5733"
)

# Get user's tags
tags = db_manager.get_user_tags(user_id=1)
```

### Editing Existing Notes
```python
# Update a note with new date and tag
success = db_manager.update_note_with_tag(
    note_id=123,
    user_id=1,
    content="Updated content",  # or None to keep existing
    note_date="2024-01-20",     # or None to keep existing
    tag_id=2                    # or None to keep existing, 0 to remove
)

# Get a specific note for editing
note = db_manager.get_note_by_id(note_id=123, user_id=1)
```

## UI Components

### Main App (app.py)
- Date picker for note date selection
- Tag dropdown with user's available tags
- Enhanced note display with tag filtering
- Color-coded tag indicators

### Settings Page (pages/2_⚙️_Settings.py)
- Tag management section
- Add new tags form with color picker
- Delete tags functionality
- Create default tags button
- Visual tag preview



## Testing

Run the comprehensive test suite:
```bash
python -m pytest tests/test_tagging_system.py -v
```

Tests cover:
- Tag creation and validation
- Note saving with tags
- Tag filtering and retrieval
- Error handling and edge cases
- Database integrity

## Future Enhancements

- **Multiple tags per note** - Allow assigning multiple tags to a single note
- **Tag hierarchies** - Support parent/child tag relationships
- **Tag-based email templates** - Generate different email formats based on tags
- **Tag analytics** - Show statistics and insights by tag
- **Tag sharing** - Allow sharing tag templates between users
- **Bulk tag operations** - Apply tags to multiple notes at once

## Troubleshooting

### Common Issues

1. **Migration fails**: Ensure database connection is working and you have proper permissions
2. **Tags not showing**: Check that `create_tables()` has been run to create new schema
3. **Duplicate tag error**: Tag names must be unique per user
4. **Date format issues**: Ensure dates are in ISO format (YYYY-MM-DD)

### Support

For issues or questions about the tagging feature, check:
1. Database connection and schema
2. Test suite results
3. Application logs for error messages
4. Migration script output

## Conclusion

The tagging system significantly enhances the note organization capabilities of the Performance Emailer, making it easier to categorize, filter, and manage daily accomplishments for more effective performance reporting.
