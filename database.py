from datetime import datetime

from sqlalchemy import create_engine, BigInteger, String, DateTime, select, exists
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from sqlalchemy.dialects.postgresql import insert

import settings

engine = create_engine(settings.DATABASE_URL, echo=bool(settings.DEBUG))

class Base(DeclarativeBase):
    pass


class Student(Base):
    __tablename__ = 'students'

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    group_id: Mapped[int] = mapped_column(BigInteger, nullable=False)

    # information of the student card
    name: Mapped[str] = mapped_column(String(255))
    st_number: Mapped[str] = mapped_column(String(255))
    national_number: Mapped[str] = mapped_column(String(255))
    degree: Mapped[str] = mapped_column(String(20))
    field: Mapped[str] = mapped_column(String(255))

    joined_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)


def init_db():
    """create all the tables in the database"""
    try:
        Base.metadata.create_all(bind=engine)
        print('Database initialized successfully with SQLAlchemy ORM.')
    except Exception as e:
        print(f'Error initializing database: {e}')


def check_student_joined(st_number):
    with Session(engine) as session:
        try:
            stmt = select(exists().where(Student.st_number == st_number))
            return session.execute(stmt).scalar()
        except Exception as e:
            print(f'Error hitting the database: {e}')
            return False


def save_student(**kwargs):
    with Session(engine) as session:
        try:
            stmt = insert(Student).values(**kwargs)

            session.execute(stmt)
            session.commit()
        except Exception as e:
            session.rollback()
            print(f'Error saving student to database: {e}')