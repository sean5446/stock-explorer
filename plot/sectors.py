
import pandas as pd
import plotly.graph_objects as go


def number_to_shorthand(number):
    number = float(number)
    if number >= 1e12:
        return f'{number / 1e12:.2f}T'
    elif number >= 1e9:
        return f'{number / 1e9:.2f}B'
    elif number >= 1e6:
        return f'{number / 1e6:.2f}M'
    elif number >= 1e3:
        return f'{number / 1e3:.2f}K'
    else:
        return str(number)


def pie_chart(sector: str, data):
    df = pd.DataFrame(data, columns=['symbol', 'short_name', 'sector', 'market_cap'])

    df['formatted_market_cap'] = df['market_cap'].apply(number_to_shorthand)

    fig = go.Figure(go.Pie(
        labels=df['symbol'], # short_name
        values=df['market_cap'], 
        hole=0.3,
        textinfo='none',
        hoverinfo='label+text+percent',
        text=df['formatted_market_cap'] + ' ' + df['short_name'],
    ))

    fig.update_layout(
        title=f"{sector}",
        title_x=0.5,
        template="plotly_dark",
        autosize=True,
    )
    return fig.to_html(include_plotlyjs='cdn', full_html=False)


def pie_chart_all(data):
    df = pd.DataFrame(data, columns=['symbol', 'short_name', 'sector', 'market_cap'])

    sector_market_cap = df.groupby('sector')['market_cap'].sum().reset_index()
    sector_market_cap['sector'] = sector_market_cap['sector'].apply(lambda x: x[:11])

    fig = go.Figure(go.Pie(
        labels=sector_market_cap['sector'],
        values=sector_market_cap['market_cap'],
        hole=0.3,
        textinfo='none',
        hoverinfo='label+text+percent',
        text=sector_market_cap['market_cap'].apply(number_to_shorthand),
    ))

    fig.update_layout(
        title="Market Cap by Sector",
        title_x=0.5,
        template="plotly_dark",
        autosize=True,
    )
    return fig.to_html(include_plotlyjs='cdn', full_html=False)
