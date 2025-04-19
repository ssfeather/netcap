
"""Compute detection threshold ML at grid points."""
import math
from geopy.distance import geodesic

def m_detect(lat, lon, depth_km, stations, noise_db, model, snr=3, n_req=4):
    m_low, m_high = 0.0, 6.0
    while m_high - m_low > 0.05:
        m_mid = (m_low + m_high) / 2
        hits = 0
        for s in stations:
            r = math.sqrt(depth_km**2 + geodesic((lat,lon),(s['lat'],s['lon'])).km**2)
            amp = model.ml_to_amp(m_mid, r)
            if amp / noise_db.get(s['code'],1000) >= snr:
                hits +=1
            if hits>=n_req: break
        if hits>=n_req: m_high=m_mid
        else: m_low=m_mid
    return round(m_high,2)
