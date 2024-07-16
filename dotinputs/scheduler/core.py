from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from config.environments import env

url = "postgresql+psycopg2://Alexandr:asusk52j@localhost:5432/postgres"

jobstores = {
    'default': SQLAlchemyJobStore(url=env.database_url_sync)
}
scheduler = BackgroundScheduler(jobstores=jobstores)
