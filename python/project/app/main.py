from fastapi import FastAPI, Depends
#from fastapi.responses import RedirectResponse 
from app.db.hr_db import SessionLocalHR
from app.db.sales_db import SessionLocalSales
#from app.db.db import SessionLocalHR,SessionLocalSales
from app.services.compare_service import compare_hr_tables, compare_hr_sales,employee_data
from app.core.logger import get_logger

logger = get_logger("main")

app = FastAPI()


def get_hr_db():
    db = SessionLocalHR()
    try:
        yield db
    finally:
        db.close()


def get_sales_db():
    db = SessionLocalSales()
    try:
        yield db
    finally:
        db.close()

#@app.get("/")
#def root():
#    return RedirectResponse(url="/redocs")


@app.get("/")
def home(db=Depends(get_hr_db)):
    logger.info("API / called")
    return compare_hr_tables(db)


@app.get("/compare")
def compare(hr_db=Depends(get_hr_db), sales_db=Depends(get_sales_db)):
    logger.info("API /compare called")
    return compare_hr_sales(hr_db, sales_db)

@app.get("/data")
def home(db=Depends(get_hr_db)):
    logger.info("API / called")
    return employee_data(db)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", reload=True)