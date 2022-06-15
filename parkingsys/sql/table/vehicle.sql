CREATE TABLE vehicle
(
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, -- primary key column
    license [NVARCHAR](10) NOT NULL UNIQUE,
    vehicle_type_id INTEGER NOT NULL REFERENCES vehicle_type (id)
);
