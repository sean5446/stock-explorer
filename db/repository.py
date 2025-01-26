# db/repository.py

from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict


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