def test_create_activity_for_customer(client, sample_customer, rep_headers):
    payload = {
        "activity_type": "CALL",
        "title": "Discovery call with VP of Sales",
        "description": "Reviewed pricing and implementation schedule."
    }
    response = client.post(
        f"/api/customers/{sample_customer.id}/activities",
        json=payload,
        headers=rep_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Discovery call with VP of Sales"
    assert data["activity_type"] == "CALL"
    assert data["customer_id"] == sample_customer.id


def test_get_activities_for_customer_timeline(client, sample_customer, rep_headers):
    client.post(
        f"/api/customers/{sample_customer.id}/activities",
        json={"activity_type": "EMAIL", "title": "Sent follow-up deck"},
        headers=rep_headers
    )
    client.post(
        f"/api/customers/{sample_customer.id}/activities",
        json={"activity_type": "DEMO", "title": "Platform walkthrough"},
        headers=rep_headers
    )

    response = client.get(f"/api/customers/{sample_customer.id}/activities")
    assert response.status_code == 200
    activities = response.json()
    assert len(activities) >= 2
    # Verify newest first
    assert activities[0]["title"] == "Platform walkthrough"


def test_get_activity_by_id(client, sample_customer, rep_headers):
    create_res = client.post(
        f"/api/customers/{sample_customer.id}/activities",
        json={"activity_type": "MEETING", "title": "Quarterly business review"},
        headers=rep_headers
    )
    act_id = create_res.json()["id"]

    get_res = client.get(f"/api/activities/{act_id}")
    assert get_res.status_code == 200
    assert get_res.json()["title"] == "Quarterly business review"


def test_delete_activity(client, sample_customer, rep_headers):
    create_res = client.post(
        f"/api/customers/{sample_customer.id}/activities",
        json={"activity_type": "NOTE", "title": "Temporary note"},
        headers=rep_headers
    )
    act_id = create_res.json()["id"]

    del_res = client.delete(f"/api/activities/{act_id}", headers=rep_headers)
    assert del_res.status_code == 204

    get_res = client.get(f"/api/activities/{act_id}")
    assert get_res.status_code == 404
