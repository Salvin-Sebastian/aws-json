# AWS Cost JSON Generator

This project contains a Python script (`generate_cost_json.py`) that uses an embedded SQLite database to query AWS resource and cost data, and generates a formatted JSON report grouped by AWS service and top cost resources.

## Setup Instructions

This script is designed to run out-of-the-box with zero configuration using Python's built-in `sqlite3` library. 

**No external database server (like PostgreSQL) is required.**

### Run the Script
Simply run the script using Python:

```bash
python generate_cost_json.py
```

Upon the first run, the script will automatically create a local `awsdb.sqlite` database file, create the necessary tables, insert mock data, and then generate the `cost_dashboard.json` file.

## Example JSON Structure

The output `cost_dashboard.json` will be formatted like this:

```json
{
  "submitted_by": "salvinsebastian@mulearn",
  "generated_at": "2025-12-10T19:37:59.381360+00:00",
  "grouped_by": "service",
  "services": {
    "EC2": [
      {
        "resource_id": "i-123",
        "total_cost": 32.6,
        "monthly_breakdown": {
          "2025-01": 10.5,
          "2025-02": 22.1
        }
      }
    ]
  },
  "top_cost_resources": [
    {
      "resource_id": "i-123",
      "monthly_cost": 32.6
    }
  ]
}
```

## Explanation of Implementation

The implementation uses Python's built-in `sqlite3` module.
- **`init_db()`**: Automatically runs on script startup to populate a local SQLite database with dummy data if it hasn't been created yet.
- **`build_by_service()`**: Uses a `JOIN` between `aws_resources` and `aws_costs`, gets dates at the month level using `strftime`, and aggregates costs. The Python logic then organizes this flat result set into a nested dictionary structure grouped by `service`, including total costs and a monthly breakdown.
- **`fetch_top_cost_resources()`**: Fetches data from the `top_cost_resources` table.
- The results are packaged into a single dictionary and dumped to `cost_dashboard.json` with indentation for readability.