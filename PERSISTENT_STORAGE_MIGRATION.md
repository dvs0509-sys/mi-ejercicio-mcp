# Issue #10: Persistent Data Storage - Implementation

## Overview
This implementation migrates the Mergington High School API from in-memory storage to persistent database storage using SQLite and SQLAlchemy ORM.

## Changes Made

### 1. **New Dependencies** (`requirements.txt`)
- **SQLAlchemy**: ORM for database operations
- **Alembic**: (included for future migrations, though not yet fully configured)

### 2. **New Database Module** (`src/database.py`)
- Defines SQLAlchemy models for:
  - `Activity`: Represents school activities with name, description, schedule, and capacity
  - `Participant`: Represents students signing up for activities
  - Association table: Manages many-to-many relationship between activities and participants
- Provides:
  - Database initialization on app startup
  - Initial data seeding from the original hardcoded activities
  - Database session management for dependency injection

### 3. **Updated App** (`src/app.py`)
- Removed hardcoded in-memory `activities` dictionary
- Added database initialization on application startup via `@app.on_event("startup")`
- Refactored all endpoints to use database queries:
  - `GET /activities`: Queries all activities from database
  - `POST /activities/{activity_name}/signup`: Creates participant records and adds to activity
  - `DELETE /activities/{activity_name}/unregister`: Removes participant from activity
- Added capacity checking to prevent overfilling activities

### 4. **Database File** 
- Stored as `src/mergington.db` (SQLite)
- Automatically created on first startup
- Persists across application restarts

### 5. **.gitignore Update**
- Added `*.db` to exclude database files from version control

## Database Schema

### Activities Table
```sql
CREATE TABLE activities (
    id INTEGER PRIMARY KEY,
    name VARCHAR UNIQUE NOT NULL,
    description VARCHAR,
    schedule VARCHAR,
    max_participants INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Participants Table
```sql
CREATE TABLE participants (
    email VARCHAR PRIMARY KEY,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Activity-Participants Junction Table
```sql
CREATE TABLE activity_participants (
    activity_id INTEGER PRIMARY KEY,
    participant_email VARCHAR PRIMARY KEY,
    signup_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(activity_id) REFERENCES activities(id),
    FOREIGN KEY(participant_email) REFERENCES participants(email)
);
```

## Installation & Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application:**
   ```bash
   cd src
   python -m uvicorn app:app --reload
   ```

3. On first startup:
   - Database schema is automatically created
   - Initial activity data is seeded from the hardcoded dataset

## Data Persistence

✅ **All data now persists** across:
- Application restarts
- Server reboots
- Browser refreshes

❌ **Data is lost only** when:
- Manually deleting `src/mergington.db`
- Running database reset scripts (when implemented)

## Future Enhancements

1. **Database Migrations**: Implement Alembic for schema versioning
2. **Backup/Restore**: Add tools for data backup and restoration
3. **PostgreSQL Support**: Currently SQLite, but can migrate to PostgreSQL
4. **Admin API**: Add endpoints for teachers to manage activities (linked to Issue #14)
5. **Data Export**: CSV/JSON export capabilities

## Testing

The API maintains backward compatibility. All existing endpoints work identically:
- Same request/response formats
- Same error codes and messages
- Same data types and structures

## Troubleshooting

### Database not being created
- Ensure the `src/` directory is writable
- Check that FastAPI startup event is being triggered

### Data not persisting
- Verify `mergington.db` file exists in `src/` directory
- Check database file permissions

### "Activity is at maximum capacity" error
- Expected behavior - activities now enforce max_participants limit
- This was not checked in the old in-memory version
