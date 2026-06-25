import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# በ Railway Variables ውስጥ ያስገባኸው የዳታቤዝ ሊንክ (DATABASE_URL)
DATABASE_URL = os.getenv('DATABASE_URL')

# የዳታቤዝ ግንኙነትን የሚፈጥር ኮድ
# Supabase ለሚጠቀም PostgreSQL የ SSL ግንኙነት የግድ ያስፈልጋል
engine = create_engine(
    DATABASE_URL,
    connect_args={"sslmode": "require"},  # ግንኙነቱን ደህንነቱ የተጠበቀ ያደርገዋል
    pool_pre_ping=True,                  # ግንኙነት ቢቋረጥ ቦቱ ራሱ እንዲያስተካክል ይረዳል
    pool_recycle=1800                    # ግንኙነቱን በየ30 ደቂቃው ያድሰዋል
)

# ዳታቤዝን ለማንበብ ወይም ለመጻፍ የሚያስችል ክፍለ ጊዜ (Session)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
