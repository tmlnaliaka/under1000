from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import get_db
from app.models import Product, User
from app.schemas import ProductCreate, ProductUpdate, ProductOut
from app.deps import get_current_user, get_current_admin, get_optional_user


router = APIRouter()


@router.get("/", response_model=List[ProductOut])
async def list_products(
    category: str | None = Query(None),
    min_price: float | None = Query(None, ge=0, le=1000),
    max_price: float | None = Query(None, ge=0, le=1000),
    search: str | None = Query(None, max_length=100),
    db: AsyncSession = Depends(get_db),
    current: User | None = Depends(get_optional_user),
):
    q = select(Product).where(Product.approved == True)
    if category:
        q = q.where(Product.category == category)
    if min_price is not None:
        q = q.where(Product.price >= min_price)
    if max_price is not None:
        q = q.where(Product.price <= max_price)
    if search:
        q = q.where(Product.name.ilike(f"%{search}%"))
    result = await db.execute(q)
    return result.scalars().all()


@router.get("/{product_id}", response_model=ProductOut)
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    p = await db.get(Product, product_id)
    if not p or not p.approved:
        raise HTTPException(status_code=404, detail="Product not found")
    return p


@router.post("/", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_in: ProductCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    product = Product(**product_in.model_dump(), submitted_by=current_user.username, approved=False)
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return product


@router.patch("/{product_id}", response_model=ProductOut)
async def update_product(
    product_id: int,
    update_in: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    product = await db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    for k, v in update_in.model_dump(exclude_unset=True).items():
        setattr(product, k, v)
    await db.commit()
    await db.refresh(product)
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_admin: User = Depends(get_current_admin),
):
    product = await db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    await db.delete(product)
    await db.commit()
