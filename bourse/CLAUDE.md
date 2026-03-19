# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A personal desktop stock portfolio manager for French (Euronext) stocks, written in Python with a Tkinter GUI. Targets Windows and is distributed as a standalone executable via PyInstaller.

## Commands

**Run the app:**
```bash
python bourse.py
```

**Build Windows executable:**
```bash
pyinstaller bourse.spec
```
Output: `dist/bourse.exe`

**Dependencies (install manually):**
```bash
pip install yfinance matplotlib requests
```

## Architecture

The entire application lives in `bourse.py` as a single monolithic class `BourseApp`. There are no modules, packages, or separate files beyond the spec and the data file.

**Data persistence:** `mon_portefeuille.json` (in `dist/` when running the compiled exe, or the project root when running via `python bourse.py`). Structure:
- `portefeuille`: list of current holdings
- `historique`: list of completed sales

**GUI structure — 4 tabs:**
1. **Portefeuille** — current holdings table with buy/sell/delete/refresh buttons
2. **Historique** — completed sales with realized gains summary
3. **Analyse Mes Actions** — per-stock fundamentals + interactive price chart (yfinance data)
4. **Explorateur Marché** — scans 54 CAC40/SBF120 stocks (`LISTE_MARCHE_PARIS`), sector filter, color-coded by upside potential

**External data:** All market data comes from `yfinance`. The Market Explorer tab uses a background thread (`threading.Thread`) to avoid blocking the GUI during scans.

**Key calculations:**
- Gain/loss per position: includes purchase fees, dividends filtered by `date_achat`, and current price
- ESG risk: mapped from a numeric score to 5 French labels (Negligible → Sévère)
- Analyst consensus: raw yfinance recommendation string mapped to French labels
