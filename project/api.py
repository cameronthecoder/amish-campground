from quart import Blueprint, request, current_app, jsonify, abort, render_template
from datetime import date
from async_sender import Message
import stripe

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

    sql = """
    SELECT id, name from site WHERE id NOT IN (
        SELECT site_id FROM reservation
            INNER JOIN site ON site.id = reservation.site_id

            WHERE (start_date <= :arrival_date AND end_date >= :arrival_date)
                OR (start_date < :departure_date AND end_date >= :departure_date)
                OR (:arrival_date <= start_date AND :departure_date >= start_date)
    );
    """

    q = await current_app.db.fetch_all(sql, values={'arrival_date': start, 'departure_date': end})

    sites = []

    for row in q:
        sites.append({"id": row[0], "name": row[1]})

    print(q)
    print(sites)

    return jsonify({"available_sites": sites, "delta": (end - start).days})


@api.route('/reservation/')
async def get_reservations():
    sql = "SELECT * FROM reservation"
    result = await current_app.db.fetch_all(sql)

    reservations = []

    for row in result:
        reservations.append({
            'id': row[0],
            'first_name': row[1],
            'last_name': row[2],
            'arrival_date': row[3],
            'departure_date': row[4],
            'site_id': row[5],
            'stripe_session_id': row[6],
            'email': row[7],
            'paid': row[8]
        })
    return jsonify(reservations)


@api.route('/reservation/', methods=["POST"])
async def create_reservation():
    stripe.api_key = current_app.config['STRIPE_SECRET_KEY']
    json = (await request.get_json())

    sql = 'INSERT INTO reservation(first_name, last_name, site_id, start_date, end_date, stripe_session_id, email) VALUES (:first_name, :last_name, :site_id, :start_date, :end_date, :stripe_session_id, :email)'

    try:
        arrival_date = date.fromisoformat(json['arrival_date'])
        departure_date = date.fromisoformat(json['departure_date'])
    except ValueError:
        return {
            'error': 'Both dates are required to be in ISO format.',
            'status': 400
        }, 400

    site = await current_app.db.fetch_one("SELECT name FROM site WHERE id = :id", values={'id': json['site_id']})


    delta = (departure_date - arrival_date).days
    price = 35 * delta
    session = stripe.checkout.Session.create(
        submit_type="pay",
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': f'{site[0]} ({str((departure_date - arrival_date).days)} night stay; $35/night)',
                    },
                    'unit_amount': price * 100,
                    },
            'quantity': 1,
        }],
        customer_email=json['email'],
        mode='payment',
        success_url='http://127.0.0.1:8000/reserve/success?session_id={CHECKOUT_SESSION_ID}',
        cancel_url='http://127.0.0.1:8000/cancel',
    )

    data = {'first_name': json['first_name'], 'last_name': json['last_name'],
            'site_id': json['site_id'], 'start_date': arrival_date, 'end_date': departure_date, 'stripe_session_id': session.id, 'email': json['email']}

    await current_app.db.execute(sql, values=data)

    return jsonify(data)

@api.route('/stripe-webhook/', methods=['POST'])
async def my_webhook_view():
    payload = (await request.get_json())
    event = None
    stripe.api_key = current_app.config['STRIPE_SECRET_KEY']

    try:
        event = stripe.Event.construct_from(
            payload, stripe.api_key
        )
    except ValueError as e:
        # Invalid payload
        return abort(400)

    # Handle the event
    if event.type == 'checkout.session.completed':
        payment_intent = event.data.object # contains a stripe.PaymentIntent
        await current_app.db.execute("UPDATE reservation SET paid = true WHERE stripe_session_id = :stripe_session_id", values={'stripe_session_id': payment_intent.id})
        reservation = await current_app.db.fetch_one("SELECT * FROM reservation WHERE stripe_session_id = :stripe_session_id", values={'stripe_session_id': payment_intent.id})
        msg = Message(f"Thank you for your reservation {reservation[1]}!", from_address="camnooten@gmail.com",
              to=reservation[7], html=(await render_template('email/reservation.html', reservation=reservation)))
        await current_app.mail.send(msg)
        return 'ok'
    else:
        return 'yay'
        