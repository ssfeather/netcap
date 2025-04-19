import typer
import yaml
import numpy as np
import json
from pathlib import Path
from core import attenuation, threshold, grid, plot
from obspy import read, read_inventory
from obspy.signal import PPSD
from statistics import median
import os

app = typer.Typer()

# Compute detection capability grid
@app.command()
def compute(
    config: str = typer.Option('config.yaml', help='Config file'),
    out_nc: str = typer.Option('capability.npz', help='Output NPZ file')
):
    """Compute detection capability grid."""
    cfg = yaml.safe_load(Path(config).read_text())
    model = attenuation.AttenuationModel(**cfg['attenuation'])
    stations = cfg['stations']
    # Load or default noise_db
    if Path('noise_db.json').exists():
        noise_db = json.load(open('noise_db.json'))
    else:
        noise_db = {s['code']: s.get('noise', 1000) for s in stations}

    # Generate grid
    lat_min, lat_max = cfg['area']['lat']
    lon_min, lon_max = cfg['area']['lon']
    mesh_lat, mesh_lon = grid.generate_grid(
        lat_min, lat_max,
        lon_min, lon_max,
        cfg['area']['step']
    )
    mdet = np.zeros_like(mesh_lat)
    for i in range(mesh_lat.shape[0]):
        for j in range(mesh_lat.shape[1]):
            mdet[i,j] = threshold.m_detect(
                mesh_lat[i,j], mesh_lon[i,j], cfg['area']['depth_km'],
                stations, noise_db, model,
                cfg['snr'], cfg['n_req']
            )
    np.savez(out_nc, lat=mesh_lat, lon=mesh_lon, mdet=mdet)
    typer.echo(f'Grid saved to {out_nc}')


# Compute station noise and generate noise_db.json
@app.command()
def noise(
    data_root: str = typer.Argument(..., help='Root directory containing station subfolders'),
    out_json: str = typer.Option('noise_db.json', help='Output JSON filename'),
    win_length: int = typer.Option(3600, help='PPSD window length (s)')
):
    """Batch compute station noise using ObsPy PPSD and generate noise_db.json."""
    def calculate_noise(sta_dir: Path, win_length=3600):
        """
        计算一个台站的噪声 (RMS)，返回线性 RMS 噪声值。
        """
        noise_rms_list = []
        
        # 获取 RESP 文件，读取台站响应
        try:
            inv = read_inventory(next(sta_dir.glob("RESP*")))
        except Exception as e:
            print(f"警告：无法读取响应文件 {sta_dir}: {e}")
            return None

        # 遍历这个台站的数据（假设以 mseed 格式存储）
        for wf in list(sta_dir.glob("*.mseed"))[:5]:  # 只取前五个文件进行计算，减少运行时间
            try:
                st = read(wf)
                ppsd = PPSD(st[0].stats, inv, win_length=win_length)
                ppsd.add(st)
                rms_db = ppsd.get_percentile(50)  # 获取50%的分位数，单位是 dB
                noise_rms_list.append(rms_db)
            except Exception as e:
                print(f"警告：处理文件 {wf} 时发生错误: {e}")
                continue
        
        if not noise_rms_list:
            return None
        
        # 计算这些 RMS 的中位数
        db50 = median(noise_rms_list)
        
        # 将 dB 转换为线性振幅（µm/s）
        noise_lin = 10 ** (db50 / 20)
        
        return round(noise_lin, 3)  # 返回 3 位有效数字

    def generate_noise_db(data_root: str, out_json="noise_db.json"):
        """
        遍历所有台站，计算噪声并保存为 noise_db.json。
        """
        noise_db = {}
        
        for sta_dir in Path(data_root).iterdir():
            if sta_dir.is_dir():  # 确保是一个目录
                noise = calculate_noise(sta_dir)
                if noise is not None:
                    noise_db[sta_dir.name] = noise
                else:
                    print(f"跳过台站 {sta_dir.name}，没有足够的有效数据计算噪声")
        
        # 保存到 JSON 文件
        with open(out_json, "w") as f:
            json.dump(noise_db, f, indent=2)
        
        print(f"噪声数据已保存到 {out_json}")

    generate_noise_db(data_root, out_json)


# Plot the capability map with optional heatmap
@app.command()
def plotmap(
    grid_file: str = typer.Argument(..., help='Path to capability.npz file'),
    config: str = typer.Option('config.yaml', help='Config file'),
    outfile: str = typer.Option('map.png', help='Output image filename'),
    bins: str = typer.Option(
        None,
        help='Comma-separated magnitude thresholds, e.g. "0.1,0.5,1,2,3,4,5,6"'
    ),
    heatmap: bool = typer.Option(
        False, "--heatmap/--no-heatmap",
        help='Whether to draw continuous heatmap background'
    ),
    sigma: float = typer.Option(
        2.0, "--sigma",
        help='Gaussian smoothing σ for heatmap and contours'
    )
):
    """
    Plot detection capability map.
    - --heatmap: show continuous heatmap
    - --bins:    draw contour lines at specified ML thresholds
    - --sigma:   smoothing parameter
    """
    # Load data
    data = np.load(grid_file)
    cfg = yaml.safe_load(Path(config).read_text())

    # Parse bins
    bin_list = [float(b.strip()) for b in bins.split(',')] if bins else None

    # Call plotting routine
    plot.plot_capability(
        grid_lat=data['lat'],
        grid_lon=data['lon'],
        mdet=data['mdet'],
        stations=cfg['stations'],
        outfile=outfile,
        bins=bin_list,
        sigma=sigma,
        show_heatmap=heatmap
    )
    typer.echo(f'Map saved to {outfile}')


if __name__ == '__main__':
    app()