from fastapi import FastAPI
from domainmaster.log_manager import logger
from domainmaster.auth_middleware import AuthenticationMiddleware

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    logger.info("Starting up DomainMaster")
    from domainmaster import router
    from domainmaster.dependencies import setup_redis, config

    await setup_redis()
    app.add_middleware(AuthenticationMiddleware, api_key=config.api_key)
    app.include_router(router.router)
