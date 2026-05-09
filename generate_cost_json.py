import sqlite3
import json
import logging
from typing import Any, Dict, List
from collections import defaultdict
from datetime import datetime, UTC
import config

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def init_db():
    """Initializes the SQLite database with tables and dummy data if it doesn't exist."""
    conn = sqlite3.connect("awsdb.sqlite")
    cur = conn.cursor()
    
    cur.execute("CREATE TABLE IF NOT EXISTS aws_resources (resource_id VARCHAR(100) PRIMARY KEY, service VARCHAR(50))")
    cur.execute("CREATE TABLE IF NOT EXISTS aws_costs (id INTEGER PRIMARY KEY AUTOINCREMENT, resource_id VARCHAR(100), cost_date DATE, cost NUMERIC(10, 2))")
    cur.execute("CREATE TABLE IF NOT EXISTS top_cost_resources (resource_id VARCHAR(100) PRIMARY KEY, monthly_cost NUMERIC(10, 2))")
    
    cur.execute("SELECT COUNT(*) FROM aws_resources")
    if cur.fetchone()[0] == 0:
        cur.executemany("INSERT INTO aws_resources (resource_id, service) VALUES (?, ?)", [
            ('i-123', 'EC2'), ('i-456', 'EC2'), ('bucket-1', 'S3')
        ])
        cur.executemany("INSERT INTO aws_costs (resource_id, cost_date, cost) VALUES (?, ?, ?)", [
            ('i-123', '2025-01-15', 10.50), ('i-123', '2025-02-15', 22.10),
            ('i-456', '2025-01-20', 5.00), ('bucket-1', '2025-01-05', 2.50),
            ('bucket-1', '2025-02-10', 4.00)
        ])
        cur.executemany("INSERT INTO top_cost_resources (resource_id, monthly_cost) VALUES (?, ?)", [
            ('i-123', 32.60), ('bucket-1', 6.50), ('i-456', 5.00)
        ])
        conn.commit()
    conn.close()


def get_conn():
    conn = sqlite3.connect("awsdb.sqlite")
    conn.row_factory = sqlite3.Row
    return conn


def fetch_rows(query: str, params: tuple = None) -> List[Dict[str, Any]]:
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute(query, params or ())
        return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()


def build_by_service() -> Dict[str, List[Dict[str, Any]]]:
    q = """
    SELECT
      ar.resource_id,
      ar.service,
      strftime('%Y-%m', ac.cost_date) AS month,
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
        month = r["month"]
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


def fetch_top_cost_resources() -> List[Dict[str, Any]]:
    query = "SELECT resource_id, monthly_cost FROM top_cost_resources ORDER BY monthly_cost DESC;"
    rows = fetch_rows(query)
    for r in rows:
        r["monthly_cost"] = float(r["monthly_cost"])
    return rows


def main():
    init_db()  # Ensures the database and tables exist
    
    output = {
        "submitted_by": config.SUBMITTER_MUID,
        "generated_at": datetime.now(UTC).isoformat(),
        "grouped_by": "service",
        "services": build_by_service(),
        "top_cost_resources": fetch_top_cost_resources()
    }

    with open("cost_dashboard.json", "w") as f:
        json.dump(output, f, indent=2)

    logger.info("Wrote cost_dashboard.json successfully.")


if __name__ == "__main__":
    main()
