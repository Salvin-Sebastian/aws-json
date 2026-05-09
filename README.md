# AWS Cost JSON Generator

This project contains a Python script (`generate_cost_json.py`) that connects to a PostgreSQL database, queries AWS resource and cost data, and generates a formatted JSON report grouped by AWS service and top cost resources.

## Setup Instructions

### Dependencies
Install the required Python packages using `pip`:

```bash
pip install psycopg2-binary
```

### Database Connection

**Recommended: Using Docker**
If you have Docker installed, you can spin up the database and required tables automatically by running:
```bash
docker-compose up -d
```
This will start a PostgreSQL server on port 5432 with the credentials already configured in `config.py` and populate it with mock data.

**Manual Setup**
If you prefer not to use Docker, ensure PostgreSQL is installed and running. Create a database for your AWS cost data.

Update the connection parameters in `config.py`:

```python
# config.py
DB = {
    "host": "localhost",
    "port": 5432,
    "dbname": "your_db_name",
    "user": "your_username",
    "password": "your_password"
}
SUBMITTER_MUID = "salvinsebastian@mulearn"
```

### Required Tables
Create the following tables in your PostgreSQL database:

```sql
CREATE TABLE aws_resources (
    resource_id VARCHAR(100) PRIMARY KEY,
    service VARCHAR(50)
);

CREATE TABLE aws_costs (
    id SERIAL PRIMARY KEY,
    resource_id VARCHAR(100) REFERENCES aws_resources(resource_id),
    cost_date DATE,
    cost NUMERIC(10, 2)
);

-- Note: The script also queries a 'top_cost_resources' view or table
CREATE TABLE top_cost_resources (
    resource_id VARCHAR(100) PRIMARY KEY,
    monthly_cost NUMERIC(10, 2)
);
```

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

The implementation uses `psycopg2` with `RealDictCursor` to fetch data as Python dictionaries.
- **`build_by_service()`**: Uses a `JOIN` between `aws_resources` and `aws_costs`, truncates dates to the month level using `DATE_TRUNC`, and aggregates costs. The Python logic then organizes this flat result set into a nested dictionary structure grouped by `service`, including total costs and a monthly breakdown.
- **`fetch_top_cost_resources()`**: Fetches data from a pre-calculated table/view of top cost resources.
- The results are packaged into a single dictionary and dumped to `cost_dashboard.json` with indentation for readability.