import time
import logging
from fastapi import Request

# configure logging
logging.basicConfig(
    filename="logs/app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)

logger=logging.getLogger("middleware")

async def log_requests(request:Request,call_next):
    start_time=time.time()

    #process request
    response=await call_next(request)

    process_time=(time.time()-start_time)*1000
    log_message=f"{request.method} {request.url.path} | {response.status_code} | {round(process_time,2)}ms"

    logger.info(log_message)

    return response


