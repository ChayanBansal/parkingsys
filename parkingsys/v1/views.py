from flask import current_app, g, request, jsonify
from flask.views import MethodView
from tinydb import Query
from parkingsys.entity import parking_lot_factory
from heapq import heapify,heappop,heappush
import sqlite3


class ParkingLotsView(MethodView):

    def post(self):
        """
        {
            "name": "LOT_1",
            "config": {
                "FOUR_WHEELER":4,
                "TWO_WHEELER":2
                }
        }
        """
        input_json = request.get_json()
        current_app.logger.info(str(input_json))
        try:
            lot_id = parking_lot_factory(input_json["name"], input_json["config"])
        except sqlite3.IntegrityError:
            return "Try another name"
        return {"lot_id": lot_id},200

    def get(self):
        query = """
                SELECT pl.id, pl.name as parking_lot,vt.name as vehicle_type,plc.slot_count
                FROM parking_lot pl, vehicle_type vt, parking_lot_config plc
                WHERE pl.id = plc.parking_lot_id AND plc.vehicle_type_id=vt.id
                """
        cur = g.db.cursor()
        cur.execute(query)
        result = cur.fetchall()
        r = [dict((cur.description[i][0], value) \
            for i, value in enumerate(row)) for row in result]
        return jsonify(r),200

class ParkingLotsByIDView(MethodView):

    def get(self,parking_lot_id):
        query = """
                SELECT pl.id, pl.name as parking_lot,vt.name as vehicle_type,plc.slot_count
                FROM parking_lot pl, vehicle_type vt, parking_lot_config plc
                WHERE pl.id = plc.parking_lot_id AND plc.vehicle_type_id=vt.id
                AND pl.id = ?
                """
        cur = g.db.cursor()
        cur.execute(query, (parking_lot_id,))
        result = cur.fetchall()
        r = [dict((cur.description[i][0], value) \
            for i, value in enumerate(row)) for row in result]
        return jsonify(r),200

class ParkingLotsByIDStatusView(MethodView):
    def get(self,parking_lot_id):
        occupancy = g.doc_db.table("occupancy")
        lot = Query()
        pl_occ = occupancy.search(lot.lot_id==parking_lot_id)
        cur = g.db.cursor()
        cur.execute("SELECT SUM(charges) as tolal_billing FROM ticket WHERE DATE(end_time)=DATE()")
        total_billing = cur.fetchall()[0][0]
        return {
            "occupancy": pl_occ,
            "total_billing": total_billing
        },200

class VehiclesView(MethodView):
    def get(self):
        cur = g.db.cursor()
        cur.execute("SELECT v.id, v.license, vt.id as type_id, vt.name as type, vt.wheels FROM vehicle v, vehicle_type vt WHERE v.vehicle_type_id=vt.id")
        result = cur.fetchall()
        r = [dict((cur.description[i][0], value) \
            for i, value in enumerate(row)) for row in result]
        return jsonify(r),200
    
    def post(self):
        """
        {
            "license": "MP09LA1234",
            "wheels": 4
        }
        """
        input_json = request.get_json()
        license_number = input_json["license"]
        wheels = input_json["wheels"]
        cur = g.db.cursor()
        try:
            cur.execute("""
            INSERT INTO vehicle (license,vehicle_type_id) VALUES  (?,(SELECT vt.id FROM vehicle_type vt WHERE vt.wheels=?))
            """,
                (license_number,wheels)
            )
            id = cur.lastrowid
        except sqlite3.IntegrityError:
            cur.execute("SELECT v.id FROM vehicle v WHERE v.license = ?", (license_number,))
            id = cur.fetchall()[0][0]
        cur.execute("SELECT vt.id, vt.name FROM vehicle_type vt WHERE vt.wheels=?",(wheels,))
        result = cur.fetchall()
        g.db.commit()
        return jsonify({"id":id, "license":license_number, "wheels":wheels, "type_id": result[0][0], "type":result[0][1]}),200

