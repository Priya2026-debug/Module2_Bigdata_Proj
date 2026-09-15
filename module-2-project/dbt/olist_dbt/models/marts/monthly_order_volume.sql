
{{ config(materialized='table') }}

SELECT
    DATE_TRUNC(
        DATE(order_purchase_timestamp),
        MONTH
    ) AS order_month,

    COUNT(DISTINCT order_id) AS order_count

FROM {{ ref('stg_orders') }}

GROUP BY order_month
ORDER BY order_month
