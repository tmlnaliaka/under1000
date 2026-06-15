from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models import Order, OrderItem, User
from app.deps import get_current_user


router = APIRouter()


@router.get("/")
async def list_orders(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Order).where(Order.user_id == current_user.id).order_by(Order.created_at.desc())
    )
    orders = result.scalars().all()
    out = []
    for o in orders:
        items_result = await db.execute(select(OrderItem).where(OrderItem.order_id == o.id))
        items = items_result.scalars().all()
        out.append(
            {
                "id": o.id,
                "total": float(o.total),
                "status": o.status,
                "created_at": o.created_at.isoformat(),
                "items": [
                    {
                        "product_id": i.product_id,
                        "quantity": i.quantity,
                        "price": float(i.price),
                    }
                    for i in items
                ],
            }
        )
    return out
