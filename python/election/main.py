from fastapi import FastAPI
from routers.election_router import router

from middleware.logging_middleware import log_requests

from database import Base,engine

app=FastAPI()

#create tables
Base.metadata.create_all(bind=engine)

#adding the middleware
app.middleware("http")(log_requests)

app.include_router(router)

@app.get("/")
def home():
    return {"message":"Election API running"}