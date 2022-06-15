CREATE TABLE slot
(
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, -- primary key column
    status BOOLEAN NOT NULL DEFAULT 0,
    vehicle_type_id INTEGER NOT NULL REFERENCES vehicle_type (id),
    parking_lot_id INTEGER NOT NULL REFERENCES parking_lot (id),
    code INTEGER NOT NULL,
    current_ticket_id INTEGER REFERENCES ticket (id)
);