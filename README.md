# MSDS-451-PA2

MSDS 451 Financial Engineering, Programming Assignment 2.

This project is a Monte Carlo study of portfolio opportunity sets for four risky assets. For each set of assets, it generates 700 sets of returns from a multivariate normal distribution and 700 random sets of portfolio weights under two strategies: long positions only, and long and short positions allowed. Each set of weights gets a portfolio return (mean) and risk (standard deviation), and the results are plotted as return versus risk.

The study is run twice:

1. **Starter assets.** The four assets (A, B, C, D) with the expected returns, volatilities, and correlations given in the professor's starter code.
2. **My assets.** Four real assets: a bond fund (BND), gold (GLD), an S&P 500 fund (SPY), and bitcoin (BTC-USD). Their expected returns, volatilities, and correlations are estimated from daily Yahoo Finance prices, 2015 through 2025.

The program is the professor's starter script (written in R), translated to Python and modified to run both sets of initial conditions.

## Repository contents

| File | Purpose |
|---|---|
| `pa2.py` | Main program. Runs the Monte Carlo study for both sets of assets. |
| `getdata_yfinance.py` | Downloads the price history for the four real assets. `pa2.py` calls it automatically if the data files are missing. |
| `msds_getdata_yfinance_bnd.csv`, `..._gld.csv`, `..._spy.csv`, `..._btc-usd.csv` | Daily price history downloaded from Yahoo Finance (January 2015 to December 2025). |
| `pa2-final-report.pdf`, `pa2-final-report.docx` | The research report (PDF and Word versions of the same document). |
| `pa2-output.txt` | Console output from a full run of `pa2.py`. |
| `pa2-estimated-inputs.csv` | Annual mean return and standard deviation estimated for my four assets. |
| `pa2-figure-starter.pdf`, `pa2-figure-starter.png` | Opportunity set plot for the starter assets. |
| `pa2-figure-mine.pdf`, `pa2-figure-mine.png` | Opportunity set plot for my assets. |
| `pa2-returns-starter.csv`, `pa2-returns-mine.csv` | The 700 generated return sets for each run. |
| `pa2-portfolios-starter.csv`, `pa2-portfolios-mine.csv` | Weights, mean return, and risk for all portfolios in each run (700 with shorts allowed and 700 long only). |
| `requirements.txt` | Python packages needed. |
| `starter-monte-carlo.R` | The professor's original R starter code, unchanged. |
| `starter-report.pdf` | The professor's technical report that goes with the starter code. |

## Requirements

- Python 3 (developed and tested on Python 3.14)
- Packages: `numpy`, `pandas`, `matplotlib`, `yfinance` (listed in `requirements.txt`)
- Internet access is only needed to download the price data. The data files are already in the repository, so the program runs offline as long as they are present.

## Setup

From the repository folder, create a virtual environment and install the packages:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On Windows, activate the environment with `.venv\Scripts\activate` instead of the `source` line.

## Running the program

```bash
MPLBACKEND=Agg python pa2.py | tee pa2-output.txt
```

It runs in a few seconds. `MPLBACKEND=Agg` keeps the plot windows from opening, and `tee` saves the console output to `pa2-output.txt` while it prints. Without `MPLBACKEND=Agg`, the program opens the starter code's preliminary plots, and you have to close each window (six in total) for the run to continue. On Windows, set the variable first (`set MPLBACKEND=Agg` in Command Prompt) and leave out `tee`.

If the four `msds_getdata_yfinance_*.csv` files are not in the folder, `pa2.py` runs `getdata_yfinance.py` first to download them. You can also run the download step on its own with `python getdata_yfinance.py`.

For each of the two runs, the program:

- generates 700 sets of returns and prints summary statistics, the target and actual correlation matrices, and the target and actual covariance matrices
- generates 700 random weight sets with shorts allowed, then 700 with long positions only, and prints a summary of the portfolio results for each
- prints the lowest risk and highest return portfolio for each strategy, and how many portfolios had a negative mean return
- draws the opportunity set plot and saves it as a PDF and a PNG
- saves the returns and the portfolio results as CSV files

After both runs it saves and prints the estimated inputs for my four assets. Output files are written to the working directory and overwrite the ones in the repository with identical copies.

## Testing and verifying the program

There is no separate test suite. The program is checked by running it end to end and comparing the outputs.

**1. Full run.** `MPLBACKEND=Agg python pa2.py` (without `tee`) should finish with exit code 0 and print `Run Complete` at the end. Check the exit code with `echo $?` right after it (it should print `0`).

**2. Output files.** After a run, the figure, returns, and portfolios files for both `starter` and `mine` should exist in the folder, along with `pa2-estimated-inputs.csv`.

