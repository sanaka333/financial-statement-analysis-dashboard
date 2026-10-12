import yfinance as yf
import pandas as pd


def get_income_data(symbol):

    ticker = yf.Ticker(symbol)
    statement = ticker.get_income_stmt(freq="yearly", pretty=True)

    if statement.empty:
        raise ValueError(f"No income statement available for {symbol}")

    df = statement.T

    income_df = df.reindex(columns=[
        "Gross Profit",
        "Total Revenue",
        "Operating Income",
        "Net Income",
    ]).copy()

    income_df.columns = [
        "gross_profit",
        "revenue",
        "operating_income",
        "net_income"
    ]

    income_df.index.name = "date"
    income_df = income_df.reset_index()

    income_df["currency"] = ticker.get_info().get(
        "financialCurrency", pd.NA
    )

    income_df = income_df[[
        "date", "currency", "gross_profit",
        "revenue", "operating_income", "net_income"
    ]]
    
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", None)

    numeric_columns = ["revenue", "gross_profit", "operating_income", "net_income"]

    income_df[numeric_columns] = income_df[numeric_columns].apply(
        pd.to_numeric,
        errors='coerce'
    )

    income_df["date"] = pd.to_datetime(income_df["date"])

    income_df["net_profit_margin"] = (
        income_df["net_income"] / income_df["revenue"]
    ) * 100

    income_df["gross_margin"] = (
        income_df["gross_profit"] / income_df["revenue"]
    ) * 100

    income_df["operating_margin"] = (
        income_df["operating_income"] / income_df["revenue"]
    ) * 100


    income_df = income_df.sort_values("date")

    income_df["year"] = income_df["date"].dt.year

    income_df["symbol"] = symbol

    income_df.to_csv(f"{symbol}_cleaned.csv", index=False) 

    return income_df

apple_df = get_income_data("AAPL")
microsoft_df = get_income_data("MSFT")
google_df = get_income_data("GOOGL")


combined_df = pd.concat(
    [apple_df, microsoft_df, google_df],
    ignore_index=True
)

combined_df.to_csv("financial_dashboard_data.csv", index=False)

