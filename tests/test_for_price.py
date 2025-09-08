import sys
import os

# Projenin kök dizinini Python'ın arama yoluna ekle
# Bu, 'tests' klasörünün bir üst dizinidir
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime
from unittest.mock import patch, MagicMock

# Test edilecek fonksiyonu import et
from src.fetch_prices import fetch_prices

# Bu test için geçici bir veritabanı dosyası oluşturun
@pytest.fixture
def db_conn():
    conn = sqlite3.connect(':memory:')  # Bellekte geçici bir veritabanı oluştur

    conn.execute("""
        CREATE TABLE IF NOT EXISTS price (
            price_id    INTEGER PRIMARY KEY,
            company_id  INTEGER NOT NULL,
            date        TEXT    NOT NULL,              
            open        REAL    CHECK (open  >= 0),
            close       REAL    CHECK (close >= 0),
            high        REAL    CHECK (high  >= 0),
            low         REAL    CHECK (low   >= 0),
            volume      INTEGER CHECK (volume >= 0),
            market_cap REAL,
            FOREIGN KEY (company_id) REFERENCES company(company_id) ON DELETE CASCADE,
            UNIQUE (company_id, date)
            )"""
        )
    yield conn
    conn.close()

@pytest.fixture
def mock_yfinance_data():
    columns_yf = [
        ('Close', 'BIMAS.IS'), ('High', 'BIMAS.IS'), ('Low', 'BIMAS.IS'), ('Open', 'BIMAS.IS'), ('Volume', 'BIMAS.IS'),
        ('Close', 'THYAO.IS'), ('High', 'THYAO.IS'), ('Low', 'THYAO.IS'), ('Open', 'THYAO.IS'), ('Volume', 'THYAO.IS')
    ]
    data_yf = np.array([
        [529.5, 530.0, 520.0, 530.0, 3811537,  # BIMAS.IS verileri
        334.057983, 336.779937, 331.336029, 331.58348, 17815923] # THYAO.IS verileri
    ]) 
    mock_df_yf = pd.DataFrame(
        data_yf,
        columns=pd.MultiIndex.from_tuples(columns_yf),
        index=pd.to_datetime(['2025-09-01'])
    )

    # Sütun dizinlerine isim ver
    mock_df_yf.index.name = 'Date'

    return mock_df_yf

@pytest.fixture
def mock_db_data():
    """Veritabanında önceden var olan veriyi simüle eder."""
    # 2025-09-01 tarihli BIMAS.IS ve THYAO.IS verisini temsil eden DataFrame
    data = {
        'date': [pd.to_datetime('2025-09-01'), pd.to_datetime('2025-09-01')],
        'open': [500.0, 300.0],
        'close': [505.0, 305.0],
        'high': [510.0, 310.0],
        'low': [490.0, 290.0],
        'volume': [1000, 2000],
        'market_cap': [1.0, 2.0],
        'company_id': [1, 2]
    }
    return pd.DataFrame(data)


@pytest.fixture
def mock_is_data():
    # isyatirimhisse'den gelecek sahte veri
    mock_df_is = pd.DataFrame({
        "HGDG_HS_KODU": ["BIMAS","THYAO"],
        "HGDG_TARIH": ["2025-09-01","2025-09-01"],
        "PD": [3.177000e+11,4.657500e+11],
        "PD_USD": [7.727708e+09,1.132886e+10]
    })

    mock_df_is['HGDG_TARIH'] = pd.to_datetime(mock_df_is['HGDG_TARIH'])

    return mock_df_is

@pytest.fixture
def default_params():
    return {
        "ticker_dict": {"BIMAS.IS": 1, "THYAO.IS": 2},
        "start_date": "2025-09-01",
        "end_date": "2025-09-02",
        "conn": None
    }


