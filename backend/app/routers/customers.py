from typing import Optional, List, Union
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.schemas.customer import (
    CustomerCreate,
    CustomerUpdate,
    CustomerResponse,
    CustomerPagination,
)
from app.services.customer_service import CustomerService
from app.core.dependencies import get_current_user_optional, get_current_user
from app.models.user import User

router = APIRouter(prefix="/customers", tags=["Customers"])


def _map_customer_response(c) -> CustomerResponse:
    assigned_name = c.assigned_user.name if getattr(c, "assigned_user", None) else None
    return CustomerResponse(
        id=c.id,
        name=c.name,
        email=c.email,
        phone=c.phone,
        company=c.company,
        industry=c.industry,
        status=c.status,
        source=c.source,
        assigned_to=c.assigned_to,
        notes=c.notes,
        created_at=c.created_at,
        updated_at=c.updated_at,
        assigned_user_name=assigned_name,
    )


@router.get("", summary="Get customers with search, filter, and pagination")
def get_customers(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search term for name, email, or company"),
    status: Optional[str] = Query(None, description="Status filter"),
    assigned_to: Optional[int] = Query(None, description="Filter by assigned user ID"),
    sort_by: str = Query("created_at", description="Field to sort by"),
    sort_order: str = Query("desc", description="Sort order: asc or desc"),
    paginate: bool = Query(True, description="Whether to return paginated object or flat list"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Retrieve customers supporting keyword search across name, email, and company,
    filtering by status and assigned user, with configurable pagination and sorting.
    """
    items, total, pages = CustomerService.get_customers(
        db=db,
        page=page,
        page_size=page_size,
        search=search,
        status_filter=status,
        assigned_to=assigned_to,
        sort_by=sort_by,
        sort_order=sort_order,
        current_user=current_user,
    )

    response_items = [_map_customer_response(c) for c in items]

    if not paginate:
        return response_items

    return CustomerPagination(
        items=response_items,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages
    )


# Legacy endpoint support for backwards compatibility
@router.get("/search", response_model=List[CustomerResponse], summary="Legacy search by customer name")
def search_customers_legacy(
    name: str = Query(..., description="Customer name substring"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    items = CustomerService.search_by_name(db, name, current_user=current_user)
    return [_map_customer_response(c) for c in items]


# Legacy endpoint support for backwards compatibility
@router.get("/filter", response_model=List[CustomerResponse], summary="Legacy filter by status")
def filter_customers_legacy(
    status: str = Query(..., description="Status enum string"),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    items = CustomerService.filter_by_status(db, status, current_user=current_user)
    return [_map_customer_response(c) for c in items]


@router.get("/{customer_id}", response_model=CustomerResponse, summary="Get customer by ID")
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Retrieve full details of a single customer record."""
    customer = CustomerService.get_by_id(db, customer_id)
    return _map_customer_response(customer)


@router.post("", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED, summary="Create a new customer")
def create_customer(
    customer_in: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Create a new customer record with validation."""
    customer = CustomerService.create_customer(db, customer_in, current_user=current_user)
    return _map_customer_response(customer)


@router.put("/{customer_id}", response_model=CustomerResponse, summary="Update an existing customer")
def update_customer(
    customer_id: int,
    customer_in: CustomerUpdate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Update details of a customer record."""
    customer = CustomerService.update_customer(db, customer_id, customer_in, current_user=current_user)
    return _map_customer_response(customer)


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a customer")
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """Delete a customer record and associated opportunities, activities, and follow-ups."""
    CustomerService.delete_customer(db, customer_id, current_user=current_user)
    return None