**3. Reproducibility.** Seeds are fixed (1111 for the returns and 9999 for the weights), so a new run should give the same numbers as `pa2-output.txt` and the same CSV files. The price data files are fixed in the repository. If they are deleted and downloaded again, later prices can change slightly because Yahoo adjusts historical data.

**4. Check the simulated data.** In the output, the actual correlation and covariance matrices of the generated returns should be close to the target matrices (they are never exact with 700 observations), and the sample means should be close to the target means. For my assets, the target values are the estimates printed at the end of the output.

**5. Check the weights.** In either portfolios CSV, `w1 + w2 + w3 + w4` should equal 1 in every row. For the long only rows (`ShortsOK` is `Long Positions Only`), every weight should be positive, and the `Positions` column should say `No Shorts`.

**6. Check the starter run against the professor's figure.** The starter-assets plot should look like Figure 1 in `starter-report.pdf`: long only portfolios stop at a mean return of about 0.17 to 0.19, and the shorts allowed portfolios reach about 0.5. The points will not match exactly, because Python and R use different random number generators.

## Results summary

| Run | Strategy | Lowest risk portfolio (mean, SD) | Highest return portfolio (mean, SD) | Portfolios with negative mean return |
|---|---|---|---|---|
| Starter assets | Long positions only | 0.031, 0.052 | 0.174, 0.185 | 0 of 700 |
| Starter assets | Shorts OK | 0.015, 0.051 | 0.531, 0.762 | 34 of 700 |
| My assets | Long positions only | 0.047, 0.057 | 0.565, 0.473 | 0 of 700 |
| My assets | Shorts OK | 0.028, 0.057 | 2.479, 2.335 | 77 of 700 |

In both runs, allowing short positions opens up much higher returns, but at much higher risk, and it is the only strategy that produces portfolios that lose money on average. Long only portfolios stay in a narrow band of lower risk and lower return. Only 16 of the 700 shorts allowed portfolios happened to have all positive weights in each run.

The inputs for my assets, estimated from daily simple returns and annualized (mean times 252, standard deviation times the square root of 252), are:

| Asset | Mean annual return | Standard deviation |
|---|---|---|
| Bonds (BND) | 0.020 | 0.054 |
| Gold (GLD) | 0.124 | 0.147 |
| SP500 (SPY) | 0.142 | 0.178 |
| Bitcoin (BTC-USD) | 0.738 | 0.668 |

Correlations: Bonds and Gold 0.33, Bonds and SP500 0.11, Bonds and Bitcoin 0.09, Gold and SP500 0.04, Gold and Bitcoin 0.09, SP500 and Bitcoin 0.23.

The sample is January 2, 2015 to December 31, 2025, with 2,765 daily returns. Bitcoin trades every day and the other three only on market days, so only dates where all four have a price are used. Bitcoin's much higher return and risk make it dominate the long only portfolios that hold a lot of it, which is why the plot for my assets looks so different from the starter plot.

## Notes on changes from the starter code

- The starter code is written in R. This is a translation to Python (`numpy` for the random draws and matrix math, `pandas` for the data frames, `matplotlib` for the plots). The steps and variable names follow the starter code.
- The starter script's body now sits inside a `for` loop that runs once for each set of initial conditions.
- For my assets, the means, standard deviations, and correlations come from downloaded price history instead of being typed in.
- Both runs use the same seeds, so both draw the same random weights. Only the asset inputs differ.
- Output file names include the run name (`starter` or `mine`), so the second run does not overwrite the first.
- Added: the lowest risk and highest return portfolio printout, a PNG copy of each plot, and CSV files of the generated returns and portfolio results.
- The plot is styled to look like the starter's ggplot figure (grey panels, white grid lines, two panels by strategy). It is saved at 11 by 6.2 inches (the starter's is 11 by 8.5) so it fits a report page better.
- The return scenarios are drawn with numpy's Cholesky method (`method="cholesky"`). The R starter's `mvrnorm` uses an eigen decomposition. Cholesky gives the same draws on every machine, while numpy's default can vary between machines.

## Report

The research report is `pa2-final-report.pdf` (the same document is in `pa2-final-report.docx`). It describes the problem, the data preparation, the research design, the results for both runs with the two figures, and the limitations. Its numbers come from the outputs in this repository, so they can be checked against `pa2-output.txt`, the CSV files, and the figures.

## Use of AI assistants
I used AI in helping me translate the provided R starter code into a Python script. I also used it to recompute the results independently from the CSV files to confirm the numbers, test the program on scratch copies, and reviewed the repo against the assignment's instructions. Lastly, I used it to reformat my report to look more legible and cleaned up.
