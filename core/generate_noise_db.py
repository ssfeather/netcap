import json
import glob
import os
from obspy import read, read_inventory
from obspy.signal import PPSD
from pathlib import Path
from statistics import median
import numpy as np

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

# 主函数，设置数据根目录（根据你的目录结构调整）
if __name__ == "__main__":
    data_root = "/path/to/your/data"  # 替换为你的台站数据根目录
    out_json = "noise_db.json"
    generate_noise_db(data_root, out_json)