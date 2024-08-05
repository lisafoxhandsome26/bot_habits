from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from config.sync_database import db


jobstores = {
    'default': SQLAlchemyJobStore(url=db.database_url_sync)
}
scheduler = BackgroundScheduler(jobstores=jobstores)
