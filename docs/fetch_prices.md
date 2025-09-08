# Document: Fetching Price Data with `yfinance`

## Overview

The goal of this step was to fetch daily stock price data from Yahoo Finance and market cap data from isyatirimhisse,then insert it into our local SQLite database. The process can be divided into three main parts:

1. Data Acquisition and Pre-processing

2. Handling Existing Data

3. Inserting and Updating Record


## 1. Data Acquisition and Pre-processing

I had two main options for determining which companies to fetch data for:

- Option A: Query the `company` table in the database and retrieve the list of tickers.

- Option B: Store tickers and their IDs in a dictionary inside the Python script.

- Option C: Store tickers and their IDs in a JSON file.

Since there are about 500 BIST companies and the set of companies we track will be relatively stable, I decided to select option C.

I decided to continue using **yfinance** and **isyatirimhisse** as my primary data sources. I've encapsulated the data fetching and cleaning logic into two separate helper functions:

* **`_fetch_and_process_yf`**: 

I was reviewing the Yfinance official documentation. It describes **multiple ticker download feature** (`yf.download(["BIMAS.IS", "THYAO.IS"], ...)`). This was my first option. However, the resulting dataframe had a multi-level column index that did not align well with the schema of our database. For example:

![screenshot](images/280825.png)

As it can be seen, there were some pandas operations needed to convert this into the format in my database.

On the other hand, the second option was data can be taken ticker by ticker inside a for loop and then concatenated into a final dataframe at the end. This method were easy to code (indeed I did code it, you can check [test_fetch_prices.ipynb](test_fetch_prices.ipynb)).

However, second option was not better for performance and it may exceed API limit at some point in the project. Therefore first option is selected:

```
def _fetch_and_process_yf(ticker_dict: dict, start_date: str, end_date: str):

    tickers = list(ticker_dict.keys())

    try:
        data = yf.download(tickers, start=start_date, end=end_date)
    except Exception as e: 
        print(f"Hata: Veri çekilemedi. Bağlantı sorunu olabilir. Hata detayları: {e}")
        return pd.DataFrame()
    
    if data.empty:
        return pd.DataFrame()

    data.columns = ['_'.join(col).strip() for col in data.columns.values]
    data = data.reset_index()
    data = pd.melt(data, id_vars=['Date'], var_name='ticker_info', value_name='value')
    data[['data_type', 'ticker']] = data['ticker_info'].str.split('_', expand=True)
    data.drop('ticker_info', axis=1, inplace=True)

    data = data.pivot_table(index=['Date', 'ticker'], columns='data_type', values='value').reset_index()
    data.columns.name = None
    data.columns = data.columns.str.lower()
    data['company_id'] = data['ticker'].map(ticker_dict)

    data = data.drop_duplicates(subset=["date", "ticker"], keep="last") # eğer aynı veriden iki tane varsa en sonuncusu kalsın

    return data
```

Error handling parts are also added after the previous version.

* **`_fetch_and_merge_is`**: This function is responsible for fetching market cap data from `isyatirimhisse` and merging it with the DataFrame created by the first function. This modular approach keeps the code clean and allows me to handle each data source independently.

```
def _fetch_and_merge_is(yf_df: pd.DataFrame,ticker_dict: dict, start_date: str, end_date: str):

    tickers = list(ticker_dict.keys())

    start_date_object = datetime.strptime(start_date, "%Y-%m-%d")
    end_date_object = datetime.strptime(end_date, "%Y-%m-%d")

    mc_df = fetch_stock_data(
        symbols=[s[:-3] for s in tickers],
        start_date=start_date_object.strftime("%d-%m-%Y"),
        end_date=end_date_object.strftime("%d-%m-%Y"),
        save_to_excel=False
    )

    expected_cols = ["HGDG_HS_KODU","HGDG_TARIH","PD"]
    if not mc_df.empty and all(col in mc_df.columns for col in expected_cols):
        mc_df = mc_df[expected_cols]
        mc_df = mc_df.rename(columns={"HGDG_HS_KODU": "ticker", "HGDG_TARIH": "date","PD":"market_cap"})
        mc_df["ticker"] = mc_df["ticker"] + ".IS"
        mc_df = mc_df.drop_duplicates(subset=["date", "ticker"], keep="last")

        mc_df['date'] = pd.to_datetime(mc_df['date'])

        merged_df = yf_df.merge(
            mc_df,
            how="left",
            left_on=["ticker", "date"],
            right_on=["ticker", "date"]
        )
    else:
        merged_df = yf_df
        merged_df["market_cap"] = pd.NA

    
    merged_df.drop('ticker', axis=1, inplace=True)

    return merged_df
```

At the end the resulting image looks like this:
![screenshot](images/010925.png)

## 2. Handling Existing Data (Duplicate & Update Logic)

This is a significant improvement over the previous version, where I simply appended new data, which could lead to duplicates. I've now implemented a smart **upsert** (update or insert) logic to ensure data integrity.

Here’s how it works:

