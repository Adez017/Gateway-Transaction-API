from fastapi import FastAPI
import pandas as pd
import numpy as np
from datetime import datetime

# ============================================================
# FASTAPI CONFIG
# ============================================================

app = FastAPI(
    title="Enterprise Financial Gateway API",
    description="Gateway Incremental Feed API",
    version="3.0.0"
)

# ============================================================
# SOURCE FILE
# ============================================================

CSV_FILE = "gateway_transactions.csv"

# ============================================================
# LOAD GATEWAY DATA
# ============================================================

gateway_df = pd.read_csv(CSV_FILE)

gateway_df.replace(
    [np.inf, -np.inf],
    np.nan,
    inplace=True
)

gateway_df.fillna("", inplace=True)

# ============================================================
# GLOBAL OFFSET
# ============================================================

current_offset = 0

# ============================================================
# ROOT
# ============================================================

@app.get("/")
def home():

    return {

        "message":
            "Financial Gateway API Running",

        "available_endpoints": [

            "/transactions",
            "/live-transactions",
            "/stats",
            "/health"
        ]
    }

# ============================================================
# FULL HISTORICAL DATA
# ============================================================

@app.get("/transactions")
def get_transactions(limit: int = 1000):

    data = gateway_df.head(limit)

    return {

        "source_type":
            "historical_gateway_data",

        "count":
            len(data),

        "transactions":
            data.to_dict(
                orient="records"
            )
    }

# ============================================================
# INCREMENTAL FEED
# ============================================================

@app.get("/live-transactions")
def live_transactions(
    batch_size: int = 100
):

    global current_offset

    start_idx = current_offset
    end_idx = current_offset + batch_size

    batch = gateway_df.iloc[
        start_idx:end_idx
    ]

    if len(batch) == 0:

        return {
            "source_type": "incremental_gateway_feed",
            "generated_at": datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "count": 0,
            "message": "No new transactions available",
            "transactions": []
        }

    current_offset = end_idx

    return {

        "source_type":
            "incremental_gateway_feed",

        "generated_at":
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),

        "batch_start":
            start_idx,

        "batch_end":
            min(
                end_idx,
                len(gateway_df)
            ),

        "count":
            len(batch),

        "transactions":
            batch.to_dict(
                orient="records"
            )
    }
# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():

    return {

        "status":
            "RUNNING",

        "gateway_records":
            len(gateway_df),

        "current_offset":
            current_offset,

        "timestamp":
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
    }

# ============================================================
# STATS
# ============================================================

@app.get("/stats")
def stats():

    return {

        "total_gateway_transactions":
            len(gateway_df),

        "successful_transactions":
            int(
                (
                    gateway_df[
                        "payment_state"
                    ] == "SUCCESS"
                ).sum()
            ),

        "failed_transactions":
            int(
                (
                    gateway_df[
                        "payment_state"
                    ] == "FAILED"
                ).sum()
            ),

        "pending_transactions":
            int(
                (
                    gateway_df[
                        "payment_state"
                    ] == "PENDING"
                ).sum()
            ),

        "total_amount":
            round(
                gateway_df[
                    "amount"
                ].sum(),
                2
            ),

        "average_gateway_fee":
            round(
                gateway_df[
                    "gateway_fee"
                ].mean(),
                2
            )
    }

# ============================================================
# RUN
# ============================================================

# uvicorn gateway_api:app --reload
