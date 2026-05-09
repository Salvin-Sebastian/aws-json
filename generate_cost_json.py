import psycopg2
import json
from collections import defaultdict
from datetime import datetime, UTC
import config


def get_conn():
    c = config.DB
    return psycopg2.connect(
        host=c["host"],
        port=c["port"],
        dbname=c["dbname"],
        user=c["user"],
        password=c["password"]
    )


def fetch_rows(query, params=None):
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(query, params or ())
            cols = [desc[0] for desc in cur.description]
            rows = [dict(zip(cols, row)) for row in cur.fetchall()]
            return rows
    finally:
        conn.close()


def build_by_service():
    """
    Group monthly cost per resource per service.
    Uses REAL column names:
    - aws_costs.cost_date
    - aws_costs.cost
    - aws_resources.service
    """

    q = """
    SELECT
      ar.resource_id,
      ar.service,
      DATE_TRUNC('month', ac.cost_date)::date AS month,
      SUM(ac.cost) AS total_cost
    FROM aws_resources ar
    JOIN aws_costs ac ON ar.resource_id = ac.resource_id
    GROUP BY ar.resource_id, ar.service, month
    ORDER BY ar.service, ar.resource_id, month;
    """

    rows = fetch_rows(q)

    services = {}
    temp = defaultdict(lambda: defaultdict(lambda: {"total_cost": 0.0, "monthly_breakdown": {}}))

    for r in rows:
        service = r["service"] or "unknown"
        resource = r["resource_id"]
        month = r["month"].strftime("%Y-%m")
        cost = float(r["total_cost"])

        temp[service][resource]["total_cost"] += cost
        temp[service][resource]["monthly_breakdown"][month] = (
            temp[service][resource]["monthly_breakdown"].get(month, 0.0) + cost
        )

    for srv, resources in temp.items():
        services[srv] = []
        for rid, info in resources.items():
            services[srv].append({
                "resource_id": rid,
                "total_cost": round(info["total_cost"], 4),
                "monthly_breakdown": {
                    k: round(v, 4) for k, v in sorted(info["monthly_breakdown"].items())
                }
            })

    return services


def fetch_top_cost_resources():
    query = "SELECT resource_id, monthly_cost FROM top_cost_resources ORDER BY monthly_cost DESC;"
    rows = fetch_rows(query)
    for r in rows:
        r["monthly_cost"] = float(r["monthly_cost"])
    return rows


def main():
    output = {
        "submitted_by": config.SUBMITTER_MUID,
        "generated_at": datetime.now(UTC).isoformat(),
        "grouped_by": "service",
        "services": build_by_service(),
        "top_cost_resources": fetch_top_cost_resources()
    }

    with open("cost_dashboard.json", "w") as f:
        json.dump(output, f, indent=2)

    print("Wrote cost_dashboard.json successfully.")


if __name__ == "__main__":
    main()
