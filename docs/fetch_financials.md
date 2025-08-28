# Document: Fetching Financial Data with `isyatirimhisse`

## Overview

The goal of this step was to fetch financials data for stocks from İş Yatırım and insert it into our local SQLite database. Actually, skorKart was selected for this purpose but it is seen that it does not include all the financials that are wanted. About the things I tried, [test_fetch_financials.ipynb](test_fetch_financials.ipynb)) can be checked.

The process of fetching data can be divided into three main parts:

1. Selecting the tickers

2. Fetching the data from isyatirimhisse and cleaning it

3. Inserting the data into the database


## 1. Selecting the tickers

Same principles are used, that were discussed in [fetch_prices.mb](fetch_prices.mb)). There is a dictionary contains tickers as keys and company_id as values.

```
ticker_dict = {"THYAO":1,"BIMAS":2}
```

## 2. Fetching the data from isyatirimhisse and cleaning it

This library also has multiple ticker feature, so multiple data from different stocks can be fetched at the same time. The library gives all the financial information possible.

```
df = fetch_financials(
    symbols=list(ticker_dict.keys()),
    start_year=2025,
    end_year=2025,
    exchange="TRY",
    financial_group='1',
    save_to_excel=False
)
```

The format of the table is converted into our database format:

```
df.drop(['FINANCIAL_ITEM_NAME_TR',"FINANCIAL_ITEM_CODE"], axis=1, inplace=True)  

df_melted = df.melt(
    id_vars=['FINANCIAL_ITEM_NAME_EN', 'SYMBOL'],
    var_name='Period',
    value_name='Value'
)

df_melted['Value'] = pd.to_numeric(df_melted['Value'], errors='coerce')

df_pivoted = df_melted.pivot_table(
    index=['SYMBOL', 'Period'],
    columns='FINANCIAL_ITEM_NAME_EN',
    values='Value'
).reset_index()
df_pivoted.columns.name = None
```

The data cleaning part was quite difficult. Names were different, some data were calculated directly from the data.
Other than that, column names are lowercased, spaces replaced with underscores, renamed to consistent English financial terms (revenue, gross_profit, net_income, etc.).

```
df_pivoted.columns = df_pivoted.columns.str.lower().str.replace(" ","_")
df_pivoted = df_pivoted.rename(columns={'net_sales': 'revenue',"gross_profit_(loss)": "gross_profit","operating_profits":"operating_profit","net_profit_after_taxes":"net_income","long_term_liabilities":"long_term_debt","short_term_liabilities":"short_term_debt","shareholders_equity":"equity"})
df_pivoted['ebitda'] = df_pivoted['operating_profit'] + df_pivoted['depreciation_&_amortization']
df_pivoted['fixed_assets'] = df_pivoted['total_assets'] - df_pivoted['current_assets']
df_pivoted['gross_debt'] = df_pivoted['short-term_financial_loans'] + df_pivoted['long-term_financial_loans']
df_pivoted['net_debt'] = df_pivoted['gross_debt'] - df_pivoted["cash\xa0and\xa0cash\xa0equivalents"]
df_pivoted['company_id'] = df_pivoted['symbol'].map(ticker_dict)
df_pivoted["date_of_publish"] = np.nan

df_pivoted = df_pivoted[['company_id',"period","date_of_publish","revenue","gross_profit","operating_profit","ebitda","net_income","current_assets","fixed_assets","long_term_debt","short_term_debt","gross_debt","net_debt","equity"]]
```

As expected, the API does not provide date of publish for financials. Another way will be thought for this later.

The resulting image looks like this:
![screenshot](images/Ekran görüntüsü 2025-08-29 002219.png)

## 3. Inserting data into the database

I chose to insert the whole dataframe once at the end. 
```
df_pivoted.to_sql('financial', conn, if_exists='append', index=False)
```

Indexes should not be transferred to database since there is a different indexes there, and there should be not problem about the arrangemnet since database matches as long as column names are same.


## Future Improvements:
- Add date_of_publish
- Error handling
isyatirimhisse can return empty DataFrame, this can lead error.
- Ticker dictionary
Company tickers can be taken from database or be stored in csv, etc for scalability.
- Control of data types
- Logging
- Solving duplicate data problem
- Making it more modular by separating it into functions.
- More data validation
