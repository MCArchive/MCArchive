# Base production config. Some secret stuff (API keys, email stuff) is added to
# this in the actual deployment.
import os

DEPLOYMENT='production'
REQUIRE_2FA = True

SECRET_KEY=os.environ['SECRET_KEY']

SQLALCHEMY_DATABASE_URI='postgresql://root:pgpasswd@postgres/mcarch'
RATELIMIT_STORAGE_URL='redis://redis:6379'

CACHE_TYPE='redis'
CACHE_REDIS_URL='redis://redis:6379'

# Database URI used for pytest
TEST_DATABASE_URI='postgresql://localhost/mcarch-test'

B2_KEY_ID=os.environ['B2_KEY_ID'] if 'B2_KEY_ID' in os.environ else None
B2_APP_KEY=os.environ['B2_APP_KEY'] if 'B2_APP_KEY' in os.environ else None
B2_PUBLIC_URL='https://b2.mcarchive.net/file/mcarchive/'
B2_BUCKET_NAME='mcarchive'

SESSION_COOKIE_SECURE = True
SESSION_COOKIE_SAMESITE = "Lax"

SQLALCHEMY_ECHO=False

MAIL_USE_TLS=True

