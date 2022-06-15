CREATE TABLE vehicle_type
(
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, -- primary key column
    name [NVARCHAR](50) NOT NULL,
    wheels INTEGER NOT NULL
);