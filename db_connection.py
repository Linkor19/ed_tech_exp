import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, Date, DateTime, Numeric
from sqlalchemy.orm import declarative_base, sessionmaker
from data_gen import plans, subjects, lessons, tests, users, marketing_costs, ab_test_segments, subscriptions, user_lessons, test_attempts, clickstream_logs

load_dotenv()

DBCON = os.getenv('DBCON')

engine = create_engine(f"postgresql://postgres:{DBCON}/ed_tech_proj")
SessionFactory = sessionmaker(bind=engine)
Base = declarative_base()


class Users(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True)
    registration_date = Column(Date)
    platform = Column(String(50))
    marketing_chanel = Column(String(50))


class Subscriptions(Base):
    __tablename__ = 'subscriptions'

    subscription_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    plan_id = Column(Integer, nullable=False)
    start_date = Column(Date)
    end_date = Column(Date)
    status = Column(String(20))
    price_paid = Column(Numeric)


class SubscriptionPlans(Base):
    __tablename__ = 'subscription_plans'

    plan_id = Column(Integer, primary_key=True)
    plan_name = Column(String(50))
    duration_days = Column(Integer, nullable=False)
    standart_price = Column(Integer)


class AbTestSegments(Base):
    __tablename__ = 'ab_test_segments'

    user_id = Column(Integer, primary_key=True)
    experiment_name = Column(String(50))
    variant = Column(String(50))


class Subjects(Base):
    __tablename__ = 'subjects'

    subject_id = Column(Integer, primary_key=True)
    subject_name = Column(String(100))


class Lessons(Base):
    __tablename__ = 'lessons'

    lesson_id = Column(Integer, primary_key=True)
    subject_id = Column(Integer, nullable=False)
    lesson_title = Column(String(100))
    difficulty = Column(String(20))


class Tests(Base):
    __tablename__ = 'tests'

    test_id = Column(Integer, primary_key=True)
    subject_id = Column(Integer, nullable=False)
    test_type = Column(String(50))


class MarketingCosts(Base):
    __tablename__ = 'marketing_costs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False)
    channel = Column(String(50), nullable=False)
    cost = Column(Numeric)


class UserLessons(Base):
    __tablename__ = 'user_lessons'

    id = Column(Integer, primary_key=True, autoincrement=True)
    lesson_id = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=False)
    completed_at = Column(DateTime)
    score = Column(Integer)


class TestAttempts(Base):
    __tablename__ = 'test_attempts'

    attempt_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    test_id = Column(Integer, nullable=False)
    started_at = Column(DateTime)
    finished_at = Column(DateTime)
    score = Column(Integer)
    max_score = Column(Integer)


class ClickstreamLogs(Base):
    __tablename__ = 'clickstream_logs'

    event_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    event_timestamp = Column(DateTime)
    event_type = Column(String(50))
    screen_name = Column(String(100))
    session_id = Column(String(50))


Base.metadata.create_all(engine)  # creates the tables in the DB if they are not there yet

# one-time data seed - commented out, so the rows are not duplicated on a second run of the file
# users.rename(columns={'marketing_channel': 'marketing_chanel'}).to_sql(
#     name='users',
#     con=engine,
#     if_exists='append',
#     index=False
# )
#
# plans.rename(columns={'standard_price': 'standart_price'}).to_sql(
#     name='subscription_plans',
#     con=engine,
#     if_exists='append',
#     index=False
# )
#
# subjects.to_sql(
#     name='subjects',
#     con=engine,
#     if_exists='append',
#     index=False
# )
#
# lessons.to_sql(
#     name='lessons',
#     con=engine,
#     if_exists='append',
#     index=False
# )
#
# tests.to_sql(
#     name='tests',
#     con=engine,
#     if_exists='append',
#     index=False
# )
#
# marketing_costs.to_sql(
#     name='marketing_costs',
#     con=engine,
#     if_exists='append',
#     index=False
# )
#
# ab_test_segments.to_sql(
#     name='ab_test_segments',
#     con=engine,
#     if_exists='append',
#     index=False
# )
#
# subscriptions.to_sql(
#     name='subscriptions',
#     con=engine,
#     if_exists='append',
#     index=False
# )
#
# user_lessons.to_sql(
#     name='user_lessons',
#     con=engine,
#     if_exists='append',
#     index=False
# )
#
# test_attempts.to_sql(
#     name='test_attempts',
#     con=engine,
#     if_exists='append',
#     index=False
# )
#
# clickstream_logs.to_sql(
#     name='clickstream_logs',
#     con=engine,
#     if_exists='append',
#     index=False
# )