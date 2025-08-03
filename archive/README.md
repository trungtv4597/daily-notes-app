# Archive Folder

This folder contains one-time run scripts, migration scripts, and other utilities that are not part of the main application logic but may be useful for reference or future maintenance.

## Contents

### Migration Scripts
- `migrate_to_simple_auth.py` - Database migration script to convert from Firebase auth to simple authentication
- `init_database.py` - Database initialization script for creating tables and populating sample data

### Testing and Development Scripts
- `test_simple_auth.py` - Simple test script to verify the authentication system works
- `run_tests.py` - Test runner script for running unit tests and quality checks

### Documentation
- `SIMPLE_AUTH_GUIDE.md` - Implementation guide for the simple authentication system

## Usage Notes

These scripts were moved to the archive because:

1. **Migration scripts** (`migrate_to_simple_auth.py`) - One-time use scripts that were used to migrate the database structure. Should not be run again unless doing a fresh setup.

2. **Initialization scripts** (`init_database.py`) - Used for initial database setup. May be needed for new deployments but not for regular operation.

3. **Test scripts** (`test_simple_auth.py`) - Standalone test scripts that are separate from the main test suite in the `tests/` directory.

4. **Development utilities** (`run_tests.py`) - Development helper scripts that are useful but not part of the core application.

5. **Documentation** (`SIMPLE_AUTH_GUIDE.md`) - Implementation guides that are useful for reference but not needed for daily operation.

## Important Notes

- These scripts are preserved for historical reference and potential future use
- Before running any migration script, ensure you have a database backup
- Some scripts may need updates if the database schema or application structure changes
- The main application (`app.py`) and core source code (`src/`) remain in the root directory

## Restoration

If you need to restore any of these files to the root directory:
```bash
cp archive/filename.py ./
```
