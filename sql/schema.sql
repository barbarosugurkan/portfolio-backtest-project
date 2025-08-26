PRAGMA foreign_keys = ON;

-- 1) company
CREATE TABLE IF NOT EXISTS company (
    company_id     INTEGER PRIMARY KEY,
    ticker         TEXT    NOT NULL UNIQUE,
    company_name   TEXT    NOT NULL,
    sector         TEXT,
    created_at     TEXT    DEFAULT (datetime('now'))  -- ISO 8601
);

-- 2) price
CREATE TABLE IF NOT EXISTS price (
    price_id    INTEGER PRIMARY KEY,
    company_id  INTEGER NOT NULL,
    date        TEXT    NOT NULL,                     -- 'YYYY-MM-DD'
    open        REAL    CHECK (open  >= 0),
    close       REAL    CHECK (close >= 0),
    high        REAL    CHECK (high  >= 0),
    low         REAL    CHECK (low   >= 0),
    volume      INTEGER CHECK (volume >= 0),
    FOREIGN KEY (company_id) REFERENCES company(company_id) ON DELETE CASCADE,
    UNIQUE (company_id, date)                          -- aynı güne iki kayıt yok
);

-- 3) financial
CREATE TABLE IF NOT EXISTS financial (
    financial_id     INTEGER PRIMARY KEY,
    company_id       INTEGER NOT NULL,
    date_of_publish  TEXT    NOT NULL,                -- 'YYYY-MM-DD'
    period           TEXT    NOT NULL,                -- örn: '2024Q1' veya '2024-06-30'
    revenue          REAL,
    gross_profit     REAL,
    operating_profit REAL,
    ebitda           REAL,
    net_income       REAL,
    current_assets   REAL,
    fixed_assets     REAL,
    long_term_debt   REAL,
    short_term_debt  REAL,
    gross_debt       REAL,
    net_debt         REAL,
    equity           REAL,
    share_count      INTEGER CHECK (share_count >= 0),
    FOREIGN KEY (company_id) REFERENCES company(company_id) ON DELETE CASCADE,
    UNIQUE (company_id, period)                        -- her dönem bir kayıt
);

-- 4) ratio
CREATE TABLE IF NOT EXISTS ratio (
    ratio_id            INTEGER PRIMARY KEY,
    company_id          INTEGER NOT NULL,
    period              TEXT    NOT NULL,
    date                TEXT,                          -- hesap/çekim tarihi
    current_ratio       REAL,
    debt_to_equity      REAL,
    debt_ratio          REAL,
    net_profit_margin   REAL,
    gross_profit_margin REAL,
    operating_margin    REAL,
    roe                 REAL,
    roa                 REAL,
    roic                REAL,
    asset_turnover      REAL,
    pe                  REAL,
    pb                  REAL,
    ps                  REAL,
    ev_ebitda           REAL,
    dividend_yield      REAL,
    revenue_growth      REAL,
    net_income_growth   REAL,
    eps_growth          REAL,
    dividend_growth     REAL,
    FOREIGN KEY (company_id) REFERENCES company(company_id) ON DELETE CASCADE,
    UNIQUE (company_id, date)                         -- dönem başına tek oran seti
);

-- 5) portfolio
CREATE TABLE IF NOT EXISTS portfolio (
    portfolio_id   INTEGER PRIMARY KEY,
    company_id     INTEGER NOT NULL,
    date_purchased TEXT    NOT NULL,
    shares         INTEGER NOT NULL CHECK (shares > 0),
    purchase_price REAL    NOT NULL CHECK (purchase_price >= 0),
    FOREIGN KEY (company_id) REFERENCES company(company_id)
);

-- temel uygulama logları
CREATE TABLE IF NOT EXISTS app_logs (
    log_id     INTEGER PRIMARY KEY,
    ts         TEXT    DEFAULT (datetime('now')),
    action     TEXT,           -- 'fetch_prices', 'calc_ratios', ...
    level      TEXT,           -- 'INFO','WARN','ERROR'
    message    TEXT
);