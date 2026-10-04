def test_create_opportunity(client, sample_customer, rep_headers):
    payload = {
        "customer_id": sample_customer.id,
        "title": "Enterprise Cloud Expansion",
        "description": "500-seat annual subscription",
        "amount": 75000.0,
        "stage": "QUALIFIED",
        "probability": 60.0
    }
    response = client.post("/api/opportunities", json=payload, headers=rep_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Enterprise Cloud Expansion"
    assert data["amount"] == 75000.0
    assert data["stage"] == "QUALIFIED"
    assert data["customer_id"] == sample_customer.id


def test_list_opportunities(client, sample_customer, rep_headers):
    client.post("/api/opportunities", json={
        "customer_id": sample_customer.id,
        "title": "Deal 1",
        "amount": 20000.0,
        "stage": "LEAD"
    }, headers=rep_headers)
    client.post("/api/opportunities", json={
        "customer_id": sample_customer.id,
        "title": "Deal 2",
        "amount": 50000.0,
        "stage": "PROPOSAL"
    }, headers=rep_headers)

    response = client.get(f"/api/opportunities?customer_id={sample_customer.id}", headers=rep_headers)
    assert response.status_code == 200
    deals = response.json()
    assert len(deals) >= 2


def test_update_opportunity_stage(client, sample_customer, rep_headers):
    res = client.post("/api/opportunities", json={
        "customer_id": sample_customer.id,
        "title": "Deal to Move",
        "amount": 40000.0,
        "stage": "NEGOTIATION"
    }, headers=rep_headers)
    opp_id = res.json()["id"]

    update_res = client.put(f"/api/opportunities/{opp_id}", json={
        "stage": "WON",
        "probability": 100.0
    }, headers=rep_headers)
    assert update_res.status_code == 200
    data = update_res.json()
    assert data["stage"] == "WON"
    assert data["probability"] == 100.0


def test_delete_opportunity(client, sample_customer, rep_headers):
    res = client.post("/api/opportunities", json={
        "customer_id": sample_customer.id,
        "title": "Deal to Delete",
        "amount": 10000.0,
        "stage": "LOST"
    }, headers=rep_headers)
    opp_id = res.json()["id"]

    del_res = client.delete(f"/api/opportunities/{opp_id}", headers=rep_headers)
    assert del_res.status_code == 204

    get_res = client.get(f"/api/opportunities/{opp_id}")
    assert get_res.status_code == 404
