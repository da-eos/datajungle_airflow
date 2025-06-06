from datetime import datetime, timedelta, timezone

from airflow.decorators import dag, task
from airflow.models import Variable
from airflow.operators.dummy import DummyOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from coinmarketcap.cmp_utils import CoinMarketCapAPI
from psycopg2.extras import execute_values

default_args = {
    "owner": "DataJungle",
    "retries": 1,
    "retry_delay": timedelta(milliseconds=500),
    "depends_on_past": True,
    "tags": ["coinmarketcap"],
}

COINCAP_API_KEY = Variable.get("COINCAP_API_KEY")
DAG_ID = "CoinMarketCapDAG"
PG_CONNECT = "POSTGRES_DB"


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
        data = data.get("data", [])
        return data

    @task(task_id="ParseData")
    def deparse_cmc_data(data):
        result = []
        for item in data:
            d = {}
            d["name"] = item.get("name")
            d["symbol"] = item.get("symbol")
            d["num_market_pairs"] = item.get("num_market_pairs")
            d["date_added"] = item.get("date_added")
            d["usdt_price"] = item.get("quote", {}).get("price")
            d["cmc_rank"] = item.get("cmc_rank")
            result.append(d)
        return result

    @task(task_id="InsertDatas")
    def insert_data(data_to_insert):
        pg_hook = PostgresHook(postgres_conn_id=PG_CONNECT)
        fields = tuple(data_to_insert[0].keys()) if data_to_insert else None
        print(fields)
        tuple_values = []
        for d in data_to_insert:
            row = tuple(d.get(key) for key in d)
            tuple_values.append(row)
        try:
            pg_hook.insert_rows(
                table="raw_data.coinmarket_data",
                rows=tuple_values,
                target_fields=fields,
                commit_every=50,
            )
            return "Data inserted"
        except Exception as e:
            print(f"error {e}")
            return e

    start = DummyOperator(task_id="Start")
    end = DummyOperator(task_id="End")
    data = get_latests_data()
    deparsed = deparse_cmc_data(data)

    insert = insert_data(deparsed)

    start >> data >> deparsed >> insert >> end


cmc_dag = coinmarketdag()
