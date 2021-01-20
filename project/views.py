from quart import Blueprint, render_template

view = Blueprint('view', __name__)
from project.config import Config

@view.route('/')
async def index():
    return await render_template('index.html')

@view.route('/reserve/')
async def reserve():
    return 'Reserve Page'

@view.route('/rates-and-reservations/')
async def rates_and_reservations():
    return 'Rates and Reservations Page'

@view.route('/about/')
async def about():
    return 'About Page'