@patch('src.fetch_prices.fetch_stock_data')
@patch('src.fetch_prices.yf.download')
def test_fetch_prices_happy_path(mock_yf_download, mock_fetch_stock_data,mock_yfinance_data,mock_is_data, default_params):
    """
    Dış servisler düzgün veri döndürdüğünde, fonksiyonun veriyi doğru bir şekilde
    işleyip, beklenen yapıda bir DataFrame döndürdüğünü test eder.
    """
    
    mock_yf_download.return_value = mock_yfinance_data

    mock_fetch_stock_data.return_value = mock_is_data

    # ACT: Asıl fonksiyonumuzu çağırıyoruz.
    # conn argümanı şu anki testte önemli olmadığı için sahte bir nesne (None) yollayabiliriz.
    result_df = fetch_prices(**default_params)

    # ASSERT: Çıktının doğruluğunu kontrol ediyoruz.
    assert not result_df.empty
    assert result_df.shape[0] == 2  # Sadece 1 satır veri bekliyoruz
    assert 'market_cap' in result_df.columns
    assert 'close' in result_df.columns # Sütun adlarının küçültüldüğünü kontrol et
    assert result_df['company_id'].iloc[0] == 1 # ticker_dict map'inin çalıştığını kontrol et
    assert result_df['market_cap'].iloc[0] == 3.177000e+11

    # --- YENİ VERİ TİPİ KONTROLLERİ ---
    expected_dtypes = {
        'date': 'datetime64[ns]',
        'open': np.dtype('float64'),
        'close': np.dtype('float64'),
        'high': np.dtype('float64'),
        'low': np.dtype('float64'),
        'volume': np.dtype('float64'),
        'market_cap': np.dtype('float64'),
        'company_id': np.dtype('int64')
    }
    
    # Her sütunun beklenen veri tipinde olduğunu doğrula
    for col, expected_dtype in expected_dtypes.items():
        assert result_df[col].dtype == expected_dtype, f"Sütun '{col}' için beklenen tip {expected_dtype} ama gelen tip {result_df[col].dtype}"

@patch('src.fetch_prices.fetch_stock_data')
@patch('src.fetch_prices.yf.download')
def test_fetch_prices_when_yfinance_returns_empty(mock_yf_download, mock_fetch_stock_data, default_params):
    """
    yfinance boş DataFrame döndürdüğünde fonksiyonun çökmediğini ve 
    boş bir sonuç ürettiğini test eder.
    """
    mock_yf_download.return_value = pd.DataFrame() # yfinance boş veri döndürdü
    mock_fetch_stock_data.return_value = pd.DataFrame() # Diğer servis de boş dönsün

    result_df = fetch_prices(**default_params)

    assert result_df.empty


@patch('src.fetch_prices.fetch_stock_data')
@patch('src.fetch_prices.yf.download')
def test_fetch_prices_merge_mismatch(mock_yf_download, mock_fetch_stock_data,mock_yfinance_data, default_params):
    """
    Fiyat verisi olan ama piyasa değeri verisi olmayan bir gün için merge işleminin
    doğru çalıştığını ve market_cap'in NaN olduğunu test eder.
    """

    mock_yf_download.return_value = mock_yfinance_data
    
    # isyatirimhisse o gün için veri döndürmedi
    mock_fetch_stock_data.return_value = pd.DataFrame(columns=["HGDG_HS_KODU", "HGDG_TARIH", "PD"])

    # ACT
    result_df = fetch_prices(**default_params)

    # ASSERT
    # `how='left'` merge yapıldığı için satır silinmemeli ama market_cap NaN olmalı
    assert result_df.shape[0] == 2
    assert pd.isna(result_df['market_cap'].iloc[0])

@patch('src.fetch_prices.fetch_stock_data')
@patch('src.fetch_prices.yf.download')
def test_fetch_prices_handles_connection_error(mock_yf_download, mock_fetch_stock_data, default_params):
    """
    yfinance bağlantı hatası fırlattığında, fonksiyonun çökmeden boş bir DataFrame
    döndürdüğünü test eder.
    """
    mock_yf_download.side_effect = ConnectionError("İnternet bağlantısı yok!")

    result_df = fetch_prices(**default_params)

    assert isinstance(result_df, pd.DataFrame)
    
    assert result_df.empty

