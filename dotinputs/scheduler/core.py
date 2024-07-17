from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from config.environments import env


jobstores = {
    'default': SQLAlchemyJobStore(url=env.database_url_sync)
}
scheduler = BackgroundScheduler(jobstores=jobstores)
