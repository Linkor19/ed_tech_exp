# Ed-Tech Product Analytics

A self-contained analytics case study built around a fictional ed-tech (test-prep) mobile app. It covers the full loop: synthetic data generation, a relational schema in PostgreSQL, ad-hoc SQL analysis, A/B test evaluation, event-log quality checks, and marketing channel economics (CAC / ROMI / LTV), wrapped up with a BI-style visualization layer.

Repository: https://github.com/Linkor19/ed_tech_exp

> **Note:** the full write-up (methodology, queries, findings) is written in **Ukrainian**. It lives in `Ed-tech proj.md`, kept alongside this project locally and not part of this repository snapshot (see below).

## Project structure

Files tracked in this repository:

- `data_gen.py` - generates a synthetic dataset (users, subscriptions, lessons, tests, marketing spend, A/B segments, clickstream logs) into `data/*.csv`
- `db_connection.py` - defines the PostgreSQL schema via SQLAlchemy ORM and loads the CSVs into the `ed_tech_proj` database
- `main.py` - Python-side analysis (A/B test conversion rates, significance testing, bootstrap)
- `createdb.sql` - DDL: tables, primary/foreign keys
- `ad_hoc_task.sql` - retention, hardest-lesson, and test-duration ad-hoc queries
- `ab_test_cr.sql` - conversion rate per A/B test variant
- `measures_and_check.sql` - `user_sub` view, channel-level metrics (ARPU/ARPPU/CAC/ROMI), and clickstream log quality checks

Kept locally, not pushed to this repository:

- `data/` - generated CSV datasets (regenerate with `data_gen.py`)
- `Ed-tech proj.md` - the full analysis write-up (in Ukrainian)

## Tech stack

- **Python 3.13**
- **pandas / numpy** - data wrangling
- **matplotlib / seaborn** - visualization
- **SQLAlchemy + psycopg2** - ORM and PostgreSQL driver
- **python-dotenv** - environment config
- **PostgreSQL** - primary datastore, target of most of the analysis (SQL queries in `Ed-tech proj.md`)
- **Power BI (DAX)** - dashboarding / KPI layer (CAC, LTV, DAU, MAU, ARPU, ARPPU)

## Setup

1. Have a PostgreSQL instance running locally and create a database named `ed_tech_proj`.
2. Create a `.env` file in the project root with the connection string:
   ```
   DBCON='<user>:<password>@<host>:<port>'
   ```
3. Create a virtual environment and install dependencies:
   ```
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```
4. Generate the dataset and load it into the database:
   ```
   python data_gen.py
   python db_connection.py
   ```
   (the `to_sql` calls in `db_connection.py` are commented out after the first run to avoid duplicate inserts - uncomment for a fresh load)
5. Run `main.py` for the Python-side A/B test analysis, or use the SQL snippets from `Ed-tech proj.md` directly against the database.
