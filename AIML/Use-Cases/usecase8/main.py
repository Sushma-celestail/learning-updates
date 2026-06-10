# """
# Entry point — run with:
#     uvicorn main:app --reload
# or:
#     python main.py
# """

# import uvicorn
# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware

# from settings import API_HOST, API_PORT, CORS_ORIGINS
# from src.api.routes import router

# app = FastAPI(title="Email Agent API", version="1.0.0")

# # Allow the frontend chat widget (any origin in CORS_ORIGINS) to call the API
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=CORS_ORIGINS,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# app.include_router(router, prefix="/api")


# @app.get("/health")
# def health() -> dict:
#     return {"status": "ok"}


# if __name__ == "__main__":
#     uvicorn.run("main:app", host=API_HOST, port=API_PORT, reload=True)