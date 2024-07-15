from backend.run_fastapi import get_application, lifespan

app = get_application(lifespan)
