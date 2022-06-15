CREATE TABLE ticket
(
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, -- primary key column
    start_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    end_time DATETIME,
    charges DECIMAL,
    parking_lot_id INTEGER NOT NULL REFERENCES parking_lot (id),
    vehicle_id INTEGER NOT NULL REFERENCES vehicle (id)
);