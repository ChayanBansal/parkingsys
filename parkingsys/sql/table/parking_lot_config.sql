CREATE TABLE parking_lot_config
(
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, -- primary key column
    parking_lot_id INTEGER NOT NULL REFERENCES parking_lot (id),
    vehicle_type_id INTEGER NOT NULL REFERENCES vehicle_type (id),
    slot_count INTEGER NOT NULL DEFAULT 1
);
