# Create Dagster assets in this file

from pathlib import Path

from dagster import asset, Definitions, ScheduleDefinition, define_asset_job, AssetSelection
from dagster_dbt import DbtCliResource, DagsterDbtTranslator, dbt_assets

from src.extract.kaggle_extract import extract_kaggle_to_gcs
from src.loader.kaggle_load import load_gcs_to_bigquery
from src.profiling.profile_orders import profile_orders


# ---------------------------------------------------------
# Existing pipeline assets
# ---------------------------------------------------------

@asset
def kaggle_to_gcs():
    extract_kaggle_to_gcs()


@asset(deps=[kaggle_to_gcs])
def gcs_to_bigquery_raw():
    load_gcs_to_bigquery()


@asset(deps=[gcs_to_bigquery_raw])
def profile_orders_asset():
    profile_orders()


# ---------------------------------------------------------
# DBT configuration
# ---------------------------------------------------------

dbt_project_dir = Path("/module-2-project/dbt/olist_dbt")

dbt = DbtCliResource(
    project_dir=dbt_project_dir,
    profiles_dir="/module-2-project/dbt/profiles",
)


# ---------------------------------------------------------
# DBT assets
# ---------------------------------------------------------
class CustomDbtTranslator(DagsterDbtTranslator):

    def get_asset_spec(self, manifest, unique_id, project):

        spec = super().get_asset_spec(
            manifest,
            unique_id,
            project
        )

        if spec.key.to_user_string() == "stg_orders":
            spec = spec.merge_attributes(
                deps=[gcs_to_bigquery_raw]
            )

        return spec

@dbt_assets(
    manifest=dbt_project_dir / "target" / "manifest.json",
    dagster_dbt_translator=CustomDbtTranslator(),
)
def olist_dbt_assets(context, dbt: DbtCliResource):
    yield from dbt.cli(["build"], context=context).stream()

# ---------------------------------------------------------
# Dagster job and schedule
# ---------------------------------------------------------

daily_pipeline_job = define_asset_job(
    name="daily_olist_pipeline",
    selection=AssetSelection.all(),
)

daily_olist_schedule = ScheduleDefinition(
    job=daily_pipeline_job,
    cron_schedule="0 2 * * *",
    execution_timezone="Asia/Singapore",
)

# ---------------------------------------------------------
# Dagster definitions
# ---------------------------------------------------------

defs = Definitions(
    assets=[
        kaggle_to_gcs,
        gcs_to_bigquery_raw,
        profile_orders_asset,
        olist_dbt_assets,
    ],
    resources={
        "dbt": dbt,
    },
    jobs=[
        daily_pipeline_job,
    ],
    schedules=[
        daily_olist_schedule,
    ],
)
