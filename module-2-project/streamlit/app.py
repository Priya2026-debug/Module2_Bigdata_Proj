
import os

import pandas as pd
import streamlit as st
from google.cloud import bigquery


# --------------------------------------------------
# Streamlit page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="Olist Analytics",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Olist Analytics Dashboard")
st.write("Historical monthly order volume")


# --------------------------------------------------
# BigQuery configuration
# --------------------------------------------------

PROJECT_ID = os.environ["GCP_PROJECT_ID"]

TABLE_ID = (
    f"{PROJECT_ID}."
    "olist_analytics."
    "monthly_order_volume"
)


# --------------------------------------------------
# Query BigQuery
# --------------------------------------------------

@st.cache_data
def load_data():

    client = bigquery.Client(project=PROJECT_ID)

    query = f"""
        SELECT
            order_month,
            order_count
        FROM `{TABLE_ID}`
        ORDER BY order_month
    """

    df = client.query(query).to_dataframe()

    return df


# --------------------------------------------------
# Load data
# --------------------------------------------------

df = load_data()


# --------------------------------------------------
# Display data
# --------------------------------------------------

st.subheader("Monthly Order Volume")

st.dataframe(
    df,
    use_container_width=True
)


# --------------------------------------------------
# Display chart
# --------------------------------------------------

st.subheader("Order Volume Trend")

chart_df = df.set_index("order_month")

st.line_chart(
    chart_df["order_count"]
)


# --------------------------------------------------
# Data interpretation
# --------------------------------------------------

st.info(
    "Note: September and October 2018 contain incomplete "
    "data because the source dataset ends in October 2018."
)

