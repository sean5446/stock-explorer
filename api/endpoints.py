# api/endpoints.py

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from db import repository, SessionLocal
from plot.sectors import top_in_sector, get_all_sectors
from plot.stocks import history


router = APIRouter()

# Dependency that provides a new database session for each API call
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/sectors/{sector_name}", response_class=HTMLResponse)
async def get_companies_by_sector(
    sector_name: str, 
    top: int = 20, 
    db: Session = Depends(get_db)
):
    data = repository.get_top_companies_by_sector(db, sector_name, top)
    if not data:
        raise HTTPException(status_code=404, detail="No companies found for this sector.")
    return top_in_sector(data)


@router.get("/sectors", response_class=HTMLResponse)
async def get_sectors_market_cap(
    db: Session = Depends(get_db)
):
    data = repository.get_all_sectors(db)
    return get_all_sectors(data)


@router.get("/chart/{ticker}/year/5", response_class=HTMLResponse)
async def get_stock_five_year(
    ticker: str,
    db: Session = Depends(get_db)
):
    data = repository.get_stock_five_year_history(db, ticker)
    if not data:
        raise HTTPException(status_code=404, detail=f"No data found for '{ticker}'.")
    return history(ticker, data)


@router.get("/chart/{ticker}/year/1", response_class=HTMLResponse)
async def get_stock_one_year(
    ticker: str,
    db: Session = Depends(get_db)
):
    data = repository.get_stock_one_year_history(db, ticker)
    if not data:
        raise HTTPException(status_code=404, detail=f"No data found for '{ticker}'.")
    return history(ticker, data)


@router.get("/chart/{ticker}/minutes/1", response_class=HTMLResponse)
async def get_stock_time_range(
    ticker: str,
    db: Session = Depends(get_db)
):
    data = repository.get_stock_one_year_history(db, ticker)
    if not data:
        raise HTTPException(status_code=404, detail=f"No data found for '{ticker}'.")
    return history(ticker, data)
