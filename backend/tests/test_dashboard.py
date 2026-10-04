def test_dashboard_summary_metrics(client, db, sample_customer, admin_headers):
    from app.models.opportunity import Opportunity
    from app.models.activity import Activity

    # Create won and open opportunities
    opp1 = Opportunity(customer_id=sample_customer.id, title="Won Deal", amount=50000.0, stage="WON")
    opp2 = Opportunity(customer_id=sample_customer.id, title="Open Deal", amount=30000.0, stage="PROPOSAL")
    act = Activity(customer_id=sample_customer.id, activity_type="CALL", title="Dashboard Test Call")
    db.add_all([opp1, opp2, act])
    db.commit()

    response = client.get("/api/dashboard/summary", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()

    assert data["total_customers"] >= 1
    assert data["won_opportunities"] >= 1
    assert data["open_opportunities"] >= 1
    assert data["won_revenue"] >= 50000.0
    assert data["pipeline_value"] >= 30000.0
    assert "customer_status_distribution" in data
    assert "pipeline_distribution" in data
    assert len(data["pipeline_distribution"]) == 7  # 7 standard stages
    assert len(data["recent_activities"]) >= 1
    assert len(data["recent_customers"]) >= 1
