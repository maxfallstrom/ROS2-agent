def try_float(val):
    try:
        return float(val)
    except (TypeError, ValueError):
        return 0.0