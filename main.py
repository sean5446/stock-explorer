from datetime import datetime

from fastapi import FastAPI, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from sqlalchemy.orm import Session

from api.endpoints import router as api_router
from db import repository, SessionLocal
from plot.sectors import pie_chart, pie_chart_all, number_to_shorthand
from plot.stocks import history_chart

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
async def home(
    request: Request,
    db: Session = Depends(get_db)
):
    symbol = '^DJI'
    chart = repository.get_stock_history(db, symbol, '1mo')
    gainers = repository.get_top_change(db, "DESC")
    losers = repository.get_top_change(db, "")
    context = {
        "chart": history_chart(symbol, chart),
        "gainers": gainers,
        "losers": losers,
    }
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
        "Symbol": stats.get('symbol', 'Unknown'),
        "Name": stats.get('shortName', 'Unknown'),
        "Sector": stats.get('sector', 'Unknown'),
        "Industry": stats.get('industry', 'Unknown'),
        "City": stats.get('city', 'Unknown'),
        "Country": stats.get('country', 'Unknown'),
        "Exchange": stats.get('exchange', 'Unknown'),
        "Market Cap": stats.get('marketCap', 'Unknown'),
        "Trailing PE": stats.get('trailingPE', 'Unknown'),
        "Forward PE": stats.get('forwardPE', 'Unknown'),
        "Trailing EPS": stats.get('trailingEps', 'Unknown'),
        "Forward EPS": stats.get('forwardEps', 'Unknown'),
        "Last Split Date": stats.get('lastSplitDate', 'Unknown'),
        "Last Split Factor": stats.get('lastSplitFactor', 'Unknown'),
        "52 Week High": stats.get('fiftyTwoWeekHigh', 'Unknown'),
        "52 Week Low": stats.get('fiftyTwoWeekLow', 'Unknown'),
        "52 Week Change": stats.get('52WeekChange', 'Unknown'),
    }
    if table['Market Cap'] != 'Unknown':
        table['Market Cap'] = number_to_shorthand(table['Market Cap'])
    if table['Last Split Date'] != 'Unknown':
        table['Last Split Date'] = datetime.fromtimestamp(table['Last Split Date']).strftime('%Y-%m-%d')
    if table['52 Week High'] != 'Unknown':
        table['52 Week High'] = f"{table['52 Week High']:.2f}"
    if table['52 Week Low'] != 'Unknown':
        table['52 Week Low'] = f"{table['52 Week Low']:.2f}"
    if table['52 Week Change'] != 'Unknown':
        table['52 Week Change'] = f"{table['52 Week Change']:.2f}"
    if table['Trailing PE'] != 'Unknown':
        table['Trailing PE'] = f"{table['Trailing PE']:.2f}"
    if table['Forward PE'] != 'Unknown':
        table['Forward PE'] = f"{table['Forward PE']:.2f}"

    chart = repository.get_stock_history(db, symbol, time)

    context = {
        "symbol": symbol,
        "summary": stats.get('longBusinessSummary', 'Unknown'),
        "table": table,
        "chart": history_chart(symbol, chart),
    }
    return templates.TemplateResponse("stock.html", {"request": request, **context})


@app.get("/sectors", response_class=HTMLResponse)
async def sectors(
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
        "all_sectors": pie_chart_all(all_sectors), 
        "technology": pie_chart('Technology', technology),
        "communication_services": pie_chart('Communication Services', communication_services),
        "healthcare": pie_chart('Healthcare', healthcare),
        "consumer_cyclical": pie_chart('Consumer Cyclical', consumer_cyclical),
        "consumer_defensive": pie_chart('Consumer Defensive', consumer_defensive),
        "financial_services": pie_chart('Financial Services', financial_services),
        "industrials": pie_chart('Industrials', industrials),
        "energy": pie_chart('Energy', energy),
        "utilities": pie_chart('Utilities', utilities),
        "real_estate": pie_chart('Real Estate', real_estate),
        "basic_materials": pie_chart('Basical Materials', basic_materials),
    }
    return templates.TemplateResponse("overview.html", {"request": request, **context})


@app.get("/jupyter")
async def jupyter():
    return RedirectResponse(url="/jupyterlab")