@patch('src.fetch_prices.yf.download')
@patch('src.fetch_prices.fetch_stock_data')
def test_partial_ticker_success_from_yfinance(mock_fetch_stock_data, mock_yf_download, default_params):
    """
    İstenen ticker listesinden sadece bir kısmı için veri geldiğinde
    fonksiyonun hata vermeden çalıştığını test eder.
    """
    # ARRANGE: yfinance sadece BIMAS için veri döndürsün, THYAO için döndürmesin.
    columns_yf = [
        ('Close', 'BIMAS.IS'), ('High', 'BIMAS.IS'), ('Low', 'BIMAS.IS'), ('Open', 'BIMAS.IS'), ('Volume', 'BIMAS.IS'),
    ]
    data_yf = np.array([
        [529.5, 530.0, 520.0, 530.0, 3811537,]  # BIMAS.IS verileri
    ]) 
    mock_df_yf = pd.DataFrame(
        data_yf,
        columns=pd.MultiIndex.from_tuples(columns_yf),
        index=pd.to_datetime(['2025-09-01'])
    )
    mock_df_yf.index.name = 'Date'

    mock_yf_download.return_value = mock_df_yf

    mock_fetch_stock_data.return_value = pd.DataFrame()

    result_df = fetch_prices(**default_params)

    # ASSERT
    # Sonuçta sadece BIMAS.IS'e ait veriler olmalı
    assert not result_df.empty
    unique_company_id = result_df['company_id'].unique() 
    assert 1 in unique_company_id
    assert 2 not in unique_company_id
    # Veya daha basiti, company_id üzerinden kontrol
    assert result_df['company_id'].unique().tolist() == [1] 


@patch('src.fetch_prices.yf.download')
@patch('src.fetch_prices.fetch_stock_data')
def test_handles_duplicate_input_data(mock_fetch_stock_data, mock_yf_download,default_params):
    """
    Girdi verisinde mükerrer satırlar olduğunda, çıktının nasıl davrandığını test eder.
    (İdeal olarak, mükerrer satırlar temizlenmelidir.)
    """
    # ARRANGE: Aynı gün için iki aynı satırı içeren veri
    columns_yf = [
        ('Close', 'BIMAS.IS'), ('High', 'BIMAS.IS'), ('Low', 'BIMAS.IS'), ('Open', 'BIMAS.IS'), ('Volume', 'BIMAS.IS')
    ]
    data_yf = np.array([
        [529.5, 530.0, 520.0, 530.0, 3811537], [529.5, 530.0, 520.0, 530.0, 3811537]  
    ]) 
    mock_df_yf = pd.DataFrame(
        data_yf,
        columns=pd.MultiIndex.from_tuples(columns_yf),
        index=pd.to_datetime(['2025-09-01','2025-09-01'])
    )
    mock_df_yf.index.name = 'Date'

    mock_yf_download.return_value = mock_df_yf

    mock_fetch_stock_data.return_value = pd.DataFrame()

    # ACT
    result_df = fetch_prices(**default_params)

    # ASSERT
    assert result_df.shape[0] == 1


@patch('src.fetch_prices.yf.download')
@patch('src.fetch_prices.fetch_stock_data')
def test_large_dataset(mock_fetch_stock_data, mock_yf_download):

    # Büyük mock dataset hazırlama
    tickers = [f"TICK{i}.IS" for i in range(100)]  # 100 ticker
    dates = pd.date_range("2025-01-01", "2025-01-10")  # 10 günlük veri
    columns_yf = [(col, ticker) for ticker in tickers for col in ['Close','High','Low','Open','Volume']]

    data_yf = np.random.rand(len(dates), len(columns_yf)) * 1000  # random fiyatlar

    mock_df_yf = pd.DataFrame(data_yf, columns=pd.MultiIndex.from_tuples(columns_yf), index=dates)
    mock_df_yf.index.name = 'Date'

    # Market cap mock verisi
    mock_mc_data = pd.DataFrame({
        "HGDG_HS_KODU": [t[:-3] for t in tickers for _ in range(len(dates))],
        "HGDG_TARIH": list(dates) * len(tickers),
        "PD": np.random.rand(len(tickers)*len(dates))*1e9
    })
    mock_mc_data["HGDG_TARIH"] = pd.to_datetime(mock_mc_data["HGDG_TARIH"])

    ticker_dict = {t: i+1 for i, t in enumerate(tickers)}

    mock_yf_download.return_value = mock_df_yf
    mock_fetch_stock_data.return_value = mock_mc_data

    df = fetch_prices(conn=None, ticker_dict=ticker_dict, start_date="2025-01-01", end_date="2025-01-10")
    
    # Basit assertler
    assert not df.empty
    assert "market_cap" in df.columns
    assert df.shape[0] > 100  # çok sayıda satır olması lazım