1.  I perform a `LEFT` merge between the new data (`final_df`) and the existing data from the database (`existing_data`) using a key of `company_id` and `date`.
2.  I use the `indicator=True` parameter, which is a powerful feature of pandas. It adds a `_merge` column to the merged DataFrame that tells me exactly where each record came from:
    * **`_merge` == 'left_only'**: This means the record is **brand new** and only exists in my fetched data. It's ready to be inserted.
    * **`_merge` == 'both'**: This means the record **already exists** in the database. I must now check if it needs to be updated.

```
    if conn is not None: 
        try:
            # Sadece ilgili tarih aralığını DB’den çek
            query = """
            SELECT *
            FROM price 
            WHERE date BETWEEN ? AND ?
            """
            existing_data = pd.read_sql_query(query, conn, params=[start_date, end_date])
            existing_data['date'] = pd.to_datetime(existing_data['date'])

            merged_df = final_df.merge(
                existing_data,
                on=['company_id', 'date'],
                how='left',
                indicator=True
            )

            if merged_df.empty:
                return pd.DataFrame(), []
```

I filter the merged DataFrame to select only the `left_only` records. This becomes my `new_data_df`, which will be inserted into the database.

```
new_data_df = merged_df[merged_df['_merge'] == 'left_only'].drop(columns=['_merge'])
new_data_df.columns = [col.replace('_x', '') if col.endswith('_x') else col for col in new_data_df.columns]
new_data_df = new_data_df[["date","close","high","low","open","volume","company_id","market_cap"]]
```

For records where `_merge` is `both`, I compare the new values (`_x` columns) with the old values (`_y` columns) to find any discrepancies. I use the `fillna(-1).ne` method for a robust element-wise comparison that handles `NaN` values correctly. If any column value is different for a given row, that row is flagged for an update.

I then check if any column in a given row has a True value using .any(axis=1). This creates a Boolean Series that identifies all the rows where at least one value has changed.

update_df: I use this Boolean Series to filter the main merged_df, keeping only the rows that both exist in the database (_merge == 'both') and have at least one change (row_has_diff). This is my final update_df.

```
update_df = pd.DataFrame()
both_mask = merged_df['_merge'].eq('both')
if both_mask.any():

    new_values = merged_df[['open_x', 'close_x', 'high_x', 'low_x', 'volume_x', 'market_cap_x']]
    new_values.columns = [col.replace('_x', '') if col.endswith('_x') else col for col in new_values.columns]
    old_values = merged_df[['open_y', 'close_y', 'high_y', 'low_y', 'volume_y', 'market_cap_y']]
    old_values.columns = [col.replace('_y', '') if col.endswith('_y') else col for col in old_values.columns]
    diffs = new_values.fillna(-1).ne(old_values.fillna(-1))   
    row_has_diff = diffs.any(axis=1)
    update_df = merged_df[row_has_diff & (merged_df['_merge'] == 'both')]

    update_df.columns = [col.replace('_x', '') if col.endswith('_x') else col for col in update_df.columns]
    update_df = update_df[["date","close","high","low","open","volume","company_id","market_cap"]]

    update_list = [
    (
        float(row.open), float(row.close), float(row.high), float(row.low),
        int(row.volume) if pd.notna(row.volume) else None,
        float(row.market_cap) if pd.notna(row.market_cap) else None,
        int(row.company_id), 
        row.date.strftime('%Y-%m-%d %H:%M:%S')  # string'e çevir
    )
        for row in update_df.itertuples(index=False)
    ]
else:
    update_list = []
```

I also printed warning messages for the cases that data is updated and data already exists. Later these can be switched to logging messages.

```
if not update_df.empty:
    for row in update_df.itertuples(index=False, name=None):
        company_id, dt = row[ update_df.columns.get_loc('company_id') ], row[ update_df.columns.get_loc('date') ]
        print(f"Uyarı: company_id {company_id} için {dt.strftime('%Y-%m-%d')} verisi zaten bulunuyor.")

dups = merged_df[merged_df['_merge'] == 'both']
    if not dups.empty:
        for row in dups.itertuples(index=False, name=None):
            company_id, dt = row[ dups.columns.get_loc('company_id') ], row[ dups.columns.get_loc('date') ]
            print(f"Uyarı: company_id {company_id} için {dt.strftime('%Y-%m-%d')} verisi zaten bulunuyor.")
```

## 3. Inserting and Updating Records

With my data now neatly categorized into new records and updated records, I can handle the database operations separately and efficiently.

* **For New Data**: I use DataFrame.to_sql with if_exists='append' to bulk insert all the new records at once.

* **For Updates**: I've created an update_list of tuples, which contains the new values and the WHERE clause parameters (company_id and date). This list is then used with conn.executemany, which is a highly performant way to execute multiple SQL UPDATE statements in a single batch. This is far more efficient than running a separate SQL query for each record.

```
# To insert new data
new_data_df.to_sql('price', conn, if_exists='append', index=False)

# To update existing data
if update_list:
    conn.executemany(
        "UPDATE price SET open=?, close=?, high=?, low=?, volume=?, market_cap=? "
        "WHERE company_id=? AND date=?",
        update_list
    )
```

## Future Improvements:
- Automating the dates
For now I write the wanted start and end dates manually. The the last date from database can be taken and the data from the last date to today can be written. 
- Logging
- Maybe more error handling
- Test market_cap data deeper
