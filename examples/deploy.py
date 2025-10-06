from prefect import tags
# from smartcity import logger
from prefect_flows.flow import workflow_openaq
from prefect import flow

# from prefect.server.schemas.schedules import CronSchedule

# prefect deploy (will use prefect CLI and prefect.yaml file)

if __name__ == "__main__":
    name = "daily-openaq"
    pool_name = "local-agent-pool"
    flow.from_source(
        source="https://github.com/issa-kabore/smartcity-datalake.git",
        entrypoint="prefect_flows/flow.py:workflow_openaq",
    ).deploy(  # type: ignore
        name=name,
        work_pool_name=pool_name,
        cron="0 4 * * *",
        tags=["smartcity", "openaq"],
    )
