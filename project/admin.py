from quart import Blueprint

admin = Blueprint('admin', __name__, template_folder='admin', url_prefix='/admin/')

