from datetime import datetime, timezone, timedelta


def test_create_follow_up(client, sample_customer, rep_headers):
    due = datetime.now(timezone.utc) + timedelta(days=2)
    payload = {
        "customer_id": sample_customer.id,
        "title": "Send updated contract draft",
        "description": "Include requested discount clause",
        "follow_up_type": "EMAIL",
        "scheduled_at": due.isoformat(),
        "completed": False
    }
    response = client.post("/api/follow-ups", json=payload, headers=rep_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Send updated contract draft"
    assert data["follow_up_type"] == "EMAIL"
    assert data["completed"] is False


def test_mark_follow_up_completed(client, sample_customer, rep_headers):
    due = datetime.now(timezone.utc) + timedelta(hours=3)
    create_res = client.post("/api/follow-ups", json={
        "customer_id": sample_customer.id,
        "title": "Call CEO",
        "scheduled_at": due.isoformat()
    }, headers=rep_headers)
    fu_id = create_res.json()["id"]

    # Mark completed
    update_res = client.put(f"/api/follow-ups/{fu_id}", json={"completed": True}, headers=rep_headers)
    assert update_res.status_code == 200
    assert update_res.json()["completed"] is True


def test_filter_follow_ups(client, sample_customer, rep_headers):
    today = datetime.now(timezone.utc) + timedelta(hours=1)
    future = datetime.now(timezone.utc) + timedelta(days=5)

    client.post("/api/follow-ups", json={
        "customer_id": sample_customer.id,
        "title": "Call Today",
        "scheduled_at": today.isoformat()
    }, headers=rep_headers)

    client.post("/api/follow-ups", json={
        "customer_id": sample_customer.id,
        "title": "Call Future",
        "scheduled_at": future.isoformat()
    }, headers=rep_headers)

    res_all = client.get("/api/follow-ups?filter_status=all", headers=rep_headers)
    assert res_all.status_code == 200
    assert len(res_all.json()) >= 2

    res_today = client.get("/api/follow-ups?filter_status=today", headers=rep_headers)
    assert res_today.status_code == 200
    assert any(f["title"] == "Call Today" for f in res_today.json())


def test_delete_follow_up(client, sample_customer, rep_headers):
    create_res = client.post("/api/follow-ups", json={
        "customer_id": sample_customer.id,
        "title": "Quick ping",
        "scheduled_at": datetime.now(timezone.utc).isoformat()
    }, headers=rep_headers)
    fu_id = create_res.json()["id"]

    del_res = client.delete(f"/api/follow-ups/{fu_id}", headers=rep_headers)
    assert del_res.status_code == 204

    get_res = client.get(f"/api/follow-ups/{fu_id}")
    assert get_res.status_code == 404
