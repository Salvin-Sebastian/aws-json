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

CREATE TABLE top_cost_resources (
    resource_id VARCHAR(100) PRIMARY KEY,
    monthly_cost NUMERIC(10, 2)
);

-- Insert dummy data to match the expected JSON output
INSERT INTO aws_resources (resource_id, service) VALUES
('i-123', 'EC2'),
('i-456', 'EC2'),
('bucket-1', 'S3');

INSERT INTO aws_costs (resource_id, cost_date, cost) VALUES
('i-123', '2025-01-15', 10.50),
('i-123', '2025-02-15', 22.10),
('i-456', '2025-01-20', 5.00),
('bucket-1', '2025-01-05', 2.50),
('bucket-1', '2025-02-10', 4.00);

INSERT INTO top_cost_resources (resource_id, monthly_cost) VALUES
('i-123', 32.60),
('bucket-1', 6.50),
('i-456', 5.00);
