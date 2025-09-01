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
    market_cap REAL,
    FOREIGN KEY (company_id) REFERENCES company(company_id) ON DELETE CASCADE,
    UNIQUE (company_id, date)                          -- aynı güne iki kayıt yok
);

-- 3) financial
CREATE TABLE IF NOT EXISTS financial (
    financial_id     INTEGER PRIMARY KEY,
    company_id       INTEGER NOT NULL,
    date_of_publish  TEXT,               
    period_year      TEXT    NOT NULL,
    period_month     TEXT    NOT NULL,          
    revenue_ttm         REAL,
    gross_profit_ttm     REAL,
    operating_profit_ttm REAL,
    ebitda_ttm          REAL,
    net_income_ttm       REAL,
    revenue_q         REAL,
    gross_profit_q     REAL,
    operating_profit_q REAL,
    ebitda_q           REAL,
    net_income_q       REAL,
    revenue_c         REAL,
    gross_profit_c     REAL,
    operating_profit_c REAL,
    ebitda_c           REAL,
    net_income_c       REAL,
    effective_tax_rate_ttm REAL,
    current_assets   REAL,
    fixed_assets     REAL,
    long_term_debt   REAL,
    short_term_debt  REAL,
    gross_debt       REAL,
    net_debt         REAL,
    equity           REAL,
    eps_c            REAL,
    eps_q            REAL,
    eps_ttm            REAL,
    FOREIGN KEY (company_id) REFERENCES company(company_id) ON DELETE CASCADE,
    UNIQUE (company_id, period_year,period_month)                        -- her dönem bir kayıt
);

-- 4) ratio
CREATE TABLE IF NOT EXISTS ratio (
    ratio_id            INTEGER PRIMARY KEY,
    company_id          INTEGER NOT NULL,
    period_year         TEXT    NOT NULL,
    period_month        TEXT    NOT NULL,
    date_of_publish     TEXT,                          
    current_ratio       REAL,
    debt_to_equity      REAL,
    debt_to_assets      REAL,
    debt_to_ebitda      REAL,
    net_income_margin_ttm   REAL,
    gross_profit_margin_ttm REAL,
    operating_margin_ttm    REAL,
    net_income_margin_q   REAL,
    gross_profit_margin_q REAL,
    operating_margin_q    REAL,
    net_income_margin_c   REAL,
    gross_profit_margin_c REAL,
    operating_margin_c    REAL,
    roe_ttm                 REAL,
    roe_q                 REAL,
    roa_ttm                 REAL,
    roa_q                 REAL,
    roic_ttm                REAL,
    asset_turnover      REAL,
    revenue_growth_ttm_yoy      REAL,
    revenue_growth_q_yoy      REAL,
    revenue_growth_q_qoq      REAL,
    net_income_growth_ttm_yoy  REAL,
    net_income_growth_q_yoy  REAL,
    net_income_growth_q_qoq  REAL,
    eps_growth_ttm_yoy REAL,
    eps_growth_q_yoy REAL,
    eps_growth_q_qoq REAL,
    FOREIGN KEY (company_id) REFERENCES company(company_id) ON DELETE CASCADE,
    UNIQUE (company_id, period_year, period_month)                         -- dönem başına tek oran seti
);

-- 5) multiple
CREATE TABLE IF NOT EXISTS multiple (
    multiple_id         INTEGER PRIMARY KEY,
    company_id          INTEGER NOT NULL,
    date_of_price       TEXT NOT NULL,
    period_year         TEXT    NOT NULL,
    period_month        TEXT    NOT NULL,
    pe                  REAL,
    pb                  REAL,
    ps                  REAL,
    ev_ebitda           REAL,
    dividend_yield      REAL,
    peg                 REAL,
    FOREIGN KEY (company_id) REFERENCES company(company_id) ON DELETE CASCADE,
    UNIQUE (company_id, date_of_price)
);

-- 6) portfolio
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