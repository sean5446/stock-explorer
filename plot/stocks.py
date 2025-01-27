
import plotly.graph_objects as go


def history_chart(ticker: str, time: str, data):
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
        title=f"{ticker} Close Price Over {time}",
        title_x=0.5,
        xaxis=dict(tickformat="%Y-%m-%d", tickangle=45),
        template="plotly_dark",
        autosize=True,
    )

    return fig.to_html(include_plotlyjs='cdn', full_html=False)


def history_image(data, scale=0.1, width=10):
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
        line=dict(color=line_color, width=width),
    ))

    fig.update_layout(
        xaxis=dict(
            showticklabels=False,
            showgrid=False,
        ),
        yaxis=dict(
            showticklabels=False,
            showgrid=False,
        ),
        template="plotly_dark",
    )
    return fig.to_image(format='png', scale=scale)
