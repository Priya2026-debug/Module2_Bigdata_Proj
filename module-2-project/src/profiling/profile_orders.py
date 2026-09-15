
from google.cloud import bigquery
import os


def profile_orders():

    GCP_PROJECT_ID = os.environ["GCP_PROJECT_ID"]
    GCS_DATASET_ID = os.environ["GCS_DATASET_ID"]

    # ---------------------------------------------------------
    # Configuration
    # ---------------------------------------------------------

    TABLE = "olist_orders"

    TABLE_ID = f"{GCP_PROJECT_ID}.{GCS_DATASET_ID}.{TABLE}"

    # ---------------------------------------------------------
    # BigQuery connection
    # ---------------------------------------------------------

    client = bigquery.Client(project=GCP_PROJECT_ID)

    print("=" * 70)
    print("DATA PROFILING REPORT")
    print("=" * 70)
    print(f"Table: {TABLE_ID}")
    print()

    # ---------------------------------------------------------
    # 1. Row count
    # ---------------------------------------------------------

    print("1. ROW COUNT")
    print("-" * 70)

    query = f"""
    SELECT COUNT(*) AS row_count
    FROM `{TABLE_ID}`
    """

    result = list(client.query(query).result())
    row_count = result[0]["row_count"]

    print(f"Total rows: {row_count:,}")
    print()

    # ---------------------------------------------------------
    # 2. Order status distribution
    # ---------------------------------------------------------

    print("2. ORDER STATUS DISTRIBUTION")
    print("-" * 70)

    query = f"""
    SELECT
        order_status,
        COUNT(*) AS count
    FROM `{TABLE_ID}`
    GROUP BY order_status
    ORDER BY count DESC
    """

    results = client.query(query).result()

    for row in results:
        print(f"{row['order_status']}: {row['count']:,}")

    print()

    # ---------------------------------------------------------
    # 3. NULL value analysis
    # ---------------------------------------------------------

    print("3. NULL VALUE ANALYSIS")
    print("-" * 70)

    query = f"""
    SELECT
        COUNTIF(order_id IS NULL) AS order_id_nulls,
        COUNTIF(customer_id IS NULL) AS customer_id_nulls,
        COUNTIF(order_status IS NULL) AS status_nulls,
        COUNTIF(order_purchase_timestamp IS NULL) AS purchase_nulls,
        COUNTIF(order_approved_at IS NULL) AS approved_nulls,
        COUNTIF(order_delivered_carrier_date IS NULL) AS carrier_nulls,
        COUNTIF(order_delivered_customer_date IS NULL) AS delivered_nulls,
        COUNTIF(order_estimated_delivery_date IS NULL) AS estimated_nulls
    FROM `{TABLE_ID}`
    """

    row = list(client.query(query).result())[0]

    null_columns = {
        "order_id": row["order_id_nulls"],
        "customer_id": row["customer_id_nulls"],
        "order_status": row["status_nulls"],
        "order_purchase_timestamp": row["purchase_nulls"],
        "order_approved_at": row["approved_nulls"],
        "order_delivered_carrier_date": row["carrier_nulls"],
        "order_delivered_customer_date": row["delivered_nulls"],
        "order_estimated_delivery_date": row["estimated_nulls"],
    }

    for column, count in null_columns.items():
        percentage = (count / row_count * 100) if row_count else 0
        print(f"{column:40} {count:8,} ({percentage:6.2f}%)")

    print()

    # ---------------------------------------------------------
    # 4. Duplicate order IDs
    # ---------------------------------------------------------

    print("4. DUPLICATE ORDER IDs")
    print("-" * 70)

    query = f"""
    SELECT
        order_id,
        COUNT(*) AS count
    FROM `{TABLE_ID}`
    GROUP BY order_id
    HAVING COUNT(*) > 1
    ORDER BY count DESC
    LIMIT 20
    """

    results = list(client.query(query).result())

    if not results:
        print("No duplicate order_ids found.")
    else:
        print("Duplicate order_ids detected.")
        print("Showing up to 20 examples:")
        print()

        for row in results:
            print(
                f"order_id: {row['order_id']} | "
                f"count: {row['count']}"
            )

    print()

    # ---------------------------------------------------------
    # 5. Purchase date range
    # ---------------------------------------------------------

    print("5. PURCHASE DATE RANGE")
    print("-" * 70)

    query = f"""
    SELECT
        MIN(order_purchase_timestamp) AS earliest_order,
        MAX(order_purchase_timestamp) AS latest_order
    FROM `{TABLE_ID}`
    """

    row = list(client.query(query).result())[0]

    print(f"Earliest order: {row['earliest_order']}")
    print(f"Latest order:   {row['latest_order']}")
    print()

    # ---------------------------------------------------------
    # 6. Invalid delivery dates
    # ---------------------------------------------------------

    print("6. INVALID DELIVERY DATES")
    print("-" * 70)

    query = f"""
    SELECT COUNT(*) AS invalid_delivery_dates
    FROM `{TABLE_ID}`
    WHERE order_delivered_customer_date < order_purchase_timestamp
    """

    row = list(client.query(query).result())[0]

    print(
        f"Orders delivered before purchase: "
        f"{row['invalid_delivery_dates']:,}"
    )
    print()

    # ---------------------------------------------------------
    # 7. Invalid estimated delivery dates
    # ---------------------------------------------------------

    print("7. INVALID ESTIMATED DELIVERY DATES")
    print("-" * 70)

    query = f"""
    SELECT COUNT(*) AS invalid_count
    FROM `{TABLE_ID}`
    WHERE DATE(order_estimated_delivery_date)
          < DATE(order_purchase_timestamp)
    """

    row = list(client.query(query).result())[0]

    print(
        f"Orders with estimated delivery before purchase: "
        f"{row['invalid_count']}"
    )

    # ---------------------------------------------------------
    # Profiling complete
    # ---------------------------------------------------------

    print("=" * 70)
    print("PROFILING COMPLETE")
    print("=" * 70)
