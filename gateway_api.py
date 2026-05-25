from fastapi import FastAPI
import pandas as pd
import numpy as np
import random
import uuid

from datetime import datetime

# ============================================================
# FASTAPI CONFIG
# ============================================================

app = FastAPI(

    title="Enterprise Financial Gateway API",

    description="""
    Hybrid Financial Gateway API
    supporting both historical and live transactions
    for reconciliation and auditing platform.
    """,

    version="1.0.0"
)

# ============================================================
# HISTORICAL FILE
# ============================================================

CSV_FILE = "gateway_transactions.csv"

# ============================================================
# LOAD HISTORICAL DATA
# ============================================================

historical_df = pd.read_csv(CSV_FILE)

historical_df.replace(
    [np.inf, -np.inf],
    np.nan,
    inplace=True
)

historical_df = historical_df.fillna("")

# ============================================================
# MASTER DATA
# ============================================================

payment_statuses = [
    "SUCCESS",
    "FAILED",
    "PENDING"
]

regions = [
    "US",
    "EU",
    "APAC"
]

# ============================================================
# ROOT ENDPOINT
# ============================================================

@app.get("/")
def home():

    return {

        "message":
            "Enterprise Financial Gateway API Running",

        "available_endpoints": [

            "/transactions",
            "/live-transactions",
            "/failed-transactions",
            "/stats",
            "/health"
        ]
    }

# ============================================================
# HISTORICAL TRANSACTIONS
# ============================================================

@app.get("/transactions")
def get_transactions(limit: int = 100):

    latest = historical_df.tail(limit)

    return {

        "source_type":
            "historical_batch_data",

        "count":
            len(latest),

        "transactions":
            latest.to_dict(
                orient="records"
            )
    }

# ============================================================
# LIVE TRANSACTION GENERATOR
# ============================================================

def generate_live_transactions(num_records=50):

    transactions = []

    for _ in range(num_records):

        amount = round(
            random.uniform(100, 100000),
            2
        )

        # Outlier Transactions

        if random.random() < 0.01:

            amount = round(
                random.uniform(1000000, 5000000),
                2
            )

        # Refund / Negative Transactions

        if random.random() < 0.02:

            amount = -amount

        transaction = {

            "gateway_transaction_id":
                f"GTX-{random.randint(1000000,9999999)}",

            "transaction_ref":
                str(uuid.uuid4())[:12],

            "customer_id":
                f"CUST-{random.randint(10000,99999)}",

            "txn_amount":
                amount,

            "gateway_fee":
                round(
                    abs(amount) * random.uniform(0.01, 0.03),
                    2
                ),

            "payment_state":
                random.choice(payment_statuses),

            "gateway_timestamp":
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),

            "settlement_batch":
                f"BATCH-{random.randint(1000,9999)}",

            "processing_region":
                random.choice(regions)
        }

        # ====================================================
        # INJECT OPERATIONAL ANOMALIES
        # ====================================================

        # Missing transaction reference

        if random.random() < 0.01:

            transaction["transaction_ref"] = None

        # Invalid region

        if random.random() < 0.01:

            transaction["processing_region"] = "UNKNOWN"

        # Delayed settlement simulation

        if random.random() < 0.03:

            transaction["payment_state"] = "PENDING"

        transactions.append(transaction)

    return transactions

# ============================================================
# LIVE TRANSACTIONS ENDPOINT
# ============================================================

@app.get("/live-transactions")
def live_transactions(limit: int = 50):

    transactions = generate_live_transactions(limit)

    return {

        "source_type":
            "live_operational_stream",

        "generated_at":
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),

        "count":
            len(transactions),

        "transactions":
            transactions
    }

# ============================================================
# FAILED TRANSACTIONS
# ============================================================

@app.get("/failed-transactions")
def failed_transactions(limit: int = 100):

    failed = historical_df[
        historical_df["payment_state"] == "FAILED"
    ]

    failed = failed.tail(limit)

    return {

        "count":
            len(failed),

        "transactions":
            failed.to_dict(
                orient="records"
            )
    }

# ============================================================
# API HEALTH
# ============================================================

@app.get("/health")
def health():

    return {

        "status":
            "RUNNING",

        "timestamp":
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
    }

# ============================================================
# OPERATIONAL STATS
# ============================================================

@app.get("/stats")
def stats():

    return {

        "total_historical_transactions":
            len(historical_df),

        "successful_transactions":
            len(
                historical_df[
                    historical_df["payment_state"]
                    == "SUCCESS"
                ]
            ),

        "failed_transactions":
            len(
                historical_df[
                    historical_df["payment_state"]
                    == "FAILED"
                ]
            ),

        "pending_transactions":
            len(
                historical_df[
                    historical_df["payment_state"]
                    == "PENDING"
                ]
            )
    }
