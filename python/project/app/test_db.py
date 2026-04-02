# test_db.py
import psycopg2

conn = psycopg2.connect(
    "postgresql://postgres.qwwvduykgdogpxzkaeiz:9x3K6mADrdQ0qjHy@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres"
)

print("✅ Connected successfully")