class VehiclesParkView(MethodView):
    
    @staticmethod
    def get_vacant_slot(lot_id, vehicle_type_id:int, rush_hour=False)-> int:
        """ Returns vacant slot if available """
        current_app.logger.info("{}, {}".format(lot_id,vehicle_type_id))
        occupancy = g.doc_db.table("occupancy")
        lot = Query()
        if rush_hour:
            # TODO
            pass
        else:
            pl_occ = occupancy.search((lot.lot_id==lot_id) & (lot.vehicle_type_id==vehicle_type_id) & (lot.slot_status==0))[0]
            try:
                vacant_slot=heappop(pl_occ['slot_codes'])
                occupancy.update(pl_occ,(lot.lot_id==lot_id) & (lot.vehicle_type_id==vehicle_type_id) & (lot.slot_status==0))
                return vacant_slot
            except IndexError:
                return -1
    
    @staticmethod
    def park_vehicle(lot_id,vehicle_type_id,slot):
        """ Updates the doc db in order to park the vehicle"""
        occupancy = g.doc_db.table("occupancy")
        lot = Query()
        pl_occ = occupancy.search((lot.lot_id==lot_id) & (lot.vehicle_type_id==vehicle_type_id) & (lot.slot_status==1))[0]
        heappush(pl_occ['slot_codes'],slot)
        occupancy.upsert(pl_occ)
        return True
    
    @staticmethod
    def vacate_parking(lot_id,vehicle_type_id,slot):
        """ Updates the doc db in order to vacate the parking """
        occupancy = g.doc_db.table("occupancy")
        lot = Query()
        pl_occ = occupancy.search((lot.lot_id==lot_id) & (lot.vehicle_type_id==vehicle_type_id) & (lot.slot_status==1))[0]
        try:
            pl_occ['slot_codes'].remove(slot)
            heapify(pl_occ['slot_codes'])
            occupancy.upsert(pl_occ)
            pl_vac = occupancy.search((lot.lot_id==lot_id) & (lot.vehicle_type_id==vehicle_type_id) & (lot.slot_status==0))[0]
            heappush(pl_vac['slot_codes'],slot)
            occupancy.upsert(pl_vac)
            return True
        except:
            return False
    
    def post(self,parking_lot_id):
        """
        {"vehicle_id": 1}
        """
        input_json = request.get_json()
        vehicle_id = input_json["vehicle_id"]
        cur = g.db.cursor()
        cur.execute("SELECT vehicle_type_id FROM vehicle WHERE id=?", (vehicle_id,))
        vehicle_type_id = cur.fetchall()[0][0]
        vacant_slot = VehiclesParkView.get_vacant_slot(parking_lot_id,vehicle_type_id)
        if vacant_slot!=-1:
            parked = VehiclesParkView.park_vehicle(parking_lot_id,vehicle_type_id,vacant_slot)
            if parked is True:
                cur.execute("INSERT INTO ticket (vehicle_id,parking_lot_id) VALUES (?,?)", (vehicle_id,parking_lot_id))
                ticket_id = cur.lastrowid
                cur.execute("UPDATE slot SET current_ticket_id = ?, status=1 WHERE parking_lot_id=? AND code = ?", (ticket_id,parking_lot_id,vacant_slot))
                g.db.commit()
                cur.close()
                return {"ticket_id": ticket_id},200
        g.db.commit()
        cur.close()
        return "Couldn't park"
    
    def delete(self,parking_lot_id):
        """
        {"ticket_id":1}
        """
        input_json = request.get_json()
        ticket_id = input_json["ticket_id"]
        cur = g.db.cursor()
        cur.execute("SELECT id, code FROM slot WHERE current_ticket_id=?",(ticket_id,))
        result = cur.fetchall()
        if len(result)!=0:
            slot_id, slot_code = result[0]
            cur.execute("UPDATE slot SET current_ticket_id=? AND status=0 WHERE id=?", (None,slot_id))
            cur.execute("SELECT v.vehicle_type_id FROM vehicle v, ticket t WHERE t.vehicle_id = v.id AND t.id=?",(ticket_id,))
            vehicle_type_id = cur.fetchall()[0][0]
            cur.execute("""
                UPDATE ticket 
                SET 
                    end_time = CURRENT_TIMESTAMP,
                    charges = ROUND((JULIANDAY(CURRENT_TIMESTAMP)-JULIANDAY(start_time))*24*60*10)
                WHERE
                    id = ?
            """, (ticket_id,)) # fixing cost to 10 rs per minute
            cur.execute("SELECT * FROM ticket WHERE id = ?", (ticket_id,))
            r = [dict((cur.description[i][0], value) \
                for i, value in enumerate(row)) for row in cur.fetchall()][0]

            g.db.commit()
            cur.close()
            if VehiclesParkView.vacate_parking(parking_lot_id,vehicle_type_id,slot_code):
                return jsonify(r),200
            else:
                return "Couldn't vacate"
        return "No Slot Allocated to Ticket"
