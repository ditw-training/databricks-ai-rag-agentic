"""Smoke test of the trainer workspace created by this Terraform stack.

Usage: python smoke_test.py [--profile mct]
       (without --profile the CLI reads DATABRICKS_HOST and DATABRICKS_TOKEN from the environment)
Needs only the Databricks CLI. Creates and drops one tiny table in the workshop catalog.
"""
import argparse
import json
import subprocess
import time

CATALOG = "workspace"
SCHEMA = "default"
LLM = "databricks-meta-llama-3-3-70b-instruct"
EMBEDDING = "databricks-gte-large-en"

results: list[tuple[str, bool, str]] = []


def cli(profile: str | None, *args: str, body: dict | None = None) -> dict | list:
    cmd = ["databricks", *args, *(["-p", profile] if profile else []), "-o", "json"]
    if body is not None:
        cmd += ["--json", json.dumps(body)]
    done = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    if done.returncode != 0:
        raise RuntimeError((done.stderr or done.stdout).strip().splitlines()[-1])
    return json.loads(done.stdout) if done.stdout.strip() else {}


def check(name: str):
    def wrap(fn):
        try:
            detail = fn()
            results.append((name, True, str(detail)))
        except Exception as exc:  # report every check, never stop at the first failure
            results.append((name, False, str(exc)[:300]))
        return fn
    return wrap


def sql(profile: str | None, warehouse_id: str, statement: str) -> list:
    response = cli(profile, "api", "post", "/api/2.0/sql/statements",
                   body={"warehouse_id": warehouse_id, "statement": statement, "wait_timeout": "50s"})
    while response["status"]["state"] in ("PENDING", "RUNNING"):
        time.sleep(5)
        response = cli(profile, "api", "get", f"/api/2.0/sql/statements/{response['statement_id']}")
    if response["status"]["state"] != "SUCCEEDED":
        raise RuntimeError(response["status"].get("error", {}).get("message", response["status"]["state"]))
    return response.get("result", {}).get("data_array", [])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", default=None)
    profile = parser.parse_args().profile

    check("identity")(lambda: cli(profile, "current-user", "me")["userName"])

    @check("catalog on ADLS")
    def _():
        root = cli(profile, "catalogs", "get", CATALOG).get("storage_root", "")
        assert root.startswith("abfss://"), f"storage_root={root!r}"
        return root

    for endpoint in (LLM, EMBEDDING):
        check(f"model endpoint {endpoint}")(lambda e=endpoint: cli(profile, "serving-endpoints", "get", e)["state"]["ready"])

    @check("chat completion")
    def _():
        reply = cli(profile, "serving-endpoints", "query", LLM,
                    body={"messages": [{"role": "user", "content": "Odpowiedz jednym słowem: OK"}], "max_tokens": 5})
        return reply["choices"][0]["message"]["content"].strip()

    warehouses = []

    @check("SQL warehouse")
    def _():
        warehouses.extend(cli(profile, "warehouses", "list"))
        assert warehouses, "no warehouse"
        return ", ".join(f"{w['name']} ({w['state']})" for w in warehouses)

    if warehouses:
        wid = warehouses[0]["id"]
        table = f"{CATALOG}.{SCHEMA}.smoke_test_adls"

        @check("managed table lands on ADLS")
        def _():
            sql(profile, wid, f"CREATE OR REPLACE TABLE {table} AS SELECT 1 AS id")
            location = sql(profile, wid, f"DESCRIBE DETAIL {table}")[0]
            sql(profile, wid, f"DROP TABLE {table}")
            path = next(v for v in location if isinstance(v, str) and v.startswith("abfss://"))
            return path

        check("samples.bakehouse")(lambda: sql(profile, wid, "SELECT count(*) FROM samples.bakehouse.sales_transactions")[0][0])
        check("ai_query")(lambda: sql(profile, wid, f"SELECT ai_query('{LLM}', 'Odpowiedz jednym słowem: OK')")[0][0])

    check("AI Search API")(lambda: f"{len(cli(profile, 'vector-search-endpoints', 'list-endpoints'))} endpoint(s)")
    check("Databricks Apps API")(lambda: f"{len(cli(profile, 'apps', 'list'))} app(s)")

    @check("managed MCP (system.ai functions)")
    def _():
        reply = cli(profile, "api", "post", "/api/2.0/mcp/functions/system/ai",
                    body={"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
        return f"{len(reply.get('result', {}).get('tools', []))} tool(s)"

    width = max(len(name) for name, _, _ in results)
    for name, ok, detail in results:
        print(f"{'✅' if ok else '❌'} {name:<{width}}  {detail}")
    return 0 if all(ok for _, ok, _ in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
