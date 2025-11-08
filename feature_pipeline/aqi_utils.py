def pm25_to_aqi(conc):
    if conc is None or conc != conc:
        return None
    c = float(conc)
    bps = [
        (0.0, 12.0, 0, 50),
        (12.1, 35.4, 51, 100),
        (35.5, 55.4, 101, 150),
        (55.5, 150.4, 151, 200),
        (150.5, 250.4, 201, 300),
        (250.5, 350.4, 301, 400),
        (350.5, 500.4, 401, 500)
    ]
    for Clow, Chigh, Ilow, Ihigh in bps:
        if Clow <= c <= Chigh:
            aqi = ((Ihigh - Ilow)/(Chigh - Clow)) * (c - Clow) + Ilow
            return round(aqi, 0)
    return 500.0
