def calculate_position_size(balance, risk_pct, sl_pips, pip_value=10):
    """
    Calculate lot size berdasarkan risk management
    """
    if sl_pips <= 0 or pip_value <= 0:
        return 0.01
    
    risk_amount = balance * (risk_pct / 100)
    lot_size = risk_amount / (sl_pips * pip_value)
    
    return round(max(0.01, lot_size), 2)


def calculate_risk_reward(entry, sl, tp):
    """
    Calculate risk-reward ratio
    """
    risk = abs(entry - sl)
    reward = abs(tp - entry)
    
    if risk == 0:
        return {"ratio": 0, "risk": 0, "reward": 0}
    
    ratio = reward / risk
    
    return {
        "ratio": round(ratio, 2),
        "risk": round(risk, 5),
        "reward": round(reward, 5)
    }


def calculate_pip_value(pair, lot_size, exchange_rate=1.0):
    """
    Calculate nilai per pip
    """
    pip = 0.0001 if "JPY" not in pair else 0.01
    return lot_size * 100000 * pip