# api/endpoints.py
import io

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from sqlalchemy.orm import Session

from db import repository, SessionLocal
from plot.sectors import pie_chart, pie_chart_all
from plot.stocks import history_chart, history_image


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
    return pie_chart(sector_name, data)


@router.get("/sectors/all", response_class=HTMLResponse)
async def get_sectors_market_cap(
    db: Session = Depends(get_db)
):
    data = repository.get_all_sectors(db)
    return pie_chart_all(data)


@router.get("/chart/{ticker}/{time}", response_class=HTMLResponse)
async def get_stock_five_year(
    ticker: str,
    time='1yr',
    db: Session = Depends(get_db)
):
    data = repository.get_stock_history(db, time, ticker)
    if not data:
        raise HTTPException(status_code=404, detail=f"No data found for '{ticker}'.")
    return history_chart(ticker, time, data)


@router.get("/top", response_class=JSONResponse)
async def get_top(
    order='DESC',
    db: Session = Depends(get_db)
):
    data = repository.get_top_change(db, order)
    rows = [tuple(row) for row in data]
    return rows


@router.get("/image/{ticker}", response_class=StreamingResponse)
async def get_image(
    ticker: str,
    db: Session = Depends(get_db)
):
    data = repository.get_stock_one_month_history(db, ticker)
    return StreamingResponse(io.BytesIO(history_image(data)), media_type="image/png")
