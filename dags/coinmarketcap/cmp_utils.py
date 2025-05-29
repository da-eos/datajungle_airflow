import requests


class CoinMarketCapAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://pro-api.coinmarketcap.com/v1/"
        self.headers = {
            "Accepts": "application/json",
            "X-CMC_PRO_API_KEY": self.api_key,
        }
        self.session = requests.Session()

    def _api_call_get(self, path="", params={}):
        try:
            response = self.session.get(
                f"{self.base_url}{path}", headers=self.headers, params=params
            )
            response.raise_for_status()
            data = response.json()
            return data
        except requests.exceptions.HTTPError as e:
            print(f"An error occured: {e}")
            return []

    def get_latests(
        self,
        path="cryptocurrency/listings/latest",
        params={"start": 1, "limit": 300, "convert": "USDT"},
    ):
        return self._api_call_get(path=path, params=params)


# if __name__ == "__main__":
#     api_key = "15594141-1816-4561-ab8c-9de458d47e93"
#     api = CoinMarketCapAPI(api_key)

#     response = api.get_latests()
#     with open("example.json", "w") as f:
#         json.dump(response.get("data"), f, indent=4)
#     print("Done")
