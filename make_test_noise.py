#!/usr/bin/env python3
import json

# 10 个台站的 code
stations = ["STA"+str(i) for i in range(1,11)]
# 全部设为 0.5 µm/s
noise_db = {code: 0.5 for code in stations}

with open("noise_db.json", "w") as f:
    json.dump(noise_db, f, indent=2)

print("Generated noise_db.json with 0.5 µm/s for all 10 stations")