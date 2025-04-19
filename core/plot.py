import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import numpy as np
from scipy.ndimage import gaussian_filter

def plot_capability(
    grid_lat, grid_lon, mdet, stations,
    outfile='map.png', bins=None,
    sigma=2, show_heatmap=False
):
    """
    Plot detection capability map.
    - bins=None: 画连续热力图（若 show_heatmap=True）或只画台站
    - bins=[…]:   对每个 M 绘制可探测区的平滑等值线
    - sigma:      Gaussian smoothing σ（格点数）
    - show_heatmap:是否绘制背景热力图
    """
    # 打印调试信息
    mn, mx = np.nanmin(mdet), np.nanmax(mdet)
    print(f"DEBUG: mdet in [{mn:.2f}, {mx:.2f}]")

    # 平滑栅格用于等值线/热力图
    mdet_s = gaussian_filter(mdet, sigma=sigma) if sigma > 0 else mdet

    fig = plt.figure(figsize=(10,8))
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.coastlines()
    gl = ax.gridlines(draw_labels=True, linestyle='--', linewidth=0.5)
    gl.top_labels = False
    gl.right_labels = False

    # 1) 背景热力图
    if show_heatmap:
        cmap = plt.get_cmap('viridis_r')
        levels = np.arange(mn, mx + 0.2, 0.2)
        cs = ax.contourf(
            grid_lon, grid_lat, mdet_s,
            levels=levels, cmap=cmap, alpha=0.6,
            transform=ccrs.PlateCarree()
        )
        plt.colorbar(cs, ax=ax, orientation='vertical', label='Detectable ML')

    # 2) 等值线
    if bins:
        cmap = plt.get_cmap('tab10')
        handles, labels = [], []
        for idx, M in enumerate(bins):
            mask = (mdet_s <= M).astype(float)
            if not mask.any():
                continue
            ax.contour(
                grid_lon, grid_lat, mask,
                levels=[0.5],
                colors=[cmap(idx / (len(bins)-1))],
                linewidths=2,
                transform=ccrs.PlateCarree()
            )
            h = mlines.Line2D([], [], color=cmap(idx / (len(bins)-1)), lw=2)
            handles.append(h)
            labels.append(f'M≤{M}')
        if handles:
            ax.legend(handles, labels, title='Detectable ML thresholds', loc='lower left')

    # 3) 叠加台站
    for s in stations:
        ax.plot(s['lon'], s['lat'], '^', color='red', markersize=4, transform=ccrs.PlateCarree())
        ax.text(s['lon']+0.04, s['lat']+0.04, s['code'], fontsize=6, transform=ccrs.PlateCarree())

    ax.set_title('Seismic Network Detection Capability', fontsize=12)
    fig.savefig(outfile, dpi=300, bbox_inches='tight')
    plt.close(fig)