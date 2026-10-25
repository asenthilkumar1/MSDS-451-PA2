#!/usr/bin/env python
# coding: utf-8

# Portfolio Optimization: A Monte Carlo Study

# Starter code (in R) by Tom Miller, June 20, 2025
# Translated to Python and modified by Ashwin Senthilkumar, October 2026

# Monte Carlo Study Showing Portfolio Opportunity Sets

# Generate above 700 random asset allocation sets: 4-by-1 vectors.
# For each set, the four portfolio asset weights must sum to 1.
# So, we generate three and set the fourth so the sum is 1.
# Weights can be negative (indicating a short position in the asset).
# Many sets of weights will be suboptimal.

# Assume multivariate normal distributions of returns
# with means, standard deviations, and correlations
# as specified in the problem setup.

# The study is run twice, once for each set of initial conditions:
#   "starter" = the four assets from the starter code
#   "mine"    = four assets that I picked (a bond fund, gold,
#               a stock index fund, and bitcoin), with means,
#               standard deviations, and correlations estimated
#               from real price history downloaded from Yahoo! Finance
#               by getdata_yfinance.py

import os
import subprocess
import sys
import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt # visualization of the simulation

# number of return sets to generate
sampleSize = 700

# names for the two runs, used in the output file names
studyNames = ["starter", "mine"]

# ----------------------------------------------------------------------
# Initial conditions for run 1: the starter assets A, B, C, and D
# ----------------------------------------------------------------------

# mean returns for portfolio assets A, B, C, and D
starterMeanVector = np.array([0.02, 0.07, 0.15, 0.20])

# standard deviations of returns
starterSDVector = np.array([0.05, 0.12, 0.17, 0.25])

# correlation matrix for the four portfolio assets
starterCorMatrix = np.array([[1, 0.3, 0.3, 0.3],
                             [0.3, 1, 0.6, 0.6],
                             [0.3, 0.6, 1, 0.6],
                             [0.3, 0.6, 0.6, 1]])

# ----------------------------------------------------------------------
# Initial conditions for run 2: my assets, estimated from price history
# ----------------------------------------------------------------------

# Yahoo! Finance tickers and the names used in the output
# (the data files are made by getdata_yfinance.py)
myTickers = ["BND", "GLD", "SPY", "BTC-USD"]
myAssetNames = ["Bonds", "Gold", "SP500", "Bitcoin"]
startfile = "msds_getdata_yfinance_"
tradingDays = 252 # trading days per year, to annualize daily returns

# Read the closing prices for each asset, keep the dates that all four
# have, compute daily returns, and annualize the mean and standard deviation.
def estimateInputs(tickers, assetNames):
    prices = pd.DataFrame()
    for ticker, assetName in zip(tickers, assetNames):
        filename = startfile + ticker.lower() + ".csv"
        if not os.path.exists(filename):
            # pull the price history first if the data files are not here yet
            print("Missing " + filename + ", running getdata_yfinance.py")
            subprocess.run([sys.executable, "getdata_yfinance.py"], check = True)
        priceData = pd.read_csv(filename)
        # keep only the calendar date (the files have a time zone on the date)
        priceData["Date"] = priceData["Date"].str[:10]
        prices[assetName] = priceData.set_index("Date")["Close"]
    prices = prices.dropna() # only dates when all four assets have a price
    dailyReturns = prices.pct_change().dropna()
    meanVector = dailyReturns.mean().to_numpy() * tradingDays
    SDVector = dailyReturns.std().to_numpy() * np.sqrt(tradingDays)
    corMatrix = dailyReturns.corr().to_numpy()
    print("\nPrice history used for my assets:", prices.index[0], "to", prices.index[-1],
        "with", len(dailyReturns), "daily returns")
    return meanVector, SDVector, corMatrix

myMeanVector, mySDVector, myCorMatrix = estimateInputs(myTickers, myAssetNames)

# put the two sets of initial conditions in lists so we can loop over them
assetNamesList = [["A", "B", "C", "D"], myAssetNames]
targetMeanList = [starterMeanVector, myMeanVector]
targetSDList = [starterSDVector, mySDVector]
targetCorList = [starterCorMatrix, myCorMatrix]

