import pytest

@pytest.mark.asyncio
async def test_index(create_test_client):
    response = await create_test_client.get("/")
    assert response.status_code == 200