@patch('src.fetch_prices.fetch_stock_data')
@patch('src.fetch_prices.yf.download')
def test_fetch_prices_handles_existing_data(mock_yf_download, mock_fetch_stock_data, mock_db_data, db_conn):
    """
    Veritabanında zaten mevcut olan verilerle yeni verilerin birleştirilmesini test eder.
    Sadece yeni verilerin eklendiğini doğrular.
    """
    # ARRANGE:
    # 1. Veritabanına önceden var olan veriyi ekle
    mock_db_data.to_sql('price', db_conn, if_exists='append', index=False)
    
    # 2. yfinance ve isyatirim'dan gelecek verileri simüle et.
    # Bu veriler hem 01-09-2025 (mevcut) hem de 02-09-2025 (yeni) verilerini içeriyor.

    columns_yf = [
        ('Close', 'BIMAS.IS'), ('High', 'BIMAS.IS'), ('Low', 'BIMAS.IS'), ('Open', 'BIMAS.IS'), ('Volume', 'BIMAS.IS'),
        ('Close', 'THYAO.IS'), ('High', 'THYAO.IS'), ('Low', 'THYAO.IS'), ('Open', 'THYAO.IS'), ('Volume', 'THYAO.IS')
    ]

    data_yf = np.array([
        [505.0, 510.0, 490.0, 490.0, 1000,  # BIMAS.IS verileri 1. gün
        305.0, 310.0, 290.0, 300.0, 2000], # THYAO.IS verileri 1. gün
        [523.5, 530.2, 520.1, 530.5, 1500,  # BIMAS.IS verileri 2. gün
        339.5, 336.8, 331.3, 320.5, 2500] # THYAO.IS verileri 2. gün
    ]) 
    mock_df_yf = pd.DataFrame(
        data_yf,
        columns=pd.MultiIndex.from_tuples(columns_yf),
        index=pd.to_datetime(['2025-09-01','2025-09-02'])
    )

    # Sütun dizinlerine isim ver
    mock_df_yf.index.name = 'Date'


    mock_yf_download.return_value = mock_df_yf
    
    is_mock_df = pd.DataFrame({
        "HGDG_HS_KODU": ["BIMAS", "THYAO","BIMAS","THYAO"],
        "HGDG_TARIH": pd.to_datetime(["2025-09-01", "2025-09-01","2025-09-02", "2025-09-02"]),
        "PD": [1.0,2.0,1.5,2.5],
        "PD_USD": [7.727708e+09,1.132886e+10,7.727708e+09,1.132886e+10]
    })
    mock_fetch_stock_data.return_value = is_mock_df
    
    ticker_dict = {"BIMAS.IS": 1, "THYAO.IS": 2}

    # ACT:
    yeni_eklenecekler_df,update_list = fetch_prices(conn=db_conn, ticker_dict=ticker_dict, start_date='2025-09-01', end_date='2025-09-02')

    # 1. Yeni verileri veritabanına ekle
    yeni_eklenecekler_df.to_sql('price', db_conn, if_exists='append', index=False)
    
    # 2. Güncelleme listesi varsa, veritabanını güncelle
    if update_list:
        db_conn.executemany(
            "UPDATE price SET open=?, close=?, high=?, low=?, volume=?, market_cap=? WHERE company_id=? AND date=?",
            update_list
        )

    # ASSERT:
    # 1. Fonksiyonun bir hata fırlatmadan çalıştığını ve bir DataFrame döndürdüğünü doğrula
    assert not yeni_eklenecekler_df.empty
    
    # 2. Döndürülen DataFrame'in yalnızca yeni tarihi (02-09-2025) içerdiğini doğrula
    expected_dates = [pd.to_datetime('2025-09-02')]
    assert list(yeni_eklenecekler_df['date'].unique()) == expected_dates
    
    # 3. Yalnızca yeni veriyi içerdiğinden emin olmak için satır sayısını kontrol et
    assert yeni_eklenecekler_df.shape[0] == 2  # BIMAS ve THYAO için 1'er satır = toplam 2 satır

    # 4. Update_list içinde ilk günün BIMAS verileri olmalı
    assert len(update_list) == 1

    # 5. Update list içeriği doğru mu?
    assert update_list[0] == (490.0,505.0,510.0,490.0,1000,1.0,1,"2025-09-01 00:00:00")

    # 6. En son database'de yeterince veri var mı?
    final_db_df = pd.read_sql_query("SELECT * FROM price ORDER BY date", db_conn)
    assert final_db_df.shape[0] == 4


