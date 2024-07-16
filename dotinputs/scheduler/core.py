from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
#from config.environments import env
url = f"postgresql+psycopg2://Alexandr:asusk52j@localhost:5432/postgres"

jobstores = {
    'default': SQLAlchemyJobStore(url=url)
}
scheduler = BackgroundScheduler(jobstores=jobstores)
