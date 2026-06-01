from fastapi import FastAPI
import pandas as pd
import numpy as np
import random
import uuid

from datetime import datetime, timedelta

# ============================================================
# FASTAPI CONFIG
# ============================================================

app = FastAPI(
    title="Enterprise Financial Gateway API",
    description="""
    Gateway Transaction Source API

    Supports:
    - Historical Transaction Load
    - Live Transaction Feed
    - Reconciliation Testing
    """,
    version="2.0.0"
)

# ============================================================
# SOURCE FILE
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

historical_df.fillna("", inplace=True)

# ============================================================
# MASTER DATA
# ============================================================

PAYMENT_STATUSES = [
    "SUCCESS",
    "FAILED",
    "PENDING"
]

CURRENCIES = [
    "USD",
    "EUR",
    "INR",
    "GBP"
]

GATEWAYS = [
    "Stripe",
    "PayPal",
    "Razorpay"
]

PAYMENT_METHODS = [
    "UPI",
    "NETBANKING",
    "CARD",
    "WALLET"
]

REGIONS = [
    "US",
    "EU",
    "IN",
    "APAC"
]

# ============================================================
# ROOT
# ============================================================

@app.get("/")
def home():

    return {

        "message":
            "Enterprise Financial Gateway API Running",

        "available_endpoints": [

            "/transactions",
            "/live-transactions",
            "/stats",
            "/health"
        ]
    }

# ============================================================
# HISTORICAL TRANSACTIONS
# ============================================================

@app.get("/transactions")
def get_transactions(limit: int = 10000):

    data = historical_df.tail(limit)

    return {

        "source_type":
            "historical_gateway_batch",

        "extracted_at":
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            ),

        "count":
            len(data),

        "transactions":
            data.to_dict(
                orient="records"
            )
    }

# ============================================================
# LIVE TRANSACTION GENERATOR
# ============================================================

def generate_live_transactions(
    num_records=100
):

    transactions = []

    for _ in range(num_records):

        amount = round(
            random.uniform(
                100,
                100000
            ),
            2
        )

        # High-value transaction anomaly

        if random.random() < 0.01:

            amount = round(
                random.uniform(
                    1000000,
                    5000000
                ),
                2
            )

        transaction = {

            "gateway_transaction_id":
                f"GTW-{random.randint(100000,999999)}",

            "transaction_ref":
                str(uuid.uuid4())[:12],

            "customer_id":
                f"CUST-{random.randint(1000,9999)}",

            "amount":
                amount,

            "currency":
                random.choice(
                    CURRENCIES
                ),

            "gateway_name":
                random.choice(
                    GATEWAYS
                ),

            "payment_method":
                random.choice(
                    PAYMENT_METHODS
                ),

            "payment_state":
                random.choice(
                    PAYMENT_STATUSES
                ),

            "gateway_timestamp":
                datetime.now().strftime(
                    "%d-%m-%Y %H:%M"
                ),

            "region":
                random.choice(
                    REGIONS
                ),

            "gateway_fee":
                round(
                    amount *
                    random.uniform(
                        0.01,
                        0.03
                    ),
                    2
                )
        }

        # ====================================================
        # RECONCILIATION TEST SCENARIOS
        # ====================================================

        # Missing transaction reference

        if random.random() < 0.01:

            transaction[
                "transaction_ref"
            ] = None

        # Missing customer

        if random.random() < 0.005:

            transaction[
                "customer_id"
            ] = None

        # Refund

        if random.random() < 0.02:

            transaction[
                "amount"
            ] = -amount

        # Invalid currency

        if random.random() < 0.005:

            transaction[
                "currency"
            ] = "XXX"

        # Unknown region

        if random.random() < 0.005:

            transaction[
                "region"
            ] = "UNKNOWN"

        # Excessive fee anomaly

        if random.random() < 0.005:

            transaction[
                "gateway_fee"
            ] = round(
                amount * 0.25,
                2
            )

        # Future timestamp anomaly

        if random.random() < 0.005:

            transaction[
                "gateway_timestamp"
            ] = (
                datetime.now()
                + timedelta(days=2)
            ).strftime(
                "%d-%m-%Y %H:%M"
            )

        # Duplicate reference anomaly

        if random.random() < 0.005:

            transaction[
                "transaction_ref"
            ] = "DUPLICATE_REF"

        transactions.append(
            transaction
        )

    return transactions

# ============================================================
# LIVE TRANSACTIONS
# ============================================================

@app.get("/live-transactions")
def live_transactions(
    limit: int = 50
):

    transactions = generate_live_transactions(
        limit
    )

    return {

        "source_type":
            "live_gateway_stream",

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
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():

    return {

        "status":
            "RUNNING",

        "source":
            "Gateway API",

        "historical_records":
            len(historical_df),

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
            int(
                (
                    historical_df[
                        "payment_state"
                    ] == "SUCCESS"
                ).sum()
            ),

        "failed_transactions":
            int(
                (
                    historical_df[
                        "payment_state"
                    ] == "FAILED"
                ).sum()
            ),

        "pending_transactions":
            int(
                (
                    historical_df[
                        "payment_state"
                    ] == "PENDING"
                ).sum()
            ),

        "total_amount":
            round(
                historical_df[
                    "amount"
                ].sum(),
                2
            ),

        "average_gateway_fee":
            round(
                historical_df[
                    "gateway_fee"
                ].mean(),
                2
            )
    }

# ============================================================
# RUN
# ============================================================

# uvicorn gateway_api:app --reload
