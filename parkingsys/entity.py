import enum
from typing import Dict
from heapq import heapify
from flask import current_app, g

class ParkingSlotStatus(enum.Enum):
    VACANT = 0
    OCCUPIED = 1

def slot_factory(parking_lot_id, slot_code_start, slot_code_end, vehicle_type_id,cursor) -> list:
    """ Creates slots in the DB and returns their codes in list """
    code_list = []
    for code in range(slot_code_start,slot_code_end):
        code_list.append(code)
        cursor.execute("INSERT INTO slot (code,parking_lot_id,vehicle_type_id) VALUES (?,?,?)",(code,parking_lot_id,vehicle_type_id) )
    heapify(code_list)
    return code_list

def parking_lot_factory(name, vehicle_typewise_slots:Dict[str,int]) -> int:
    """ Creates a parking lot in the DB and returns its id """
    db_obj = g.db
    cur = db_obj.cursor()
    current_app.logger.info("Creating Parking Lot")
    cur.execute("INSERT INTO parking_lot (name) VALUES (?)", (name,))
    lot_id = cur.lastrowid
    cur.execute("SELECT vt.id, vt.name, vt.wheels FROM vehicle_type vt")
    result = cur.fetchall()
    total_slots=0
    parking_occupancy= []
    for row in result:
        cur.execute("""
            INSERT INTO parking_lot_config (parking_lot_id, vehicle_type_id, slot_count) 
            VALUES (?,?,?)
            """,
            (lot_id,row[0],vehicle_typewise_slots[row[1]])
            )

        parking_occupancy.append({
                "lot_id":lot_id,
                "vehicle_type_id": row[0],
                "slot_status": ParkingSlotStatus.VACANT.value,
                "slot_codes": slot_factory(lot_id, total_slots+1,total_slots+vehicle_typewise_slots[row[1]]+1, row[0],cur)
                })
        
        parking_occupancy.append({
            "lot_id":lot_id,
            "vehicle_type_id": row[0],
            "slot_status": ParkingSlotStatus.OCCUPIED.value,
            "slot_codes": []
            })
        total_slots+=vehicle_typewise_slots[row[1]]

    cur.close()
    db_obj.commit()            
    doc_db = g.doc_db
    occupancy = doc_db.table("occupancy")
    occupancy.insert_multiple(parking_occupancy)
    return lot_id



# class VehicleTypeWheels:
#     FOUR_WHEELER = 4
#     TWO_WHEELER = 2

# class Vehicle:
#     def __init__(self, license:str, wheels:int, db_obj) -> None:
#         self.license_number = license
#         self.wheels = wheels
#         cur = db_obj.cursor()
#         try:
#             cur.execute("""
#             INSERT INTO vehicle (license,vehicle_type_id) VALUES  (?,(SELECT vt.id FROM vehicle_type vt WHERE vt.wheels=?))
#             """,
#                 (license,wheels)
#             )
#             self.id = cur.lastrowid
#         except sqlite3.IntegrityError:
#             cur.execute("SELECT v.id FROM vehicle v WHERE v.license = ?", (license,))
#             self.id = cur.fetchall()[0][0]
#         cur.execute("SELECT vt.id FROM vehicle_type vt WHERE vt.wheels=?",(wheels,))
#         self.type_id = cur.fetchall()[0][0]
    
    

# class ParkingSpot:
#     def __init__(self, id:int, status:ParkingSlotStatus=ParkingSlotStatus.VACANT) -> None:
#         self.status = status
#         self.id = id

# class ParkingLot:
#     def __init__(self, id, init_config:Dict[int,int], obj) -> None:
#         self.init_config = init_config
#         self.id=id

#     def is_slot_available(self,vehicle_type_id:int):
#         if len(self.status[vehicle_type_id]["VACANT"]) !=0:
#             return True
#         else:
#             False

#     def park_vehicle(self, vehicle:Vehicle):
#         if self.is_slot_available(vehicle.type_id):
#             spot = self.status[vehicle.type_id]["VACANT"].pop(0)
#             self.status[vehicle.type_id]["OCCUPIED"].append(spot)
#             return spot # Update this to persistent storage
#         else:
#             raise OverflowError("No spots available for the vehicle")
    
#     def move_out(self,vehicle,spot):
#         self.status[vehicle.type_id]["OCCUPIED"].remove(spot)
#         self.status[vehicle.type_id]["VACANT"].append(spot)
#         return 



# if __name__ == "__main__":
#     DB_FILE_PATH = "instance/parkingsys.db"
#     db_obj = sqlite3.connect(DB_FILE_PATH)
#     parking_lot = parking_lot_factory("LOT_1",{"FOUR_WHEELER":4,"TWO_WHEELER":2}, db_obj)

#     v1= Vehicle("MP09LA1234", 4, db_obj)
#     parking_lot.park_vehicle(v1)
    
    
