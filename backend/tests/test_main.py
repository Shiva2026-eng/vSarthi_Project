def test_greet_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["message"] == "App working correctly!"
