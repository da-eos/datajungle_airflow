from datetime import datetime, timedelta, timezone

from airflow.decorators import dag, task
from airflow.models import Variable
from airflow.operators.dummy import DummyOperator
from coinmarketcap.cmp_utils import CoinMarketCapAPI

default_args = {
    "owner": "DataJungle",
    "retries": 1,
    "retry_delay": timedelta(milliseconds=500),
    "depends_on_past": True,
    "tags": ["coinmarketcap"],
}

COINCAP_API_KEY = Variable.get("COINCAP_API_KEY")
DAG_ID = "CoinMarketCapDAG"


@dag(
    dag_id=DAG_ID,
    schedule_interval="@hourly",
    start_date=datetime.now(timezone.utc) - timedelta(hours=1),
    catchup=False,
    max_active_runs=1,
)
def coinmarketdag():
    """
    Dag for load data from CMP API
    """

    cmc_api = CoinMarketCapAPI(COINCAP_API_KEY)

    @task(task_id="GetLatests")
    def get_latests_data():
        data = cmc_api.get_latests()
        return data

    @task(task_id="ParseData")
    def deparse_cmc_data(data):
        print(data)

    start = DummyOperator(task_id="Start")
    end = DummyOperator(task_id="End")
    data = get_latests_data()
    deparsed = deparse_cmc_data(data)

    start >> data >> deparsed >> end


cmc_dag = coinmarketdag()
