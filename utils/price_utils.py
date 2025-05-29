import yfinance as yf

def get_current_price(symbol):
    try:
        stock = yf.Ticker(symbol)
        price = stock.history(period="1d")["Close"].iloc[-1]
        return round(float(price), 2)
    except:
        return None

def get_price_lookup(symbols):
    prices = {}
    for symbol in symbols:
        price = get_current_price(symbol)
        if price:
            prices[symbol] = price
    return prices
