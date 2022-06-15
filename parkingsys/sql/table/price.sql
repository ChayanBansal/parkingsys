CREATE TABLE price
(
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, -- primary key column
    vehicle_type_id INTEGER NOT NULL REFERENCES vehicle_type(id),
    per_hour_rate DECIMAL NOT NULL
)