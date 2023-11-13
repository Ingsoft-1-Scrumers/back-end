import os

CARDS_PER_USER = 4

TEST = 'test'
PROD = 'production'
DEV = 'development'
ENVIRONMENT = os.getenv('ENVIRONMENT', PROD)

DATABASE_FILENAME = f"database_{ENVIRONMENT}.sqlite"