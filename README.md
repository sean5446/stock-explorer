# FastAPI Stock Explorer

## Installing
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Database
Setup a postgres database with this schema:
```sql
CREATE TABLE stocks.yfinance (
	ticker varchar(5) NOT NULL,
	info jsonb NULL,
	weekly jsonb NULL,
	daily jsonb NULL,
	hourly jsonb NULL,
	CONSTRAINT yfinance_pk PRIMARY KEY (ticker)
);
CREATE INDEX idx_ticker ON stocks.yfinance USING btree (ticker);
CREATE INDEX idx_info_symbol ON stocks.yfinance ((info->>'symbol'));
```

Create functions - one for daily, monthly, hourly
```sql
CREATE OR REPLACE FUNCTION stocks.get_stock_five_year_history(sym text)
 RETURNS TABLE(symbol text, short_name text, close_history json[])
 LANGUAGE plpgsql
AS $function$
BEGIN
    RETURN QUERY
    SELECT
        info->>'symbol' AS symbol,
        info->>'shortName' AS short_name,
        array_agg(
            json_build_object(
                'close_date', to_timestamp((key)::numeric / 1000),
                'price', value::numeric
            )
        ) AS close_history
    FROM stocks.yfinance y,
        jsonb_each_text(weekly->'Close') AS close_data(key, value)
    WHERE ticker = sym
    GROUP BY symbol, short_name;
END;

CREATE OR REPLACE FUNCTION stocks.get_stock_one_month_history(sym text)
 RETURNS TABLE(symbol text, short_name text, close_history json[])
 LANGUAGE plpgsql
AS $function$
BEGIN
    RETURN QUERY
    SELECT
        info->>'symbol' AS symbol,
        info->>'shortName' AS short_name,
        array_agg(
            json_build_object(
                'close_date', to_timestamp((key)::numeric / 1000),
                'price', value::numeric
            )
        ) AS close_history
    FROM stocks.yfinance y,
        jsonb_each_text(hourly->'Close') AS close_data(key, value)
    WHERE ticker = sym
    GROUP BY symbol, short_name;
END;

CREATE OR REPLACE FUNCTION stocks.get_stock_one_year_history(sym text)
 RETURNS TABLE(symbol text, short_name text, close_history json[])
 LANGUAGE plpgsql
AS $function$
BEGIN
    RETURN QUERY
    SELECT
        info->>'symbol' AS symbol,
        info->>'shortName' AS short_name,
        array_agg(
            json_build_object(
                'close_date', to_timestamp((key)::numeric / 1000),
                'price', value::numeric
            )
        ) AS close_history
    FROM stocks.yfinance y,
        jsonb_each_text(daily->'Close') AS close_data(key, value)
    WHERE ticker = sym
    GROUP BY symbol, short_name;
END;

CREATE OR REPLACE FUNCTION stocks.get_top_companies_by_sector(sector_name text, result_limit integer)
 RETURNS TABLE(symbol text, short_name text, sector text, market_cap numeric)
 LANGUAGE plpgsql
AS $function$
BEGIN
    RETURN QUERY
    SELECT
        info->>'symbol' AS symbol,
        info->>'shortName' AS short_name,
        info->>'sector' AS sector,
        (info->>'marketCap')::numeric AS market_cap
    FROM stocks.yfinance y
    WHERE info->>'sector' = sector_name  -- Use the sector_name variable
    ORDER BY market_cap DESC  -- Order by market cap in descending order
    LIMIT result_limit;  -- Use the result_limit variable
END;
```

## Running
Run: `uvicorn main:app --host 0.0.0.0 --reload`

