# PostgreSQL Project

This project demonstrates the setup and usage of a PostgreSQL database with Python, including connection handling, dependency management, and basic API interactions.

## Setup Instructions

### Dependencies
Install the required Python packages using pip:

```bash
pip install psycopg2-binary flask
```

### Database Connection
Ensure PostgreSQL is installed and running on your system. Create a database named `example_db`.

Update the connection parameters in `config.py` or directly in your script:

```python
import psycopg2

conn = psycopg2.connect(
    host="localhost",
    database="example_db",
    user="your_username",
    password="your_password"
)
```

### Required Tables
Create the following table in your PostgreSQL database:

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Example JSON Structure or API Response

When querying the database via a simple Flask API, the response might look like this:

```json
{
  "users": [
    {
      "id": 1,
      "name": "John Doe",
      "email": "john@example.com",
      "created_at": "2023-10-01T12:00:00Z"
    },
    {
      "id": 2,
      "name": "Jane Smith",
      "email": "jane@example.com",
      "created_at": "2023-10-02T12:00:00Z"
    }
  ]
}
```

## Explanation of Implementation

The implementation uses `psycopg2` for PostgreSQL connectivity in Python.