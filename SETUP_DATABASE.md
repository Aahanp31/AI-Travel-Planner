# PostgreSQL Database Setup

This guide will help you set up PostgreSQL for the AI Travel Planner application.

## Option 1: Install PostgreSQL Locally

### macOS (using Homebrew)
```bash
# Install PostgreSQL
brew install postgresql@15

# Start PostgreSQL service
brew services start postgresql@15

# Create database
createdb travel_planner

# Create user (optional)
psql postgres
CREATE USER travel_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE travel_planner TO travel_user;
\q
```

### Ubuntu/Debian Linux
```bash
# Install PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib

# Start service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
sudo -u postgres psql
CREATE DATABASE travel_planner;
CREATE USER travel_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE travel_planner TO travel_user;
\q
```

### Windows
1. Download PostgreSQL from https://www.postgresql.org/download/windows/
2. Run the installer
3. During installation, set a password for the postgres user
4. Open pgAdmin or command line and create database:
```sql
CREATE DATABASE travel_planner;
```

## Option 2: Use Cloud PostgreSQL (Recommended for Production)

### Supabase (Free tier available)
1. Go to https://supabase.com
2. Create a new project
3. Get your connection string from Project Settings → Database
4. Copy the connection string (looks like: `postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres`)

### Heroku Postgres (Free tier available)
1. Go to https://www.heroku.com
2. Create a new app
3. Add "Heroku Postgres" add-on
4. Get connection string from Settings → Config Vars → DATABASE_URL

### Railway (Free tier available)
1. Go to https://railway.app
2. Create new project → Add PostgreSQL
3. Get connection string from the PostgreSQL service

## Configure Your Application

1. **Update your `.env` file** in the `backend` directory:
```env
DATABASE_URL=postgresql://username:password@localhost:5432/travel_planner
```

Replace with your actual credentials:
- **username**: Your PostgreSQL username (e.g., `travel_user` or `postgres`)
- **password**: Your PostgreSQL password
- **localhost**: Or your cloud database host
- **5432**: Default PostgreSQL port
- **travel_planner**: Your database name

Example for local setup:
```env
DATABASE_URL=postgresql://travel_user:your_password@localhost:5432/travel_planner
```

Example for Supabase:
```env
DATABASE_URL=postgresql://postgres:your_password@db.abc123.supabase.co:5432/postgres
```

2. **Install Python dependencies**:
```bash
cd backend
pip install -r requirements.txt
```

3. **Run the application**:
```bash
python app.py
```

The application will automatically create all necessary tables on first run.

## Verify Database Setup

Connect to your database and verify tables were created:

```bash
# Local PostgreSQL
psql -U travel_user -d travel_planner -c "\dt"

# Or using psql interactive mode
psql -U travel_user -d travel_planner
\dt  # List all tables
\d users  # Describe users table
\d saved_trips  # Describe saved_trips table
\q  # Quit
```

You should see two tables:
- `users`
- `saved_trips`

## Troubleshooting

### Connection refused
- Make sure PostgreSQL is running: `brew services list` (macOS) or `sudo systemctl status postgresql` (Linux)
- Check if PostgreSQL is listening on port 5432: `lsof -i :5432`

### Authentication failed
- Double-check your username and password in DATABASE_URL
- Make sure the user has access to the database

### Database does not exist
- Create the database: `createdb travel_planner`
- Or using psql: `CREATE DATABASE travel_planner;`

### Permission denied
- Grant privileges: `GRANT ALL PRIVILEGES ON DATABASE travel_planner TO your_user;`
- For all tables: `GRANT ALL ON ALL TABLES IN SCHEMA public TO your_user;`

## Production Recommendations

1. **Use environment-specific databases**:
   - Development: Local PostgreSQL
   - Production: Cloud PostgreSQL (Supabase, Railway, etc.)

2. **Enable SSL connections** for cloud databases:
   ```env
   DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require
   ```

3. **Set up database backups** (most cloud providers do this automatically)

4. **Use connection pooling** (already configured in app.py with `pool_pre_ping`)

5. **Monitor database performance** using your cloud provider's dashboard
