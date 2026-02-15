import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from simple_salesforce import Salesforce

BASE_DIR = Path(__file__).resolve().parent
QUERY_PATH = BASE_DIR / "input_queries/field_definition.sql"
OUTPUT_PATH = BASE_DIR / "output_files/"
ENV_PATH = BASE_DIR / ".env"


def _required_env(var_name: str) -> str:
    value = os.getenv(var_name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {var_name}")
    return value

def main() -> None:
    """
    Main function to fetch Salesforce table schema and save it as a CSV file.
    """
    load_dotenv(dotenv_path=ENV_PATH)

    sf = Salesforce(
        username=_required_env("SALESFORCE_USERNAME"),
        password=_required_env("SALESFORCE_PASSWORD"),
        security_token=_required_env("SALESFORCE_SECURITY_TOKEN"),
        domain=_required_env("SALESFORCE_DOMAIN"),
    )

    table_name = _required_env("SALESFORCE_TABLE_NAME")
    sql_query = QUERY_PATH.read_text(encoding="utf-8").replace("{table_name}", table_name)

    sf_data = sf.query_all(sql_query)
    df = pd.DataFrame(sf_data["records"]).drop(columns="attributes")

    OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
    output_file = OUTPUT_PATH / f"{table_name}.csv"
    df.to_csv(output_file, index=False)

    print(f"Schema saved at: {output_file}")


if __name__ == "__main__":
    main()
