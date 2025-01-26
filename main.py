from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from sqlalchemy.orm import Session

from api.endpoints import router as api_router
from db import repository, SessionLocal
from plot.sectors import top_in_sector, get_all_sectors
from plot.stocks import history

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(api_router)
templates = Jinja2Templates(directory="templates")


# Dependency that provides a new database session for each API call
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    context = {"mesage": "Hello, World!"}
    return templates.TemplateResponse("index.html", {"request": request, **context})


@app.get("/stock/{symbol}", response_class=HTMLResponse)
async def stock(
    request: Request,
    symbol: str,
    time = '1yr',
    db: Session = Depends(get_db)
):
    stats = repository.get_stock_stats(db, symbol)[0][0]
    table = {
        "Symbol": stats['symbol'],
        "Name": stats['shortName'],
        "Sector": stats['sector'],
        "Industry": stats['industry'],
        "City": stats['city'],
        "State": stats['state'],
        "Country": stats['country'],
        "Exchange": stats['exchange'],
        "Market Cap": stats['marketCap'],
        "Trailing PE": stats['trailingPE'],
        "Forward PE": stats['forwardPE'],
        "Trailing EPS": stats['trailingEps'],
        "Forward EPS": stats['forwardEps'],
        "Last Split Date": stats['lastSplitDate'],
        "Last Split Factor": stats['lastSplitFactor'],
        "52 Week High": stats['fiftyTwoWeekHigh'],
        "52 Week Low": stats['fiftyTwoWeekLow'],
        "52 Week Change": stats['52WeekChange'],
    }
    chart = repository.get_stock_history(db, symbol, time)

    context = {
        "symbol": symbol,
        "summary": stats['longBusinessSummary'],
        "table": table,
        "chart": history(symbol, chart),
    }
    return templates.TemplateResponse("stock.html", {"request": request, **context})


@app.get("/overview", response_class=HTMLResponse)
async def overview(
    request: Request,
    db: Session = Depends(get_db)
):
    all_sectors = repository.get_all_sectors(db)
    technology = repository.get_top_companies_by_sector(db, "Technology")
    communication_services = repository.get_top_companies_by_sector(db, "Communication Services")
    healthcare = repository.get_top_companies_by_sector(db, "Healthcare")
    consumer_cyclical = repository.get_top_companies_by_sector(db, "Consumer Cyclical")
    consumer_defensive = repository.get_top_companies_by_sector(db, "Consumer Defensive")
    financial_services = repository.get_top_companies_by_sector(db, "Financial Services")
    industrials = repository.get_top_companies_by_sector(db, "Industrials")
    energy = repository.get_top_companies_by_sector(db, "Energy")
    utilities = repository.get_top_companies_by_sector(db, "Utilities")
    real_estate = repository.get_top_companies_by_sector(db, "Real Estate")
    basic_materials = repository.get_top_companies_by_sector(db, "Basic Materials")
    context = {
        "all_sectors": get_all_sectors(all_sectors), 
        "technology": top_in_sector('Technology', technology),
        "communication_services": top_in_sector('Communication Services', communication_services),
        "healthcare": top_in_sector('Healthcare', healthcare),
        "consumer_cyclical": top_in_sector('Consumer Cyclical', consumer_cyclical),
        "consumer_defensive": top_in_sector('Consumer Defensive', consumer_defensive),
        "financial_services": top_in_sector('Financial Services', financial_services),
        "industrials": top_in_sector('Industrials', industrials),
        "energy": top_in_sector('Energy', energy),
        "utilities": top_in_sector('Utilities', utilities),
        "real_estate": top_in_sector('Real Estate', real_estate),
        "basic_materials": top_in_sector('Basical Materials', basic_materials),
    }
    return templates.TemplateResponse("overview.html", {"request": request, **context})


@app.get("/explore")
async def explore():
    return RedirectResponse(url="/new-url")
