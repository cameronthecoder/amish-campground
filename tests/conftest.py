import pytest, asyncio
from project import create_app

@pytest.fixture(scope="module")
def event_loop(request):
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()

@pytest.mark.asyncio
@pytest.fixture(scope="module")
async def create_test_app():
    quart_app = create_app(testing=True)
    await quart_app.startup()
    yield quart_app
    await quart_app.db.disconnect()

@pytest.fixture
def create_test_client(create_test_app):
    return create_test_app.test_client()