import uvicorn
from domainmaster.__init__ import app
from domainmaster.config import ServerSettings
from domainmaster.log_manager import get_log_config

if __name__ == "__main__":
    settings = ServerSettings()
    uvicorn.run(app, host=settings.host, port=settings.port, log_config=get_log_config())
