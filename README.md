
# Earthquake Network Monitoring Capability Calculation and Visualization

This project provides a set of tools for calculating the monitoring capabilities of earthquake networks and visualizing the results. It also supports calculating the background noise of stations and storing the noise data in the `noise_db.json` file.

## Table of Contents
1. [Feature Overview](#feature-overview)
2. [System Requirements](#system-requirements)
3. [Installation Guide](#installation-guide)
4. [Usage Instructions](#usage-instructions)
   - [1. Calculate Earthquake Network Monitoring Capability](#1-calculate-earthquake-network-monitoring-capability)
   - [2. Calculate and Generate Noise Data](#2-calculate-and-generate-noise-data)
   - [3. Plot Monitoring Capability Map](#3-plot-monitoring-capability-map)
5. [Configuration File Explanation](#configuration-file-explanation)

---

## Feature Overview
- **Monitor Capability Calculation**: Calculates the monitoring capability of the earthquake network at different magnitudes and outputs NPZ files.
- **Generate Noise Data**: Calculates the background noise of each station and generates the `noise_db.json` file.
- **Plot Monitoring Capability Map**: Plots the earthquake network's monitoring capability map, with options to display heatmaps, contour lines, or both.

---

## System Requirements
- Python 3.x
- Required Python Packages:
  - `obspy`: For reading and processing earthquake data.
  - `numpy`: For numerical calculations.
  - `matplotlib`: For plotting graphs.
  - `cartopy`: For geographic plotting.
  - `scipy`: For Gaussian smoothing.
  - `pyyaml`: For reading configuration files.

To install dependencies:
```bash
pip install obspy numpy matplotlib cartopy scipy pyyaml
```

---

## Installation Guide

1. **Clone the repository:**

   ```bash
   git clone <repository_url>
   cd <project_directory>
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

---

## Usage Instructions

### 1. Calculate Earthquake Network Monitoring Capability

This command calculates the earthquake network's monitoring capability and stores the results as an NPZ file.

#### Command:
```bash
python cli.py compute --config config.yaml --out-nc capability.npz
```

#### Parameters:
- `--config`: Path to the `config.yaml` configuration file.
- `--out-nc`: Output NPZ file containing the calculated monitoring capability grid.

### 2. Calculate and Generate Noise Data

This command calculates the background noise of each station and stores it in the `noise_db.json` file.

#### Command:
```bash
python cli.py noise /path/to/your/data --out-json noise_db.json
```

#### Parameters:
- `/path/to/your/data`: Root directory containing subdirectories for stations, each with earthquake data files.
- `--out-json`: Path to the output `noise_db.json` file.
- `--win-length`: Window length for PPSD calculation (default: `3600` seconds).

### 3. Plot Monitoring Capability Map

This command plots the earthquake network's monitoring capability map. The map can show a heatmap, contour lines, or both.

#### Command:
```bash
python cli.py plotmap capability.npz --outfile map.png --bins 0.1,0.5,1,2,3,4,5,6 --heatmap --sigma 2.0
```

#### Parameters:
- `--outfile`: Output image file name (default: `map.png`).
- `--bins`: List of magnitude thresholds (e.g., `0.1,0.5,1,2,3,4,5,6`).
- `--heatmap`: Whether to plot a continuous heatmap background (default: `False`).
- `--sigma`: Gaussian smoothing parameter, controlling the smoothness of the heatmap and contour lines (default: `2.0`).

#### Example: Plot heatmap and contour lines
```bash
python cli.py plotmap capability.npz --outfile map_with_heatmap.png --heatmap --bins 0.1,0.5,1,2,3 --sigma 1.5
```

---

## Configuration File Explanation

### `config.yaml`

The `config.yaml` file is used to configure the parameters for the earthquake network monitoring capability calculation.

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
  # ... Add more stations
area:
  lat: [34.5, 36.0]
  lon: [109.0, 112.0]
  depth_km: 5
  step: 0.2
snr: 1   # Signal-to-noise ratio threshold
n_req: 1 # Number of stations required to trigger
attenuation:
  logA0: -1.3
  gamma: 1.0
  kappa: 0.003
```

### `noise_db.json`

The `noise_db.json` file stores the background noise level for each station. The noise value represents the RMS (Root Mean Square) noise in µm/s.

Example of `noise_db.json`:

```json
{
  "STA1": 0.75,
  "STA2": 0.65,
  "STA3": 0.80
}
```

---

## Example Workflow

1. **Generate noise data**:
   ```bash
   python cli.py noise /path/to/data --out-json noise_db.json
   ```

2. **Calculate earthquake network monitoring capability**:
   ```bash
   python cli.py compute --config config.yaml --out-nc capability.npz
   ```

3. **Plot monitoring capability map**:
   ```bash
   python cli.py plotmap capability.npz --outfile map.png --heatmap --bins 0.1,0.5,1,2,3 --sigma 1.5
   ```

---

### Frequently Asked Questions

1. **No contour lines displayed**:
   - Ensure that the calculated monitoring capability (`mdet`) covers the magnitude thresholds specified in `--bins`. If not, check the noise settings in `config.yaml` and the `noise_db.json` file, as well as the `snr` and `n_req` parameters.

2. **`plot_capability` function not found**:
   - Ensure that the `core/plot.py` file contains the `plot_capability` function and that the function name is correct.

3. **`noise` command errors**:
   - Ensure that the station directory contains valid `.mseed` data files and response files (`RESP_*`).

---

This is a complete English `README.md` file containing the feature descriptions, configuration, usage commands, and other relevant information. Feel free to modify and customize the details as needed. If you encounter any other issues, don't hesitate to let me know!
