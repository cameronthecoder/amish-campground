from quart import Blueprint, render_template, current_app, request, redirect, url_for
import stripe

view = Blueprint('view', __name__)
@view.route('/')
async def index():
    return await render_template('index.html')

@view.route('/reserve/')
async def reserve():
    return await render_template('reserve.html', STRIPE_TEST_KEY=current_app.config['STRIPE_PUBLISHABLE_KEY'])

@view.route('/reserve/success/')
async def reserve_success():
    stripe.api_key = current_app.config['STRIPE_SECRET_KEY']
    session_id = request.args.get('session_id')

    if not session_id:
        return redirect(url_for('index'))

    session = stripe.checkout.Session.retrieve(session_id)

    return await render_template('reserve_success.html', session=session)

@view.route('/rates-and-reservations/')
async def rates_and_reservations():
    return 'Rates and Reservations Page'

@view.route('/amenities/')
async def amenities():
    return 'Amenities Page'

@view.route('/about/')
async def about():
    return 'About Page'