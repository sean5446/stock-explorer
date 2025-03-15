# db/repository.py

from sqlalchemy.orm import Session
from sqlalchemy import text


def get_top_companies_by_sector(db: Session, sector_name: str, top_limit=20):
    result = db.execute(
        text("SELECT * FROM stocks.get_top_companies_by_sector(:sector_name, :top_limit)"), 
        {"sector_name": sector_name, "top_limit": top_limit}
    )
    return result.fetchall()


def get_all_sectors(db: Session):
    result = db.execute(text("""
    SELECT 
        info->>'symbol' AS symbol,
        info->>'shortName' AS short_name,
        info->>'sector' AS sector,
        (info->>'marketCap')::numeric AS market_cap
    FROM stocks.yfinance y;
    """))
    return result.fetchall()


def get_stock_five_year_history(db: Session, ticker: str):
    result = db.execute(
        text("SELECT * FROM stocks.get_stock_five_year_history(:ticker)"), 
        {"ticker": ticker}
    )
    return result.fetchall()


def get_stock_one_year_history(db: Session, ticker: str):
    result = db.execute(
        text("SELECT * FROM stocks.get_stock_one_year_history(:ticker)"), 
        {"ticker": ticker}
    )
    return result.fetchall()


def get_stock_one_month_history(db: Session, ticker: str):
    result = db.execute(
        text("SELECT * FROM stocks.get_stock_one_month_history(:ticker)"), 
        {"ticker": ticker}
    )
    return result.fetchall()


def get_stock_history(db: Session, ticker: str, time: str):
    if time == '5yr':
        return get_stock_five_year_history(db, ticker)
    elif time == '1yr':
        return get_stock_one_year_history(db, ticker)
    elif time == '1mo':
        return get_stock_one_month_history(db, ticker)
    else:
        return []


def get_stock_stats(db: Session, ticker: str):
    result = db.execute(
        text("SELECT info FROM stocks.yfinance WHERE ticker = :ticker"), 
        {"ticker": ticker}
    )
    return result.fetchall()


def get_top_change(db: Session, sort='DESC', limit=15):
    result = db.execute(text(f"""
    SELECT 
        info->>'symbol' AS symbol,
        info->>'shortName' AS short_name,
        info->>'currentPrice' AS price,
        info->>'regularMarketPreviousClose' AS close,
        ROUND(((info->>'currentPrice')::numeric - (info->>'regularMarketPreviousClose')::numeric), 2) as change,
        ROUND(((info->>'currentPrice')::numeric - (info->>'regularMarketPreviousClose')::numeric) / (info->>'currentPrice')::numeric  * 100, 2) AS percent
    FROM stocks.yfinance y
    where info->>'currentPrice' is not null and info->>'previousClose' is not null
    ORDER BY percent {sort}
    LIMIT {limit};
    """))
    return result.fetchall()


def get_close_52wk_low(db: Session, limit=15):
    result = db.execute(text(f"""
    SELECT 
        info->>'symbol' AS symbol,
        info->>'shortName' AS short_name,
        info->>'currentPrice' AS price,
        info->>'fiftyTwoWeekLow' AS low,
        ROUND(((info->>'currentPrice')::numeric - (info->>'fiftyTwoWeekLow')::numeric) / (info->>'currentPrice')::numeric  * 100, 2) AS percent
    FROM stocks.yfinance y
    where info->>'currentPrice' is not null and info->>'fiftyTwoWeekLow' is not null
    ORDER BY percent ASC
    LIMIT {limit};
    """))
    return result.fetchall()


def search(db: Session, term: str, limit=10):
    term = term.replace("'", "")
    result = db.execute(
        text(f"""
        SELECT ticker, info->>'shortName' AS short_name
        FROM stocks.yfinance
        WHERE ticker ILIKE '%{term}%' OR info->>'shortName' ILIKE '%{term}%'
        LIMIT {limit}
        """),
        {"term": term}
    )
    return result.fetchall()
