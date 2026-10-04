import math
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, asc
from fastapi import HTTPException, status
from app.models.customer import Customer
from app.models.user import User
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse, CustomerPagination


class CustomerService:
    @staticmethod
    def get_by_id(db: Session, customer_id: int) -> Customer:
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer not found with id: {customer_id}"
            )
        return customer

    @staticmethod
    def get_customers(
        db: Session,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        status_filter: Optional[str] = None,
        assigned_to: Optional[int] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        current_user: Optional[User] = None,
    ) -> Tuple[List[Customer], int, int]:
        """
        List customers with searching, filtering, sorting, and pagination.
        Enforces role-based visibility if current_user is provided.
        """
        query = db.query(Customer)

        # Role-based scoping: SALES_REP only sees assigned customers (or unassigned leads they can adopt)
        if current_user and current_user.role == "SALES_REP":
            query = query.filter(
                or_(Customer.assigned_to == current_user.id, Customer.assigned_to.is_(None))
            )
        elif assigned_to is not None:
            query = query.filter(Customer.assigned_to == assigned_to)

        # Search across name, email, company
        if search and search.strip():
            term = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    Customer.name.ilike(term),
                    Customer.email.ilike(term),
                    Customer.company.ilike(term)
                )
            )

        # Status filter
        if status_filter and status_filter.strip():
            query = query.filter(Customer.status == status_filter.strip().upper())

        # Sorting
        sort_column = getattr(Customer, sort_by, Customer.created_at)
        if sort_order.lower() == "asc":
            query = query.order_by(asc(sort_column))
        else:
            query = query.order_by(desc(sort_column))

        total = query.count()
        pages = math.ceil(total / page_size) if total > 0 else 1
        
        offset = (page - 1) * page_size
        items = query.offset(offset).limit(page_size).all()

        return items, total, pages

    @staticmethod
    def create_customer(db: Session, customer_in: CustomerCreate, current_user: Optional[User] = None) -> Customer:
        assigned_id = customer_in.assigned_to
        if assigned_id is None and current_user:
            assigned_id = current_user.id

        status_val = customer_in.status.value if hasattr(customer_in.status, "value") else str(customer_in.status)

        customer = Customer(
            name=customer_in.name.strip(),
            email=customer_in.email.lower().strip(),
            phone=customer_in.phone.strip() if customer_in.phone else None,
            company=customer_in.company.strip() if customer_in.company else None,
            industry=customer_in.industry.strip() if customer_in.industry else None,
            status=status_val.upper(),
            source=customer_in.source.strip() if customer_in.source else None,
            assigned_to=assigned_id,
            notes=customer_in.notes
        )
        db.add(customer)
        db.commit()
        db.refresh(customer)
        return customer

    @staticmethod
    def update_customer(
        db: Session,
        customer_id: int,
        customer_in: CustomerUpdate,
        current_user: Optional[User] = None
    ) -> Customer:
        customer = CustomerService.get_by_id(db, customer_id)

        # SALES_REP authorization check
        if current_user and current_user.role == "SALES_REP":
            if customer.assigned_to and customer.assigned_to != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to edit a customer assigned to another sales representative"
                )

        if customer_in.name is not None:
            customer.name = customer_in.name.strip()
        if customer_in.email is not None:
            customer.email = customer_in.email.lower().strip()
        if customer_in.phone is not None:
            customer.phone = customer_in.phone.strip() if customer_in.phone else None
        if customer_in.company is not None:
            customer.company = customer_in.company.strip() if customer_in.company else None
        if customer_in.industry is not None:
            customer.industry = customer_in.industry.strip() if customer_in.industry else None
        if customer_in.status is not None:
            status_val = customer_in.status.value if hasattr(customer_in.status, "value") else str(customer_in.status)
            customer.status = status_val.upper()
        if customer_in.source is not None:
            customer.source = customer_in.source.strip() if customer_in.source else None
        if customer_in.assigned_to is not None:
            customer.assigned_to = customer_in.assigned_to
        if customer_in.notes is not None:
            customer.notes = customer_in.notes

        db.commit()
        db.refresh(customer)
        return customer

    @staticmethod
    def delete_customer(db: Session, customer_id: int, current_user: Optional[User] = None) -> bool:
        customer = CustomerService.get_by_id(db, customer_id)

        if current_user and current_user.role == "SALES_REP":
            if customer.assigned_to and customer.assigned_to != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to delete a customer assigned to another sales representative"
                )

        db.delete(customer)
        db.commit()
        return True

    @staticmethod
    def search_by_name(db: Session, name: str, current_user: Optional[User] = None) -> List[Customer]:
        """Compatibility method for legacy /search endpoint."""
        items, _, _ = CustomerService.get_customers(
            db, page=1, page_size=1000, search=name, current_user=current_user
        )
        return items

    @staticmethod
    def filter_by_status(db: Session, status_str: str, current_user: Optional[User] = None) -> List[Customer]:
        """Compatibility method for legacy /filter endpoint."""
        items, _, _ = CustomerService.get_customers(
            db, page=1, page_size=1000, status_filter=status_str, current_user=current_user
        )
        return items
