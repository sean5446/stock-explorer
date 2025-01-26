
import pandas as pd
import plotly.graph_objects as go


def human_readable_format(number):
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


def top_in_sector(sector: str, data):
    df = pd.DataFrame(data, columns=['symbol', 'short_name', 'sector', 'market_cap'])

    df['formatted_market_cap'] = df['market_cap'].apply(human_readable_format)

    fig = go.Figure(go.Pie(
        labels=df['short_name'],
        values=df['market_cap'], 
        hole=0.3,
        textinfo='none',
        hoverinfo='label+text+percent',
        text=df['formatted_market_cap'],
    ))

    # Customize the layout
    fig.update_layout(
        title=f"Top 20 Companies by Market Cap in the {sector} Sector",
        template="plotly_dark",
    )
    return fig.to_html(include_plotlyjs='cdn', full_html=False)


def get_all_sectors(data):
    df = pd.DataFrame(data, columns=['symbol', 'short_name', 'sector', 'market_cap'])

    sector_market_cap = df.groupby('sector')['market_cap'].sum().reset_index()

    fig = go.Figure(go.Pie(
        labels=sector_market_cap['sector'],
        values=sector_market_cap['market_cap'],
        hole=0.3,
        textinfo='none',
        hoverinfo='label+text+percent',
        text=sector_market_cap['market_cap'].apply(human_readable_format),
    ))

    # Customize the layout
    fig.update_layout(
        title="Market Cap by Sector",
        template="plotly_dark",
    )
    return fig.to_html(include_plotlyjs='cdn', full_html=False)
