from fastapi import FastAPI
from domainmaster.log_manager import logger

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    logger.info("Starting up DomainMaster")
    from domainmaster import router
    from domainmaster.dependencies import setup_redis

    await setup_redis()
    app.include_router(router.router)
