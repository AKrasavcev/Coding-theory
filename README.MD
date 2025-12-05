Golay C(23,12) — Python implementation
=====================================

This repository contains a practical implementation of the binary Golay
C(23,12) code and an end-to-end pipeline that: reads 24-bit BMP images,
splits the byte stream into 12-bit payloads, encodes them to 23-bit
codewords, simulates transmission through a Binary Symmetric Channel
(BSC), decodes with IMLD, and reconstructs the image. An experiment
harness is included to evaluate Bit Error Rate (BER) and timings.

Requirements
------------
- Python 3.10+ (3.13 recommended)
- Install dependencies:

```powershell
pip install pillow
```

Optional (to make a single exe):

```powershell
pip install pyinstaller
pyinstaller --onefile main.py
```

Quick start
-----------
Run the interactive demo:

```powershell
python .\main.py
```

Follow the menu to test:
- `1` — enter a 12-bit vector (interactive)
- `2` — encode/decode a short text string
- `3` — run the full image pipeline on a 24-bit BMP file

Experiments (batch measurements)
-------------------------------
Use `experiments.py` to run a set of trials over several channel error
probabilities `p` and collect averaged BER and timing results. The script
will create a 1 MB dummy file (`dummy_1MB.bin`) if one isn't present.

Run experiments:

```powershell
python .\experiments.py
```

Configurable parameters inside `experiments.py`:
- `p_values` — list of channel error probabilities to test
- `max_workers` — number of worker processes used for parallel stages
- `num_runs` — number of independent runs per `p` (default in the script: 10)

Outputs produced by experiments:
- `experiments_results.csv` — row per run with timings and error counts
- `experiments_results_avg.csv` — per-`p` averages across `num_runs`

Notes & troubleshooting (Windows)
--------------------------------
- The code uses `multiprocessing` and spawns worker processes via
	`ProcessPoolExecutor`. On Windows the spawn overhead and antivirus
	(e.g., Windows Defender) can increase timing variance. If you see
	large fluctuations, try lowering `max_workers` or reusing a
	long-lived pool.
- The script calls `multiprocessing.freeze_support()` to be compatible
	with frozen executables and Windows spawn semantics.

Files of interest
-----------------
- `main.py` — interactive demo and image pipeline
- `functions.py` — core encode/decode/channel/packing helpers
- `experiments.py` — experiment harness that saves CSVs
- `report.tex` — LaTeX report (includes PGFPlots templates using
	`experiments_results_avg.csv`)
