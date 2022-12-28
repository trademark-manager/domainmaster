import os
import uvicorn
from domainmaster.__init__ import app
from domainmaster.config import ServerSettings
from domainmaster.log_manager import logger

if __name__ == "__main__":
    settings = ServerSettings()
    logger.setLevel(settings.log_level.upper())
    logger.debug("Starting DomainMaster in debug mode")
    uvicorn.run(app, host=settings.host, port=settings.port, log_level=settings.log_level)
