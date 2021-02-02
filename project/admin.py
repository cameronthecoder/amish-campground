from quart import Blueprint, render_template

admin = Blueprint('admin', __name__, url_prefix='/admin/')

@admin.route('/')
async def index():
    return await render_template('admin/base.html')