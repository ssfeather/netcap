
# 地震台网监测能力计算与可视化

本项目提供了一套工具，用于计算地震台网的监测能力，并可视化结果。同时，它还支持计算台站的背景噪声，并将噪声数据存储到 `noise_db.json` 文件中。

## 目录
1. [功能概述](#功能概述)
2. [环境要求](#环境要求)
3. [安装指南](#安装指南)
4. [使用说明](#使用说明)
   - [1. 计算地震台网监测能力](#1-计算地震台网监测能力)
   - [2. 计算并生成噪声数据](#2-计算并生成噪声数据)
   - [3. 绘制监测能力图](#3-绘制监测能力图)
5. [配置文件说明](#配置文件说明)

---

## 功能概述
- **计算监测能力**：计算地震台网在不同震级下的监测能力，输出 NPZ 文件。
- **生成噪声数据**：计算每个台站的背景噪声，并生成 `noise_db.json` 文件。
- **绘制监测能力图**：绘制地震台网的监测能力图，可以选择热力图、等值线或二者叠加展示。

---

## 环境要求
- Python 3.x
- 必需的 Python 包：
  - `obspy`：用于读取和处理地震数据。
  - `numpy`：用于数值计算。
  - `matplotlib`：用于绘制图形。
  - `cartopy`：用于地理信息绘图。
  - `scipy`：用于高斯平滑。
  - `pyyaml`：用于读取配置文件。

安装依赖：
```bash
pip install obspy numpy matplotlib cartopy scipy pyyaml
```

---

## 安装指南

1. **克隆代码库：**

   ```bash
   git clone <repository_url>
   cd <project_directory>
   ```

2. **安装依赖：**

   ```bash
   pip install -r requirements.txt
   ```

---

## 使用说明

### 1. 计算地震台网监测能力

此命令计算地震台网的监测能力，并将结果存储为 NPZ 文件。

#### 命令：
```bash
python cli.py compute --config config.yaml --out-nc capability.npz
```

#### 参数：
- `--config`：`config.yaml` 配置文件路径。
- `--out-nc`：输出的 NPZ 文件，包含计算出的监测能力栅格。

### 2. 计算并生成噪声数据

此命令计算每个台站的背景噪声，并将其存储为 `noise_db.json` 文件。

#### 命令：
```bash
python cli.py noise /path/to/your/data --out-json noise_db.json
```

#### 参数：
- `/path/to/your/data`：包含台站子目录的根目录，子目录中包含地震数据文件。
- `--out-json`：输出的 `noise_db.json` 文件路径。
- `--win-length`：PPSD 计算时的窗口长度（默认为 `3600` 秒）。

### 3. 绘制监测能力图

此命令绘制地震台网的监测能力图。图形可以选择只显示热力图、只显示等值线，或者同时显示热力图和等值线。

#### 命令：
```bash
python cli.py plotmap capability.npz --outfile map.png --bins 0.1,0.5,1,2,3,4,5,6 --heatmap --sigma 2.0
```

#### 参数：
- `--outfile`：输出图像文件名（默认：`map.png`）。
- `--bins`：指定震级阈值的列表（例如：`0.1,0.5,1,2,3,4,5,6`）。
- `--heatmap`：是否绘制连续的热力图背景（默认：`False`）。
- `--sigma`：高斯平滑参数，控制热力图和等值线的平滑程度（默认：`2.0`）。

#### 示例：绘制热力图和等值线
```bash
python cli.py plotmap capability.npz --outfile map_with_heatmap.png --heatmap --bins 0.1,0.5,1,2,3 --sigma 1.5
```

---

## 配置文件说明

### `config.yaml`

`config.yaml` 文件用于配置地震台网监测能力计算的参数。

```yaml
network: DemoNet10
stations:
  - code: STA1
    lat: 35.10
    lon: 109.60
    elev: 900
  - code: STA2
    lat: 35.20
    lon: 110.00
    elev: 950
  - code: STA3
    lat: 35.30
    lon: 109.80
    elev: 850
  # ... 添加更多台站
area:
  lat: [34.5, 36.0]
  lon: [109.0, 112.0]
  depth_km: 5
  step: 0.2
snr: 1   # 信噪比阈值
n_req: 1 # 触发所需的台站数量
attenuation:
  logA0: -1.3
  gamma: 1.0
  kappa: 0.003
```

### `noise_db.json`

`noise_db.json` 文件存储每个台站的背景噪声水平。噪声值代表的是 RMS（均方根）噪声，以 µm/s 为单位。

`noise_db.json` 示例：

```json
{
  "STA1": 0.75,
  "STA2": 0.65,
  "STA3": 0.80
}
```

---

## 示例工作流程

1. **生成噪声数据**：
   ```bash
   python cli.py noise /path/to/data --out-json noise_db.json
   ```

2. **计算地震台网监测能力**：
   ```bash
   python cli.py compute --config config.yaml --out-nc capability.npz
   ```

3. **绘制监测能力图**：
   ```bash
   python cli.py plotmap capability.npz --outfile map.png --heatmap --bins 0.1,0.5,1,2,3 --sigma 1.5
   ```

---

### 常见问题

1. **没有显示等值线**：
   - 确保计算出的监测能力（`mdet`）覆盖了你在 `--bins` 中指定的震级阈值。如果没有覆盖，请检查 `config.yaml` 中的噪声设置（`noise_db.json`）和 `snr`、`n_req` 参数。

2. **`plot_capability` 函数未找到**：
   - 确保 `core/plot.py` 文件中包含了 `plot_capability` 函数，并且函数名正确。

3. **`noise` 命令报错**：
   - 确保台站目录中包含有效的 `.mseed` 数据文件和响应文件（`RESP_*`）。

---

这是一个完整的中文 `README.md` 文件，包含了该项目的功能说明、配置、使用命令等信息。你可以根据需要修改和定制其中的细节。如果你遇到其他问题，随时告诉我！
