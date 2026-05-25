from fastapi import FastAPI
import pandas as pd
import numpy as np

app = FastAPI(

    title="Financial Gateway API",

    description="""
    Production-grade payment gateway simulation API
    for financial reconciliation and auditing platform.
    """,

    version="1.0.0",

    contact={
        "name": "Aditya Singh Rathore",
        "email": "aditya.rathore@getondata.com"
    }
)
# ====================================================
# LOAD DATA
# ====================================================

df = pd.read_csv("gateway_transactions.csv")

# ====================================================
# CLEAN INVALID JSON VALUES
# ====================================================

df.replace(
    [np.inf, -np.inf],
    np.nan,
    inplace=True
)

df = df.fillna("")

# ====================================================
# ROOT
# ====================================================

@app.get("/")
def home():

    return {
        "message": "Financial Gateway API Running"
    }

# ====================================================
# GET TRANSACTIONS
# ====================================================

@app.get("/transactions")
def get_transactions(limit: int = 100):

    data = df.sample(limit).to_dict(
        orient="records"
    )

    return {
        "count": len(data),
        "transactions": data
    }

# ====================================================
# FAILED TRANSACTIONS
# ====================================================

@app.get("/failed-transactions")
def failed_transactions():

    failed = df[
        df["payment_state"] == "FAILED"
    ]

    data = failed.head(100).to_dict(
        orient="records"
    )

    return {
        "count": len(data),
        "transactions": data
    }

# ====================================================
# GET TRANSACTION BY ID
# ====================================================

@app.get("/transaction/{transaction_id}")
def transaction_by_id(transaction_id: str):

    txn = df[
        df["gateway_transaction_id"] == transaction_id
    ]

    if txn.empty:

        return {
            "message": "Transaction not found"
        }

    return txn.iloc[0].to_dict()