def test_data_validation(db_conn):
    ticker_dict = {
        "BIMAS.IS":1,
        "THYAO.IS":2,
        "HTTBT.IS":3,
        "AKFYE.IS":4,
        "CEMTS.IS":5,
    }
    db_df,update_list = fetch_prices(db_conn,ticker_dict,"2022-09-01","2025-09-01")

    ground_truth_df = pd.DataFrame(
        {
        'date': [pd.to_datetime('2024-07-26'), pd.to_datetime('2023-10-12'),pd.to_datetime('2024-08-05'),pd.to_datetime('2024-02-06'), pd.to_datetime('2023-08-02')],
        'open': [599.0, 228.2, 27.40, 20.38, 10.72],
        'close': [598.0, 219.9, 28.48, 21.50, 10.72],
        'high': [603.5, 229.6, 30.14, 21.70, 10.85],
        'low': [596.0, 213.6, 27.40, 20.14, 10.59],
        'volume': [1.69e+06, 37.19e+06, 619.60e+03, 19.82e+06, 13.52e+06],
        'market_cap': [363105600000, 303462000000, 8544000000, 21844000000, 5360000000],
        'company_id': [1, 2, 3, 4, 5]
        }
    )
    
    # ground_truth_df'den (tarih, şirket_id) çiftlerini al
    date_id_pairs = list(zip(ground_truth_df['date'], ground_truth_df['company_id']))

    # db_df'i filtrele
    db_df = db_df[
        db_df.apply(lambda row: (row['date'], row['company_id']) in date_id_pairs, axis=1)
    ]
    
    # Fiyat ve hacim sütunlarını sayısal tiplere dönüştür
    for col in ['open', 'close', 'high', 'low', 'volume', 'market_cap']:
        db_df[col] = pd.to_numeric(db_df[col], errors='coerce')
    # Date verisini datetime yap
    db_df["date"] = pd.to_datetime(db_df["date"])

    # Her iki DataFrame'i de date ve company_id sütunlarına göre sırala
    db_df = db_df.sort_values(by=['date', 'company_id']).reset_index(drop=True)
    ground_truth_df = ground_truth_df.sort_values(by=['date', 'company_id']).reset_index(drop=True)

    assert db_df.shape[0] == ground_truth_df.shape[0], "Karşılaştırma için DataFrame'lerin satır sayıları uyuşmuyor."

    # Fiyat verilerini (açılış, kapanış, yüksek, düşük) karşılaştır. %1 sapma potansiyeli olsun.
    for col in ['open', 'close', 'high', 'low']:
        # Hacim verilerini %1 sapma toleransıyla karşılaştır
        diff_percentage = np.abs(db_df[col] - ground_truth_df[col]) / ground_truth_df[col]
        for idx, pct_diff in enumerate(diff_percentage):
            assert pct_diff < 0.01, f"{ground_truth_df.iloc[idx]['date'].strftime('%Y-%m-%d')} tarihli ve {ground_truth_df.iloc[idx]['company_id']} company_id'sine sahip {col} verisi doğrulaması başarısız. Sapma: {pct_diff:.2%} (Beklenen: <1%)"


    # Hacim verilerini %5 sapma toleransıyla karşılaştır
    volume_diff_percentage = np.abs(db_df['volume'] - ground_truth_df['volume']) / ground_truth_df['volume']
    for idx, pct_diff in enumerate(volume_diff_percentage):
        assert pct_diff < 0.05, f"{ground_truth_df.iloc[idx]['date'].strftime('%Y-%m-%d')} tarihli ve {ground_truth_df.iloc[idx]['company_id']} company_id'sine sahip volume verisi doğrulaması başarısız. Sapma: {pct_diff:.2%} (Beklenen: <5%)"

    # Market Cap verisini (market_cap) %5 sapma toleransıyla karşılaştır
    market_cap_diff_percentage = np.abs(db_df['market_cap'] - ground_truth_df['market_cap']) / ground_truth_df['market_cap']
    # Testin başarısız olması durumunda, sapma miktarını görmek için bir döngü ekleyebilirsin
    for idx, pct_diff in enumerate(market_cap_diff_percentage):
        assert pct_diff < 0.05, f"{ground_truth_df.iloc[idx]['date'].strftime('%Y-%m-%d')} tarihli ve {ground_truth_df.iloc[idx]['company_id']} company_id'sine sahip market cap verisi doğrulaması başarısız. Sapma: {pct_diff:.2%} (Beklenen: <5%)"
