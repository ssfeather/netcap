
"""Noise processing utilities with batch capability."""
import json
from pathlib import Path
from obspy import read, read_inventory
from obspy.signal import PPSD
from statistics import median
import glob

def compute_station_noise(mseed_path: str, resp_path: str, outfile: str, win_length: int = 3600):
    st = read(mseed_path)
    inv = read_inventory(resp_path)
    ppsd = PPSD(st[0].stats, inv, win_length=win_length)
    ppsd.add(st)
    stats = {
        "station": st[0].stats.station,
        "channel": st[0].stats.channel,
        "rms_db": float(ppsd.get_percentile(50))
    }
    Path(outfile).write_text(json.dumps(stats, indent=2))
    return stats

def batch_compute_noise(data_root: str, out_json: str = 'noise_db.json', win_length: int = 3600):
    """Traverse data_root/<STA>/*.{mseed,sac} and RESP to build noise_db.json."""
    noise_dict = {}
    root = Path(data_root)
    for sta_dir in root.iterdir():
        if not sta_dir.is_dir(): continue
        mseed_files = sorted(glob.glob(str(sta_dir/'*.mseed'))) + sorted(glob.glob(str(sta_dir/'*.sac')))
        resp_files = glob.glob(str(sta_dir/'RESP*')) + glob.glob(str(sta_dir/'*.xml'))
        if not mseed_files or not resp_files:
            print(f'[WARN] {sta_dir.name} skipped (no data/resp)')
            continue
        inv = read_inventory(resp_files[0])
        rms_list = []
        for wf in mseed_files[:5]:
            st = read(wf)
            ppsd = PPSD(st[0].stats, inv, win_length=win_length)
            ppsd.add(st)
            rms_list.append(ppsd.get_percentile(50))
        if not rms_list: continue
        rms_db = median(rms_list)
        rms_lin = 10 ** (rms_db/20)
        noise_dict[sta_dir.name] = round(rms_lin,1)
    Path(out_json).write_text(json.dumps(noise_dict, indent=2))
    print(f'noise_db.json with {len(noise_dict)} stations')
    return noise_dict
