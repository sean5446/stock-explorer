
import random
import requests
import time
import json

import psycopg2
import yfinance as yf


def read_stock_symbols(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file.readlines()]


def read_proxies(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file.readlines()]


def get_random_proxy(proxies):
    proxy = random.choice(proxies)
    return {'http': f'http://{proxy}', 'https': f'http://{proxy}'}


def get_proxies(file_path):
    url = 'https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&country=us&protocol=http&proxy_format=protocolipport&format=text&timeout=4000'
    response = requests.get(url)
    proxies = response.text.split('\r\n')
    with open(file_path, 'w') as f:
        for proxy in proxies:
            f.write(proxy + '\n')


def fetch_stock_data(ticker, proxies):
    proxy = None #get_random_proxy(proxies)
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        # 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
        today = "2025-01-25"
        weekly = '' # stock.history(start="2020-01-01", end=today, interval="1wk", proxy=proxy)
        daily = '' # stock.history(start="2024-01-01", end=today, interval="1d", proxy=proxy)
        hourly = stock.history(start="2024-12-01", end=today, interval="60m", proxy=proxy)
        return json.dumps(info), 'weekly.to_json()', 'daily.to_json()', hourly.to_json()
    except Exception as e:
        print(f"Error fetching data for {ticker} with proxy {proxy}: {e}")
        return None


def save_stock(conn, cursor, ticker, info, weekly, daily, hourly):
    # cursor.execute("""INSERT INTO stocks.yfinance (ticker, info, weekly, daily, hourly) 
    #                VALUES (%s, %s, %s, %s, %s)""", (ticker, info, weekly, daily, hourly))
    # cursor.execute("UPDATE stocks.yfinance SET daily = %s WHERE ticker = %s", (daily, ticker))
    cursor.execute("UPDATE stocks.yfinance SET hourly = %s WHERE ticker = %s", (hourly, ticker))
    conn.commit()


def stock_exists(cursor, ticker):
    cursor.execute("SELECT ticker from stocks.yfinance where ticker = %s", (ticker, ))
    result = cursor.fetchone()
    return result is not None


def main():
    stock_symbols_file = 'stocks.txt'
    proxies_file = 'proxies.txt'

    conn = psycopg2.connect(
        host="localhost",
        database="postgres",
        user="postgres",
        password="password",
    )
    cursor = conn.cursor()

    # get_proxies(proxies_file)
    proxies = read_proxies(proxies_file)
    stock_symbols = read_stock_symbols(stock_symbols_file)

    # ^GSPC

    for ticker in stock_symbols:
        if ticker == '':
            continue
        # if stock_exists(cursor, ticker):
        #     continue

        info, weekly, daily, hourly = fetch_stock_data(ticker, proxies)
        save_stock(conn, cursor, ticker, info, weekly, daily, hourly)
        time.sleep(0.5)

    cursor.close()
    conn.close()


if __name__ == "__main__":
    main()
