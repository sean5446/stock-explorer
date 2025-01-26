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
CREATE OR REPLACE FUNCTION get_stock_one_month_history(sym text)
RETURNS TABLE (
    symbol text,
    short_name text,
    close_history json[]
) AS $$
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
$$ LANGUAGE plpgsql;
```

## Running
Run: `uvicorn main:app --host 0.0.0.0 --reload`

