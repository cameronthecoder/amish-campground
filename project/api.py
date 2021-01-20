from quart import Blueprint, request, current_app, jsonify
from datetime import date

api = Blueprint('api', __name__, url_prefix='/api/')

@api.route('/get-available-sites/')
async def get_available_sites():
    arrival_date = request.args.get('arrival_date')
    departure_date = request.args.get('departure_date')

    # Validation
    if not arrival_date or not departure_date:
        return {
            'error': 'You must provide a arrival_date and departure_date parameter in ISO format.',
            'status': 400
        }, 400

    # Check if start date or end date is in the future
    today = date.today()
    try:
        start = date.fromisoformat(arrival_date)
        end = date.fromisoformat(departure_date)
    except ValueError:
        return {
            'error': 'Both dates are required to be in ISO format.',
            'status': 400
        }, 400

    if start < today or end < today:
        return {
            'error': 'The arrival and departure dates can not be in the past.',
            'status': 400
        }, 400
        
    # Check if end date comes before start date
    if end < start:
        return {
            'error': 'The departure date cannot be before the arrival date.',
            'status': 400
        }, 400

    sql = f"""
    SELECT id,name from site WHERE id NOT IN (
        SELECT site_id FROM reservation
            INNER JOIN site ON site.id = reservation.site_id

            WHERE (start_date <= "{arrival_date}" AND end_date >= "{arrival_date}")
                OR (start_date < "{departure_date}" AND end_date >= "{departure_date}" )
                OR ("{arrival_date}" <= start_date AND "{departure_date}" >= start_date)
    )
    """


    q = await current_app.db.fetch_all(sql)

    sites = []

    for id, name in q:
        sites.append({"id": id, "name": name})

    return jsonify({"available_sites": sites})

@api.route('/reservation/')
async def get_reservations():
    sql = "SELECT * FROM reservation"
    result = await current_app.db.fetch_all(sql)

    reservations = []

    for id, first_name, last_name, start_date, end_date, site_id in result:
        reservations.append({
            'id': id,
            'first_name': first_name,
            'last_name': last_name,
            'start_date': start_date,
            'end_date': end_date,
            'site_id': site_id
            })
    return jsonify(reservations)
