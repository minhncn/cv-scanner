from fastapi import FastAPI
import logging
from api.routes import router
from models.models import Candidate, WorkExperience, RawCV

logging.basicConfig(level=logging.DEBUG)

app = FastAPI()
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)