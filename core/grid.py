
import numpy as np

def generate_grid(lat_min, lat_max, lon_min, lon_max, step_deg=0.1):
    lats = np.arange(lat_min, lat_max+step_deg, step_deg)
    lons = np.arange(lon_min, lon_max+step_deg, step_deg)
    return np.meshgrid(lats, lons, indexing='ij')
