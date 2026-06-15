from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func
from sqlalchemy.future import select
from app.database import get_db
from app.models import Product, User, Order, CartItem
from app.deps import get_current_admin


router = APIRouter()


@router.get("/stats")
async def admin_stats(db: AsyncSession = Depends(get_db), admin: User = Depends(get_current_admin)):
    total_products = await db.scalar(select(func.count(Product.id)))
    pending_products = await db.scalar(
        select(func.count(Product.id)).where(Product.approved == False)
    )
    total_orders = await db.scalar(select(func.count(Order.id)))
    total_buyers = await db.scalar(select(func.count(User.id)).where(User.role == "buyer"))
    revenue = await db.scalar(select(func.coalesce(func.sum(Order.total), 0)))
    return {
        "total_products": total_products,
        "pending_products": pending_products,
        "total_orders": total_orders,
        "total_buyers": total_buyers,
        "revenue": float(revenue),
    }


@router.get("/products")
async def admin_products(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    result = await db.execute(select(Product).order_by(Product.id.desc()))
    products = result.scalars().all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "price": float(p.price),
            "seller": p.seller,
            "location": p.location,
            "approved": p.approved,
            "inventory": p.inventory,
            "created_at": p.created_at.isoformat(),
        }
        for p in products
    ]


@router.post("/products/{product_id}/approve")
async def approve_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    product = await db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product.approved = True
    await db.commit()
    return {"detail": "approved"}
