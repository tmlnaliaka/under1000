from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models import CartItem, Product, User
from app.schemas import CartItemCreate, CartItemOut, CheckoutRequest
from app.deps import get_current_user


router = APIRouter()


@router.get("/", response_model=list[CartItemOut])
async def get_cart(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = (
        select(CartItem)
        .where(CartItem.user_id == current_user.id)
        .order_by(CartItem.created_at.desc())
    )
    result = await db.execute(q)
    items = result.scalars().all()
    out = []
    for item in items:
        product = await db.get(Product, item.product_id)
        if product and product.approved:
            item.product = product
            out.append(item)
    return out


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def add_to_cart(
    item_in: CartItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    product = await db.get(Product, item_in.product_id)
    if not product or not product.approved:
        raise HTTPException(status_code=404, detail="Product not found or not approved")
    if product.inventory < item_in.quantity:
        raise HTTPException(status_code=400, detail="Insufficient inventory")
    result = await db.execute(
        select(CartItem).where(
            CartItem.user_id == current_user.id,
            CartItem.product_id == item_in.product_id,
        )
    )
    existing = result.scalars().first()
    if existing:
        existing.quantity = min(existing.quantity + item_in.quantity, product.inventory)
    else:
        cart_item = CartItem(
            user_id=current_user.id, product_id=item_in.product_id, quantity=item_in.quantity
        )
        db.add(cart_item)
    await db.commit()
    return {"detail": "added to cart"}


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_cart(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(CartItem).where(
            CartItem.user_id == current_user.id,
            CartItem.product_id == product_id,
        )
    )
    item = result.scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not in cart")
    await db.delete(item)
    await db.commit()


@router.post("/checkout", response_model=dict)
async def checkout(
    checkout_in: CheckoutRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    from app.services import CheckoutService

    service = CheckoutService(db)
    try:
        result = await service.process_checkout(current_user.id, checkout_in)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return result
