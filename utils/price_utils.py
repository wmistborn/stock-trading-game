import yfinance as yf

# --- Get latest price for a single stock ---
def get_latest_price(symbol):
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        price = info.get('regularMarketPrice') or info.get('previousClose')
        return float(price) if price else None
    except Exception as e:
        print(f"[ERROR] Could not fetch price for {symbol}: {e}")
        return None

# --- Get latest prices for multiple stocks ---
def get_latest_prices(symbols):
    prices = {}
    try:
        tickers = yf.Tickers(" ".join(symbols))
        for symbol in symbols:
            info = tickers.tickers[symbol].info
            price = info.get('regularMarketPrice') or info.get('previousClose')
            prices[symbol] = float(price) if price else None
    except Exception as e:
        print(f"[ERROR] Could not fetch multiple prices: {e}")
    return prices
