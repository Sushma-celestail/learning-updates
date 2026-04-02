from sqlalchemy import create_engine

engine = create_engine("postgresql://postgres.qwwvduykgdogpxzkaeiz:9x3K6mADrdQ0qjHy@aws-1-ap-southeast-1.pooler.supabase.com:5432/postgres")

with engine.connect() as conn:
    print("Connected successfully!")