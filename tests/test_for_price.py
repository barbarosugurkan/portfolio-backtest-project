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
        'high': [510.0, 310.0],
        'low': [490.0, 290.0],
        'close': [505.0, 305.0],
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
        'high': np.dtype('float64'),
        'low': np.dtype('float64'),
        'close': np.dtype('float64'),
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
    # Bu veriler hem 03-09-2025 (mevcut) hem de 04-09-2025 (yeni) verilerini içeriyor.

    columns_yf = [
        ('Close', 'BIMAS.IS'), ('High', 'BIMAS.IS'), ('Low', 'BIMAS.IS'), ('Open', 'BIMAS.IS'), ('Volume', 'BIMAS.IS'),
        ('Close', 'THYAO.IS'), ('High', 'THYAO.IS'), ('Low', 'THYAO.IS'), ('Open', 'THYAO.IS'), ('Volume', 'THYAO.IS')
    ]
    data_yf = np.array([
        [529.5, 530.0, 520.0, 530.0, 3811537,  # BIMAS.IS verileri 1. gün
        334.057983, 336.779937, 331.336029, 331.58348, 17815923], # THYAO.IS verileri 1. gün
        [523.5, 530.2, 520.1, 530.5, 3811537,  # BIMAS.IS verileri 2. gün
        339.5, 336.8, 331.336029, 320.5, 17815923] # THYAO.IS verileri 2. gün
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
        "HGDG_TARIH": ["01-09-2025", "01-09-2025","02-09-2025", "02-09-2025"],
        "PD": [3.177000e+11,4.657500e+11,3.177000e+11,4.657500e+11],
        "PD_USD": [7.727708e+09,1.132886e+10,7.727708e+09,1.132886e+10]
    })
    mock_fetch_stock_data.return_value = is_mock_df
    
    ticker_dict = {"BIMAS.IS": 1, "THYAO.IS": 2}

    # ACT:
    result_df = fetch_prices(conn=db_conn, ticker_dict=ticker_dict, start_date='2025-09-01', end_date='2025-09-02')

    # ASSERT:
    # 1. Fonksiyonun bir hata fırlatmadan çalıştığını ve bir DataFrame döndürdüğünü doğrula
    assert not result_df.empty
    
    # 2. Döndürülen DataFrame'in yalnızca yeni tarihi (02-09-2025) içerdiğini doğrula
    expected_dates = [pd.to_datetime('2025-09-02')]
    assert list(result_df['date'].unique()) == expected_dates
    
    # 3. Yalnızca yeni veriyi içerdiğinden emin olmak için satır sayısını kontrol et
    assert result_df.shape[0] == 2  # BIMAS ve THYAO için 1'er satır = toplam 2 satır