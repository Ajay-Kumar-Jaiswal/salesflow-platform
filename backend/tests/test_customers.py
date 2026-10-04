def test_create_customer_success(client, rep_headers):
    payload = {
        "name": "Wayne Enterprises",
        "email": "bruce@wayne-enterprises.com",
        "phone": "+1-555-0987",
        "company": "Wayne Enterprises",
        "industry": "Defense & Tech",
        "status": "QUALIFIED",
        "source": "Referral",
        "notes": "Interested in premium CRM"
    }
    response = client.post("/api/customers", json=payload, headers=rep_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Wayne Enterprises"
    assert data["email"] == "bruce@wayne-enterprises.com"
    assert data["status"] == "QUALIFIED"
    assert data["id"] is not None


def test_create_customer_invalid_email(client, rep_headers):
    payload = {
        "name": "Stark Industries",
        "email": "invalid-email-string"
    }
    response = client.post("/api/customers", json=payload, headers=rep_headers)
    assert response.status_code == 422


def test_create_customer_missing_name(client, rep_headers):
    payload = {
        "email": "tony@stark.com"
    }
    response = client.post("/api/customers", json=payload, headers=rep_headers)
    assert response.status_code == 422


def test_get_customer_by_id(client, sample_customer):
    response = client.get(f"/api/customers/{sample_customer.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == sample_customer.id
    assert data["name"] == sample_customer.name


def test_get_customer_not_found(client):
    response = client.get("/api/customers/999999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_update_customer(client, sample_customer, rep_headers):
    update_data = {
        "company": "Acme Global Industries",
        "status": "PROPOSAL"
    }
    response = client.put(f"/api/customers/{sample_customer.id}", json=update_data, headers=rep_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["company"] == "Acme Global Industries"
    assert data["status"] == "PROPOSAL"
    assert data["name"] == sample_customer.name  # unchanged


def test_delete_customer(client, sample_customer, admin_headers):
    del_res = client.delete(f"/api/customers/{sample_customer.id}", headers=admin_headers)
    assert del_res.status_code == 204

    # Verify deleted
    get_res = client.get(f"/api/customers/{sample_customer.id}")
    assert get_res.status_code == 404


def test_customer_search_and_filter(client, db):
    from app.models.customer import Customer
    c1 = Customer(name="Alpha Corp", email="alpha@corp.com", company="Alpha LLC", status="LEAD")
    c2 = Customer(name="Beta Ltd", email="beta@corp.com", company="Beta Group", status="WON")
    c3 = Customer(name="Gamma Inc", email="gamma@corp.com", company="Alpha Subsidiary", status="LEAD")
    db.add_all([c1, c2, c3])
    db.commit()

    # Search by keyword
    search_res = client.get("/api/customers?search=Alpha")
    assert search_res.status_code == 200
    items = search_res.json()["items"]
    assert len(items) >= 2

    # Filter by status
    filter_res = client.get("/api/customers?status=WON")
    assert filter_res.status_code == 200
    won_items = filter_res.json()["items"]
    assert any(c["name"] == "Beta Ltd" for c in won_items)


def test_customer_pagination(client, db):
    from app.models.customer import Customer
    for i in range(15):
        db.add(Customer(name=f"Customer {i}", email=f"cust{i}@test.com", status="LEAD"))
    db.commit()

    page1 = client.get("/api/customers?page=1&page_size=5")
    assert page1.status_code == 200
    data1 = page1.json()
    assert len(data1["items"]) == 5
    assert data1["page"] == 1
    assert data1["page_size"] == 5
    assert data1["total"] >= 15

    page2 = client.get("/api/customers?page=2&page_size=5")
    assert page2.status_code == 200
    data2 = page2.json()
    assert len(data2["items"]) == 5
    assert data2["items"][0]["id"] != data1["items"][0]["id"]


def test_legacy_endpoints_compatibility(client, sample_customer):
    # Test legacy GET /api/customers/search?name=value
    res_search = client.get(f"/api/customers/search?name={sample_customer.name[:4]}")
    assert res_search.status_code == 200
    assert isinstance(res_search.json(), list)
    assert any(c["id"] == sample_customer.id for c in res_search.json())

    # Test legacy GET /api/customers/filter?status=VALUE
    res_filter = client.get(f"/api/customers/filter?status={sample_customer.status}")
    assert res_filter.status_code == 200
    assert isinstance(res_filter.json(), list)
    assert any(c["id"] == sample_customer.id for c in res_filter.json())
