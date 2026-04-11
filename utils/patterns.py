def detect_candlestick_pattern(df, lookback=5):
    """
    Deteksi candlestick pattern sederhana
    """
    patterns = []
    
    if len(df) < 2:
        return patterns
    
    for i in range(1, min(lookback + 1, len(df))):
        try:
            c = df.iloc[-i]
            p = df.iloc[-i - 1]
            
            o, cl, h, l = c["open"], c["close"], c["high"], c["low"]
            po, pc = p["open"], p["close"]
            
            body = abs(cl - o)
            prev_body = abs(pc - po)
            
            # Bullish Engulfing
            if pc < po and cl > o and o < pc and cl > po:
                patterns.append({
                    "pattern": "Bullish Engulfing",
                    "signal": "BULLISH",
                    "price": cl,
                    "date": df.index[-i]
                })
            
            # Bearish Engulfing
            elif pc > po and cl < o and o > pc and cl < po:
                patterns.append({
                    "pattern": "Bearish Engulfing",
                    "signal": "BEARISH",
                    "price": cl,
                    "date": df.index[-i]
                })
            
            # Hammer
            elif (min(o, cl) - l) > 2 * body and (h - max(o, cl)) < 0.3 * body:
                patterns.append({
                    "pattern": "Hammer",
                    "signal": "BULLISH",
                    "price": cl,
                    "date": df.index[-i]
                })
            
            # Shooting Star
            elif (h - max(o, cl)) > 2 * body and (min(o, cl) - l) < 0.3 * body:
                patterns.append({
                    "pattern": "Shooting Star",
                    "signal": "BEARISH",
                    "price": cl,
                    "date": df.index[-i]
                })
        
        except Exception:
            continue
    
    return patterns