# Generate a random sets of weights using
# a uniform distribution from -1 to 1 if
# shortsOK is TRUE. Otherwise use a uniform
# distribution from 0 to 1 with scaling to
# ensure that the weights sum to 1.
def makeWeights(shortsOK):
    if shortsOK:
        threeWeights = rng.uniform(-1, 1, size = 3)
        fourthWeight = 1 - threeWeights.sum() # ensures sum of 1
        return np.append(threeWeights, fourthWeight)
    else:
        initialWeights = rng.uniform(0, 1, size = 4)
        return initialWeights / initialWeights.sum() # ensures sum of 1

# run the whole study once for each set of initial conditions
for istudy in range(2):

    studyName = studyNames[istudy]
    print("\n\n=== Monte Carlo study:", studyName, "assets ===")

    targetMeanVector = targetMeanList[istudy]
    targetSDVector = targetSDList[istudy]
    targetCorMatrix = targetCorList[istudy]

    # compute the covariance matrix
    targetCovMatrix = np.diag(targetSDVector) @ targetCorMatrix @ np.diag(targetSDVector)

    # set seed so results are reproducible across executions
    rng = np.random.default_rng(1111)
    # generate multivariate normal returns
    returnsData = rng.multivariate_normal(mean = targetMeanVector,
                                          cov = targetCovMatrix,
                                          size = sampleSize,
                                          method = "cholesky") # same draws on any machine
    returnsDataFrame = pd.DataFrame(returnsData, columns = assetNamesList[istudy])

    # check statistics from the generated returns data
    print(returnsDataFrame.describe().round(4))

    # check correlation matrix of the generated returns data
    print("\nTarget Correlation of Returns for Generated Data:")
    print(np.round(targetCorMatrix, 4))
    print("\nActual Correlation of Returns in Generated Data:")
    print(returnsDataFrame.corr().round(4))

    # compute covariance matrix for the sample data
    # to be used later in portfolio calculations
    print("\nTarget Covariance of Returns for Generated Data:")
    print(np.round(targetCovMatrix, 4))
    print("\nActual Covariance of Returns in Generated Data:")
    dataCovMatrix = returnsDataFrame.cov().to_numpy()
    print(np.round(dataCovMatrix, 4))

    # generate sets of portfolio weights in shortsOK state
    rng = np.random.default_rng(9999) # set seed so results are reproducible
    weightsMatrix = np.full((sampleSize, 4), np.nan)
    for iset in range(sampleSize):
        weightsMatrix[iset, :] = makeWeights(shortsOK = True)

    # Compute the portfolio return for each set of weights
    # for each set of weights applied to each set of returns,
    # storing calculations in a new data frame for the portfolios.
    portfolioList = []
    for iset in range(sampleSize):
        Positions = 1 # has shorts is 1
        w1 = weightsMatrix[iset, 0]
        w2 = weightsMatrix[iset, 1]
        w3 = weightsMatrix[iset, 2]
        w4 = weightsMatrix[iset, 3]
        if w1 > 0 and w2 > 0 and w3 > 0 and w4 > 0: Positions = 2 # no shorts

        returnVector = weightsMatrix[iset, :] @ returnsData.T
        returnMean = returnVector.mean()
        returnSD = np.sqrt(weightsMatrix[iset, :] @ dataCovMatrix @ weightsMatrix[iset, :])
        portfolioList.append([w1, w2, w3, w4, Positions, returnMean, returnSD])
    portfolioResults = pd.DataFrame(portfolioList,
        columns = ["w1", "w2", "w3", "w4", "Positions", "returnMean", "returnSD"])

    # check portfolio results
    print("\nSummary of portfolio results with short positions allowed:")
    print(portfolioResults.describe().round(4))

    # preliminary plot on console
    plt.scatter(portfolioResults["returnSD"], portfolioResults["returnMean"], s = 6)
    plt.xlabel("returnSD")
    plt.ylabel("returnMean")
    plt.show()

    shortsOKResults = portfolioResults.copy()
    shortsOKResults["ShortsOK"] = "Shorts OK"

    # generate sets of portfolio weights with no shorts allowed
    rng = np.random.default_rng(9999) # set seed so results are reproducible
    weightsMatrix = np.full((sampleSize, 4), np.nan)
    for iset in range(sampleSize):
        weightsMatrix[iset, :] = makeWeights(shortsOK = False)

    # Compute the portfolio return for each set of weights
    # for each set of weights applied to each set of returns,
    # storing calculations in a new data frame for the portfolios.
    portfolioList = []
    for iset in range(sampleSize):
        Positions = 1 # has shorts is 1
        w1 = weightsMatrix[iset, 0]
        w2 = weightsMatrix[iset, 1]
        w3 = weightsMatrix[iset, 2]
        w4 = weightsMatrix[iset, 3]
        if w1 > 0 and w2 > 0 and w3 > 0 and w4 > 0: Positions = 2 # no shorts
        returnVector = weightsMatrix[iset, :] @ returnsData.T
        returnMean = returnVector.mean()
        returnSD = np.sqrt(weightsMatrix[iset, :] @ dataCovMatrix @ weightsMatrix[iset, :])
        portfolioList.append([w1, w2, w3, w4, Positions, returnMean, returnSD])
    portfolioResults = pd.DataFrame(portfolioList,
        columns = ["w1", "w2", "w3", "w4", "Positions", "returnMean", "returnSD"])

    # check portfolio results
    print("\nSummary of portfolio results with long positions only:")
    print(portfolioResults.describe().round(4))

    # preliminary plot on console
    plt.scatter(portfolioResults["returnSD"], portfolioResults["returnMean"], s = 6)
    plt.xlabel("returnSD")
    plt.ylabel("returnMean")
    plt.show()

    noShortsResults = portfolioResults.copy()
    noShortsResults["ShortsOK"] = "Long Positions Only"

    # merge the two data frames
    plottingFrame = pd.concat([shortsOKResults, noShortsResults], ignore_index = True)
    plottingFrame["Positions"] = plottingFrame["Positions"].map({1: "Has Short(s)", 2: "No Shorts"})

    # added: lowest risk and highest return portfolios for each strategy,
    # to use in the write-up
    print("\nLowest risk and highest return portfolios,", studyName, "assets:")
    for strategy in sorted(plottingFrame["ShortsOK"].unique()):
        thisSet = plottingFrame[plottingFrame["ShortsOK"] == strategy]
        columnsToShow = ["w1", "w2", "w3", "w4", "returnMean", "returnSD"]
        print("\n" + strategy)
        print("Lowest risk:")
        print(thisSet.loc[[thisSet["returnSD"].idxmin()], columnsToShow].round(3).to_string(index = False))
        print("Highest return:")
        print(thisSet.loc[[thisSet["returnMean"].idxmax()], columnsToShow].round(3).to_string(index = False))
        print("Portfolios with negative mean return:", int((thisSet["returnMean"] < 0).sum()), "of", len(thisSet))

    # complete plot for both conditions: Shorts Allowed and No Shorts
    fig, axes = plt.subplots(1, 2, figsize = (11, 6.2), sharex = True, sharey = True)
    for ax, strategy in zip(axes, sorted(plottingFrame["ShortsOK"].unique())):
        thisSet = plottingFrame[plottingFrame["ShortsOK"] == strategy]
        for positions, colour in [("Has Short(s)", "red"), ("No Shorts", "darkblue")]:
            subset = thisSet[thisSet["Positions"] == positions]
            ax.scatter(subset["returnSD"], subset["returnMean"], s = 5, c = colour, label = positions)
        ax.set_title(strategy, fontsize = 10)
        ax.set_facecolor("#EBEBEB")
        ax.grid(color = "white")
        ax.set_axisbelow(True)
        for side in ax.spines.values(): side.set_visible(False)
    fig.supxlabel("Risk: Standard Deviation of Portfolio Returns", fontsize = 15)
    fig.supylabel("Return: Mean of Portfolio Returns", fontsize = 15)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, title = "Positions", loc = "center right", markerscale = 2)
    fig.subplots_adjust(right = 0.86)

    # export pdf plot for inclusion in the report, and a png copy
    fig.savefig("pa2-figure-" + studyName + ".pdf")
    fig.savefig("pa2-figure-" + studyName + ".png", dpi = 150)
    plt.show()

    # added: csv files of the data, for the repository
    returnsDataFrame.to_csv("pa2-returns-" + studyName + ".csv", index = False)
    plottingFrame.to_csv("pa2-portfolios-" + studyName + ".csv", index = False)

# added: the inputs estimated for my assets, for the write-up
inputsFrame = pd.DataFrame({"Asset": myAssetNames, "Mean": myMeanVector, "SD": mySDVector})
print("\nInputs estimated from price history for my assets (annualized):")
print(inputsFrame.round(4).to_string(index = False))
print(pd.DataFrame(myCorMatrix, index = myAssetNames, columns = myAssetNames).round(3))
inputsFrame.to_csv("pa2-estimated-inputs.csv", index = False)

print("\nRun Complete")
