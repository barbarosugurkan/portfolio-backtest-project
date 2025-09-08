import sqlite3
import pandas as pd
import yfinance as yf
import json
import os
from isyatirimhisse import fetch_stock_data
from datetime import datetime

# yf verilerini çekip işleyen fonksiyon
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

# isyatirimhisse'den gelen market_cap verisini ekleyen fonksiyon
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
    

def _get_ticker_dict() -> dict:
    """Proje kök dizinindeki config klasöründen ticker sözlüğünü okur."""
    
    # Mevcut dosyanın (fetch_prices.py) dizinini bulur
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Bir seviye yukarı çıkarak proje kök dizinine ulaşır
    project_root = os.path.dirname(current_dir)
    
    # JSON dosyasının tam yolunu oluşturur
    json_path = os.path.join(project_root, 'config', "ticker_dict.json")
    
    # Dosyayı açar ve veriyi okur
    try:
        with open(json_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Hata: Konfigürasyon dosyası bulunamadı. Lütfen '{json_path}' adresini kontrol edin.")
        return {}
    

def fetch_prices(conn, ticker_dict: dict, start_date: str, end_date: str):
    yfinance_df = _fetch_and_process_yf(ticker_dict, start_date, end_date)
    if yfinance_df.empty:
        print("yfinance'ten veri alınamadı. İşlem durduruldu.")
        return pd.DataFrame()

    final_df = _fetch_and_merge_is(yfinance_df, ticker_dict, start_date, end_date)

    # -----------------------------------------------------------
    # Bu koyacağımız veri database'de zaten var mı ona bakacağız.
    # -----------------------------------------------------------
    if conn is not None: # bu kısım testlerde conn'un None olduğu durumları engellemek için
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

            # indicator=True → yeni bir _merge kolonu ekleniyor:
            # "left_only" → sadece final_df’de var, DB’de yok (yeni kayıt).
            # "both" → hem final_df hem DB’de var (duplicate).

            # Uyarı mesajı
            dups = merged_df[merged_df['_merge'] == 'both']
            if not dups.empty:
                for row in dups.itertuples(index=False, name=None):
                    company_id, dt = row[ dups.columns.get_loc('company_id') ], row[ dups.columns.get_loc('date') ]
                    print(f"Uyarı: company_id {company_id} için {dt.strftime('%Y-%m-%d')} verisi zaten bulunuyor.")



            # burada sadece yeni güne ait veriler var
            new_data_df = merged_df[merged_df['_merge'] == 'left_only'].drop(columns=['_merge'])
            new_data_df.columns = [col.replace('_x', '') if col.endswith('_x') else col for col in new_data_df.columns]
            new_data_df = new_data_df[["date","close","high","low","open","volume","company_id","market_cap"]]

            update_df = pd.DataFrame()
            both_mask = merged_df['_merge'].eq('both')
            if both_mask.any():

                # bu kısımda ise daha önceden olan ancak değişmiş verileri değiştireceğiz
                new_values = merged_df[['open_x', 'close_x', 'high_x', 'low_x', 'volume_x', 'market_cap_x']]
                new_values.columns = [col.replace('_x', '') if col.endswith('_x') else col for col in new_values.columns]
                old_values = merged_df[['open_y', 'close_y', 'high_y', 'low_y', 'volume_y', 'market_cap_y']]
                old_values.columns = [col.replace('_y', '') if col.endswith('_y') else col for col in old_values.columns]
                diffs = new_values.fillna(-1).ne(old_values.fillna(-1))   # element bazlı karşılaştırma (True/False)
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


            # Değişenler için uyarı mesajları
            if not update_df.empty:
                for row in update_df.itertuples(index=False, name=None):
                    company_id, dt = row[ update_df.columns.get_loc('company_id') ], row[ update_df.columns.get_loc('date') ]
                    print(f"Uyarı: company_id {company_id} için {dt.strftime('%Y-%m-%d')} verisi zaten bulunuyor.")


        except Exception as e:
            print(f"Hata: Veritabanından mevcut veri çekilemedi. İşlem durduruldu: {e}")
            return pd.DataFrame()
        
    else: 
        # conn'un none olma durumu (testler için önemli)
        return final_df.drop_duplicates(subset=["date", "company_id"], keep="last")

    return new_data_df.drop_duplicates(subset=["date", "company_id"], keep="last"),update_list



if __name__ == "__main__":
    db_path = "C:/Users/KULLANICI/Desktop/portfolio-backtest-project/data/database.db"

    ticker_dict = _get_ticker_dict()
    start_date = '2025-08-20'
    end_date = '2025-09-03'

    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA journal_mode=WAL;")

        new_data_df,update_list = fetch_prices(conn,ticker_dict,start_date,end_date)
        
        new_data_df.to_sql('price', conn, if_exists='append', index=False)

        if update_list:
            conn.executemany(
                "UPDATE price SET open=?, close=?, high=?, low=?, volume=?, market_cap=? "
                "WHERE company_id=? AND date=?",
                update_list
            )

    print("Price fetch completed.")