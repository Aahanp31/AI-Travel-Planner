"""
Database migration to add security fields to users table
"""
from app import app
from models import db, User

def add_security_fields():
    with app.app_context():
        # List of columns to add
        columns_to_add = [
            ('twofa_enabled', 'BOOLEAN DEFAULT 0'),
            ('twofa_code', 'VARCHAR(6)'),
            ('twofa_code_expiry', 'DATETIME'),
            ('reset_token', 'VARCHAR(32)'),
            ('reset_token_expiry', 'DATETIME')
        ]

        for column_name, column_type in columns_to_add:
            try:
                # Try to query the column (will fail if it doesn't exist)
                db.session.execute(db.text(f'SELECT {column_name} FROM users LIMIT 1'))
                print(f'✓ Column {column_name} already exists')
            except Exception:
                # Column doesn't exist, add it
                print(f'Adding column {column_name}...')
                db.session.execute(db.text(
                    f'ALTER TABLE users ADD COLUMN {column_name} {column_type}'
                ))
                db.session.commit()
                print(f'✓ Column {column_name} added')

        print('\n✓ All security fields migration completed successfully!')

if __name__ == '__main__':
    add_security_fields()
