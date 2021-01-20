import pytest

@pytest.mark.asyncio
async def test_site_availability_without_params(create_test_client):
    response = await create_test_client.get('/api/get-available-sites/')
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_site_availability_invalid_params(create_test_client):
    response = await create_test_client.get('/api/get-available-sites/?arrival_date=2021&departure_date=2022')
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_site_availability_future(create_test_client):
    response = await create_test_client.get("/api/get-available-sites/?arrival_date=2021-09-20&departure_date=2021-09-25")
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_site_availability_departure_date_before_arrival_date(create_test_client):
    response = await create_test_client.get("/api/get-available-sites/?arrival_date=2021-09-25&departure_date=2021-09-24")
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_reservation_api(create_test_client):
    response = await create_test_client.get("/api/reservation/")
    assert response.status_code == 200

