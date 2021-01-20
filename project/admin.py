from quart import Blueprint

admin = Blueprint('admin', __name__, template_folder='admin', url_prefix='/admin/')

@admin.route('/')
async def index():
    return 'admin index'