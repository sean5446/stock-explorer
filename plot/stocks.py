
import plotly.graph_objects as go


def history(ticker: str, data):
    close_history = data[0][2]
    dates = []
    prices = []

    for entry in close_history:
        dates.append(entry['close_date'])
        prices.append(entry['price'])
    
    line_color = 'green' if prices[-1] >= prices[0] else 'red'

    fig = go.Figure(data=go.Scatter(
        x=dates, 
        y=prices, 
        mode='lines+markers',
        line=dict(color=line_color)
    ))

    fig.update_layout(
        title=f"{ticker} Stock Close Price Over Time",
        xaxis_title="Date",
        yaxis_title="Close Price (USD)",
        xaxis=dict(tickformat="%Y-%m-%d", tickangle=45),
        template="plotly_dark"
    )

    return fig.to_html(include_plotlyjs='cdn', full_html=False)
