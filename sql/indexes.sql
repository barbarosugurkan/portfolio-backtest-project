-- Bu dosyanın ana amacı sorgu performansını arttırmak için indexler oluşturmak
-- Mesela finansallar için company_id ve period bir girişi temsil eder. Buna göre
-- sorgulama yapılabilir.

CREATE INDEX IF NOT EXISTS idx_prices_company_date
    ON price (company_id, date);

CREATE INDEX IF NOT EXISTS idx_financials_company_period
    ON financial (company_id, period);

CREATE INDEX IF NOT EXISTS idx_ratios_company_period
    ON ratio (company_id, date);
    
CREATE INDEX IF NOT EXISTS idx_multiples_company_period
    ON multiple (company_id, date_of_price);

CREATE INDEX IF NOT EXISTS idx_portfolio_company_date
    ON portfolio (company_id, date_purchased);