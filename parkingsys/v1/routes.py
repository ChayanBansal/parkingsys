from parkingsys.v1 import api_bp
from parkingsys.v1.views import ParkingLotsView, ParkingLotsByIDView, VehiclesView, VehiclesParkView, ParkingLotsByIDStatusView


# requests URIs
api_bp.add_url_rule('/parking_lots/', view_func=ParkingLotsView.as_view('parking_lots'), 
                methods=['GET', 'POST'])
api_bp.add_url_rule('/parking_lots/<int:parking_lot_id>/', view_func=ParkingLotsByIDView.as_view('parking_lots_by_id'), 
                methods=['GET'])
api_bp.add_url_rule('/parking_lots/<int:parking_lot_id>/status/', view_func=ParkingLotsByIDStatusView.as_view('parking_lots_status'), 
                methods=['GET'])
api_bp.add_url_rule('/vehicles/', view_func=VehiclesView.as_view('vehicles'), 
                methods=['GET', 'POST'])
api_bp.add_url_rule('/parking_lots/<int:parking_lot_id>/park/', view_func=VehiclesParkView.as_view('vehicles_park'), 
                methods=['POST', "DELETE"])
