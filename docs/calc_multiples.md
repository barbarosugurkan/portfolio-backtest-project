# Document: Calculating Multiples from Financial and Price Table

## Overview

`calc_multiples.py` is a Python script designed to merge daily stock price data with quarterly financial statements to calculate key valuation multiples (e.g., P/E, P/B, P/S). The script reads data from a local SQLite database, performs the necessary calculations and data cleaning, and writes the final dataset to a new table.

For test document please check: [test_calc_multiples.ipynb](test_calc_multiples.ipynb)

This process can be divided into smaller parts: 

1) Get the market cap data which is related to price table and get financial data

2) Match these two data

3) Do data cleaning and calculate multiples

## 1. Getting the market cap and financial data

When I started coding calc_multiples.py, neither financial nor price table include market cap or stock count data, please check [fetch_prices.md](fetch_prices.md) or [../adr/0010-integrate_market_cap_or_share_count_data.md](adr file for this). Right now price table include market cap data, too. So that data is fetched.

Financial did include all the data wanted except growth data, which is in ratio table. I decided not to take ratio table just for one data calculated it in the script then from financial data.

## 2. Match these two data

This is the second challenging part. It was hard to align a daily time series (stock prices) with a quarterly time series (financials). A simple merge based on a common date isn't feasible because the price data changes every day, while financial data only changes once a quarter.

There was two options I found: 

1. "As-of" Merge

The initial approach used pd.merge_asof because it's the most appropriate tool for this task. It matches each stock price to the most recent financial data point available. However, a series of persistent errors with merge_asof's by parameter led us to a different solution. In order not get bored of from the project, another solution was used.

2. Manual "As-of" Logic with pd.merge()

To solve the merge_asof error, we adopted a different strategy: a traditional pd.merge() based on a calculated "effective" date.

- Why this works: We decided to create a new effective_quarter_end column in the price_df. This column assumes a 45-day delay for financial report releases. This means that all the financials for Q1 of 2025 are released in 16 May 2025 and used for 3 months until 14 August 2025, in 15 August 2025 financials for Q2 of 2025 are released, and so on. Amount of delays after quarter ends are checked and 45 was an ideal number.

- Why we chose this: This method ensures a direct, one-to-one match for every row, avoiding the complexities and errors we encountered with merge_asof. While this approach is based on a fixed assumption, it provides a stable and reliable foundation for the rest of the calculations.

However, it has some flaws for example, let's assume that today is 1 May and Q1 financials are released. The system is not dynamic so multiples are calculated from previous data.

Here are the codes for this section:

```
price_df["date"] = pd.to_datetime(price_df["date"])

price_df["effective_quarter_end"] = (price_df["date"] - pd.Timedelta(days=45)) + pd.offsets.QuarterEnd(-1)

fin_df["period_end"] = pd.to_datetime(
    fin_df["period_year"].astype(str) + "-" + fin_df["period_month"].astype(str) + "-01"
) + pd.offsets.MonthEnd(0)

merged_df = price_df.merge(
    fin_df,
    left_on=["company_id", "effective_quarter_end"],
    right_on=["company_id", "period_end"],
    how="left"
)
```

## 3. Data cleaning and calculations

Trailing twelve month data are used for pe, ps, ev/ebitda and dividend yield multiples as expected. However, in the peg ratio contrary to the literature I used net income growth instead of eps growth. The reason behind this is that most of the financials do not include eps directly. This can be considered later.

```
merged_df = merged_df.rename(columns={"date":"date_of_price"})
merged_df["pe"] = merged_df["market_cap"] / merged_df["net_income_ttm"]
merged_df["pb"] = merged_df["market_cap"] / merged_df["equity"]
merged_df["ps"] = merged_df["market_cap"] / merged_df["revenue_ttm"]
merged_df["ev_ebitda"] = (merged_df['market_cap'] + merged_df['gross_debt'] - merged_df['cash_and_cash_equivalents']) / merged_df["ebitda_ttm"]
merged_df["dividend_yield"] = merged_df["dividend_ttm"] / merged_df["market_cap"]


merged_df["peg"] = merged_df["pe"] / merged_df["net_income_growth_ttm_yoy"] / 100


merged_df = merged_df[["company_id","date_of_price","period_year","period_month","pe","pb","ps","ev_ebitda","dividend_yield","peg"]]
```

## Future improvements: 
- Dynamic matching with date of publish data
- Add more ratios
- Solve the problem with peg ratio
- Error handling