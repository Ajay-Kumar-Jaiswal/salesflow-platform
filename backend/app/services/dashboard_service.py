from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, asc
from app.models.customer import Customer
from app.models.opportunity import Opportunity
from app.models.activity import Activity
from app.models.follow_up import FollowUp
from app.models.user import User
from app.schemas.dashboard import DashboardSummary, StageDistribution
from app.schemas.customer import CustomerResponse
from app.schemas.activity import ActivityResponse
from app.schemas.follow_up import FollowUpResponse


class DashboardService:
    @staticmethod
    def get_summary(db: Session, current_user: Optional[User] = None) -> DashboardSummary:
        # Base queries - allow scoping if sales rep
        cust_query = db.query(Customer)
        opp_query = db.query(Opportunity)
        act_query = db.query(Activity)
        fu_query = db.query(FollowUp)

        if current_user and current_user.role == "SALES_REP":
            cust_query = cust_query.filter(Customer.assigned_to == current_user.id)
            opp_query = opp_query.filter(Opportunity.assigned_to == current_user.id)
            fu_query = fu_query.filter(FollowUp.user_id == current_user.id)

        # Total customers
        total_customers = cust_query.count()

        # Opportunity metrics
        open_opportunities = opp_query.filter(~Opportunity.stage.in_(["WON", "LOST"])).count()
        won_opportunities = opp_query.filter(Opportunity.stage == "WON").count()
        lost_opportunities = opp_query.filter(Opportunity.stage == "LOST").count()

        pipeline_val_result = opp_query.filter(~Opportunity.stage.in_(["WON", "LOST"])).with_entities(
            func.coalesce(func.sum(Opportunity.amount), 0.0)
        ).scalar()
        pipeline_value = float(pipeline_val_result or 0.0)

        won_revenue_result = opp_query.filter(Opportunity.stage == "WON").with_entities(
            func.coalesce(func.sum(Opportunity.amount), 0.0)
        ).scalar()
        won_revenue = float(won_revenue_result or 0.0)

        closed_deals = won_opportunities + lost_opportunities
        conversion_rate = round((won_opportunities / closed_deals * 100), 1) if closed_deals > 0 else 0.0

        # Customer status distribution
        status_counts = cust_query.with_entities(Customer.status, func.count(Customer.id)).group_by(Customer.status).all()
        status_dist: Dict[str, int] = {st: 0 for st in ["LEAD", "CONTACTED", "QUALIFIED", "PROPOSAL", "NEGOTIATION", "WON", "LOST", "INACTIVE"]}
        for status_name, count in status_counts:
            status_dist[status_name] = count

        # Pipeline distribution across stages
        stages_order = ["LEAD", "CONTACTED", "QUALIFIED", "PROPOSAL", "NEGOTIATION", "WON", "LOST"]
        stage_aggregates = opp_query.with_entities(
            Opportunity.stage,
            func.count(Opportunity.id),
            func.coalesce(func.sum(Opportunity.amount), 0.0)
        ).group_by(Opportunity.stage).all()
        
        stage_map = {row[0]: (row[1], float(row[2])) for row in stage_aggregates}
        pipeline_dist: List[StageDistribution] = []
        for s in stages_order:
            cnt, val = stage_map.get(s, (0, 0.0))
            pipeline_dist.append(StageDistribution(stage=s, count=cnt, value=val))

        # Upcoming follow-ups
        now = datetime.now(timezone.utc)
        upcoming_fus = fu_query.filter(
            FollowUp.completed == False,
            FollowUp.scheduled_at >= now
        ).order_by(asc(FollowUp.scheduled_at)).limit(5).all()

        fu_responses = []
        for fu in upcoming_fus:
            fu_responses.append(FollowUpResponse(
                id=fu.id,
                customer_id=fu.customer_id,
                user_id=fu.user_id,
                user_name=fu.user.name if fu.user else None,
                customer_name=fu.customer.name if fu.customer else None,
                title=fu.title,
                description=fu.description,
                follow_up_type=fu.follow_up_type,
                scheduled_at=fu.scheduled_at,
                completed=fu.completed,
                created_at=fu.created_at,
                updated_at=fu.updated_at
            ))

        # Recent activities
        recent_acts = act_query.order_by(desc(Activity.created_at)).limit(5).all()
        act_responses = []
        for act in recent_acts:
            act_responses.append(ActivityResponse(
                id=act.id,
                customer_id=act.customer_id,
                user_id=act.user_id,
                user_name=act.user.name if act.user else None,
                customer_name=act.customer.name if act.customer else None,
                activity_type=act.activity_type,
                title=act.title,
                description=act.description,
                created_at=act.created_at
            ))

        # Recent customers
        recent_custs = cust_query.order_by(desc(Customer.created_at)).limit(5).all()
        cust_responses = []
        for c in recent_custs:
            cust_responses.append(CustomerResponse(
                id=c.id,
                name=c.name,
                email=c.email,
                phone=c.phone,
                company=c.company,
                industry=c.industry,
                status=c.status,
                source=c.source,
                assigned_to=c.assigned_to,
                assigned_user_name=c.assigned_user.name if c.assigned_user else None,
                notes=c.notes,
                created_at=c.created_at,
                updated_at=c.updated_at
            ))

        return DashboardSummary(
            total_customers=total_customers,
            open_opportunities=open_opportunities,
            won_opportunities=won_opportunities,
            pipeline_value=pipeline_value,
            won_revenue=won_revenue,
            conversion_rate=conversion_rate,
            customer_status_distribution=status_dist,
            pipeline_distribution=pipeline_dist,
            upcoming_follow_ups=fu_responses,
            recent_activities=act_responses,
            recent_customers=cust_responses
        )
