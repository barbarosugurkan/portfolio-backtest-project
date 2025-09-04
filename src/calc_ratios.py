import sqlite3
import pandas as pd

def calc_ratios(conn):

    query = "SELECT * FROM financial"
    fin_df = pd.read_sql_query(query, conn)

    fin_df["current_ratio"] = fin_df["current_assets"] / fin_df["short_term_debt"]
    fin_df["debt_to_equity"] = fin_df["gross_debt"] / fin_df["equity"]
    fin_df["debt_to_assets"] = fin_df["gross_debt"] / (fin_df["fixed_assets"] + fin_df["current_assets"])
    fin_df['debt_to_ebitda'] = fin_df['gross_debt'] / fin_df['ebitda_ttm']

    fin_df["net_income_margin_ttm"] = fin_df["net_income_ttm"] / fin_df["revenue_ttm"]
    fin_df["net_income_margin_q"] = fin_df["net_income_q"] / fin_df["revenue_q"]
    fin_df["net_income_margin_c"] = fin_df["net_income_c"] / fin_df["revenue_c"]
    fin_df["gross_profit_margin_ttm"] = fin_df["gross_profit_ttm"] / fin_df["revenue_ttm"]
    fin_df["gross_profit_margin_q"] = fin_df["gross_profit_q"] / fin_df["revenue_q"]
    fin_df["gross_profit_margin_c"] = fin_df["gross_profit_c"] / fin_df["revenue_c"]
    fin_df["operating_margin_ttm"] = fin_df["operating_profit_ttm"] / fin_df["revenue_ttm"]
    fin_df["operating_margin_q"] = fin_df["operating_profit_q"] / fin_df["revenue_q"]
    fin_df["operating_margin_c"] = fin_df["operating_profit_c"] / fin_df["revenue_c"]

    fin_df["roe_ttm"] = fin_df["net_income_ttm"] / fin_df["equity"]
    fin_df["roe_q"] = fin_df["net_income_q"] / fin_df["equity"]
    fin_df["roa_ttm"] = fin_df["net_income_ttm"] / (fin_df["fixed_assets"] + fin_df["current_assets"])
    fin_df["roa_q"] = fin_df["net_income_q"] / (fin_df["fixed_assets"] + fin_df["current_assets"])
    fin_df["roic_ttm"] = (fin_df['operating_profit_ttm'] * (1 - fin_df['effective_tax_rate_ttm'])) / (fin_df['gross_debt'] + fin_df['equity'])
    fin_df['asset_turnover'] = fin_df['revenue_ttm'] / (fin_df["fixed_assets"] + fin_df["current_assets"])

    fin_df['period_month'] = pd.to_numeric(fin_df['period_month'])
    fin_df['period_year'] = pd.to_numeric(fin_df['period_year'])
    fin_df = fin_df.sort_values(by=['company_id', 'period_year', 'period_month']).reset_index(drop=True)
    fin_df["revenue_growth_ttm_yoy"] = (fin_df["revenue_ttm"] / fin_df.groupby('company_id')['revenue_ttm'].shift(4)) - 1
    fin_df["revenue_growth_q_yoy"] = (fin_df["revenue_q"] / fin_df.groupby('company_id')['revenue_q'].shift(4)) - 1
    fin_df["revenue_growth_q_qoq"] = (fin_df["revenue_q"] / fin_df.groupby('company_id')['revenue_q'].shift(1)) - 1
    fin_df["net_income_growth_ttm_yoy"] = (fin_df["net_income_ttm"] / fin_df.groupby('company_id')['net_income_ttm'].shift(4)) - 1
    fin_df["net_income_growth_q_yoy"] = (fin_df["net_income_q"] / fin_df.groupby('company_id')['net_income_q'].shift(4)) - 1
    fin_df["net_income_growth_q_qoq"] = (fin_df["net_income_q"] / fin_df.groupby('company_id')['net_income_q'].shift(1)) - 1
    fin_df["eps_growth_ttm_yoy"] = (fin_df["eps_ttm"] / fin_df.groupby('company_id')['eps_ttm'].shift(4)) - 1
    fin_df["eps_growth_q_yoy"] = (fin_df["eps_q"] / fin_df.groupby('company_id')['eps_q'].shift(4)) - 1
    fin_df["eps_growth_q_qoq"] = (fin_df["eps_q"] / fin_df.groupby('company_id')['eps_q'].shift(1)) - 1

    ratio_df = fin_df[["company_id","period_year","period_month","date_of_publish","current_ratio","debt_to_equity","debt_to_assets","debt_to_ebitda","net_income_margin_ttm","net_income_margin_q","net_income_margin_c","gross_profit_margin_ttm","gross_profit_margin_q","gross_profit_margin_c","operating_margin_ttm","operating_margin_q","operating_margin_c","roe_ttm","roe_q","roa_ttm","roa_q","roic_ttm",'asset_turnover',"revenue_growth_ttm_yoy","revenue_growth_q_yoy","revenue_growth_q_qoq","net_income_growth_ttm_yoy","net_income_growth_q_yoy","net_income_growth_q_qoq","eps_growth_ttm_yoy","eps_growth_q_yoy","eps_growth_q_qoq"]]

    return ratio_df


if __name__ == "__main__":
    conn = sqlite3.connect("C:/Users/KULLANICI/Desktop/portfolio-backtest-project/data/database.db")
    ratio_df = calc_ratios(conn)
    ratio_df.to_sql('ratio', conn, if_exists='append', index=False)
    conn.close()