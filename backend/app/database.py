from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def ensure_schema() -> None:
    """轻量迁移：为旧库补 oven_type 列（无 Alembic 环境）。

    只补列、不按标签/备注猜测炉型；旧数据一律落到默认盘炉，
    由用户在炉位页改正后持久保存。
    """
    inspector = inspect(engine)
    with engine.begin() as conn:
        for table in ("products", "ovens"):
            if table not in inspector.get_table_names():
                continue
            cols = {c["name"] for c in inspector.get_columns(table)}
            if "oven_type" not in cols:
                conn.execute(
                    text(
                        "ALTER TABLE " + table + " ADD COLUMN oven_type "
                        "VARCHAR(10) DEFAULT 'tray' NOT NULL"
                    )
                )
