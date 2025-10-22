# IGROdisha-scraper

Lightweight scraper for harvesting registered land values from the Odisha government Inspector General of Registration website endpoints. The primary goal of this repository is to enumerate registration offices, villages and plot-level market rate values and persist them in CSV batches for downstream analysis.

This project is a collection of small, single-file Python scripts. The main scraping logic is duplicated in the `igrodisha_api_*.py` files and is intended to be run from the command line.

## Highlights

- Uses the public JSON endpoints on `igrodisha.gov.in` to list registration offices, villages, plots and plot-level values.
- Parallelizes per-plot HTTP requests with a `ThreadPool` to speed up scraping (for `igrodisha_api_multithread.py`).
- Persists results in CSV batches under a configurable `base_dir`.
- Designed for long-running runs with a resume-by-file-count heuristic (see `retVill` in `igrodisha_api_multithread.py`).

## Quick start (command-line)

1. Ensure Python 3.8+ is installed and required packages are available:

```bash
pip install requests pandas
```

2. Run the main script. By default, data is written to `./data` (POSIX-friendly).

```bash
python src/igrodisha_api_multithread.py
```

3. To change the output directory, either set the environment variable `IGRO_BASE_DIR` or pass `--base-dir`:

```bash
export IGRO_BASE_DIR=/path/to/igro-data
python src/igrodisha_api_multithread.py

# or
python src/igrodisha_api_multithread.py --base-dir /path/to/igro-data
```

The script prompts for a district ID and a registration office selection. It then iterates villages and plots, writing CSV batches to `base_dir/<DistId>/<RegName>/`.

### Dry-run mode

Both `igrodisha_api_multithread.py` and `igrodisha_api_enduser.py` support a `--dry-run` flag for quick testing. When `--dry-run` is set, processing is limited to the first registration office selection, the first village encountered and the first plot in that village.

Usage example:

```bash
python src/igrodisha_api_multithread.py --dry-run
```

## CSV layout and resume behavior

- CSV files are created in `base_dir/<DistId>/<RegName>/` and named `RegName_<n>.csv`.
- Each CSV has the columns: `District, RegistrationOff, Village, PlotID, Kisam, Value, Date, TransactionDate`.
- The scraper estimates progress by counting files in the registration office directory and assumes each file represents ~50 processed plots. This behavior is implemented in `retVill()` and must be preserved if you change file naming or batch size.

## Platform notes

- The project was developed on Windows and the original code contained a hard-coded Windows `base_dir` and an import of `winsound` (for auditory completion alerts, useful for long scraping jobs). The scraper now accepts `--base-dir` and respects `IGRO_BASE_DIR` for cross-platform use. `winsound` is safely guarded so the script runs on Linux/macOS.

## Notes on API endpoints

- `GetRegoffice` — `https://www.igrodisha.gov.in/ViewFeeValue.aspx/GetRegoffice`
- `GetVillage` — `https://www.igrodisha.gov.in/ViewFeeValue.aspx/GetVillage`
- `GetPlotDtl` — `https://www.igrodisha.gov.in/ViewFeeValue.aspx/GetPlotDtl`
- `GetKismByPlot` — `https://www.igrodisha.gov.in/ViewFeeValue.aspx/GetKismByPlot`
- `GetMRVal` — `https://www.igrodisha.gov.in/ViewFeeValue.aspx/GetMRVal`

## License

This repository includes a `LICENSE` file. Review it before reusing code.