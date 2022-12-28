from domainmaster.log_manager import logger
from fastapi import FastAPI
from domainmaster.routes import home


def main():
    app = FastAPI()
    from domainmaster.dependencies import master

    logger.info("AC: " + master.access_token)
    app.include_router(home.router)
    return app


app = main()
