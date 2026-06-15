from decimal import Decimal
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import Product, CartItem, User, DiscountCode
from app.schemas import CartItemCreate, CheckoutRequest
from app.security import hash_password, verify_password
from app import schemas


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_user(self, user_in: schemas.UserRegister, role: str = "buyer") -> User:
        result = await self.db.execute(select(User).where(User.username == user_in.username))
        if result.scalars().first():
            raise ValueError("Username already exists")
        result = await self.db.execute(select(User).where(User.email == user_in.email))
        if result.scalars().first():
            raise ValueError("Email already exists")
        user = User(
            username=user_in.username,
            email=user_in.email,
            password_hash=hash_password(user_in.password),
            role=role,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def authenticate(self, username: str, password: str) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.username == username))
        user = result.scalars().first()
        if not user or not verify_password(password, user.password_hash):
            return None
        return user


class ProductService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_products(self, approved_only: bool = True):
        q = select(Product)
        if approved_only:
            q = q.where(Product.approved == True)
        result = await self.db.execute(q)
        return result.scalars().all()

    async def get(self, product_id: int) -> Optional[Product]:
        result = await self.db.execute(select(Product).where(Product.id == product_id))
        return result.scalars().first()

    async def create(self, product_in: schemas.ProductCreate, submitted_by: str) -> Product:
        product = Product(**product_in.model_dump(), submitted_by=submitted_by, approved=False)
        self.db.add(product)
        await self.db.commit()
        await self.db.refresh(product)
        return product

    async def approve(self, product_id: int) -> Optional[Product]:
        product = await self.get(product_id)
        if not product:
            return None
        product.approved = True
        await self.db.commit()
        await self.db.refresh(product)
        return product

    async def delete(self, product_id: int) -> bool:
        result = await self.db.execute(select(Product).where(Product.id == product_id))
        product = result.scalars().first()
        if not product:
            return False
        await self.db.delete(product)
        await self.db.commit()
        return True


class CartService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_or_create_cart_item(self, user_id: int, product: Product) -> CartItem:
        result = await self.db.execute(
            select(CartItem).where(
                CartItem.user_id == user_id, CartItem.product_id == product.id
            )
        )
        item = result.scalars().first()
        if item:
            item.quantity += 1
        else:
            item = CartItem(user_id=user_id, product_id=product.id, quantity=1)
            self.db.add(item)
        await self.db.commit()
        await self.db.refresh(item)
        return item

    async def list_cart(self, user_id: int):
        result = await self.db.execute(select(CartItem).where(CartItem.user_id == user_id))
        return result.scalars().all()

    async def remove_item(self, user_id: int, product_id: int) -> bool:
        result = await self.db.execute(
            select(CartItem).where(
                CartItem.user_id == user_id, CartItem.product_id == product_id
            )
        )
        item = result.scalars().first()
        if not item:
            return False
        await self.db.delete(item)
        await self.db.commit()
        return True

    async def clear_cart(self, user_id: int) -> None:
        result = await self.db.execute(select(CartItem).where(CartItem.user_id == user_id))
        items = result.scalars().all()
        for item in items:
            await self.db.delete(item)
        await self.db.commit()


class CheckoutService:
    TAX_RATE = Decimal("0.16")
    MAX_INVENTORY_CHECK = 5

    def __init__(self, db: AsyncSession):
        self.db = db

    async def process_checkout(self, user_id: int, checkout: CheckoutRequest) -> dict:
        cart_items = await self._get_cart_items(user_id)
        if not cart_items:
            raise ValueError("Cart is empty")
        total = Decimal("0")
        product_updates = []
        for cart in cart_items:
            product = await self.db.get(Product, cart.product_id)
            if not product or not product.approved:
                raise ValueError(f"Product {cart.product_id} unavailable")
            if product.inventory < cart.quantity:
                raise ValueError(
                    f"Insufficient inventory for {product.name}. "
                    f"Available: {product.inventory}, requested: {cart.quantity}"
                )
            product.inventory -= cart.quantity
            product_updates.append(product)
            total += Decimal(str(product.price)) * cart.quantity
        tax = total * self.TAX_RATE
        discount_amount = Decimal("0")
        discount = None
        if checkout.discount_code:
            discount = await self._validate_discount(checkout.discount_code)
            discount_amount = total * (Decimal(str(discount.percentage)) / Decimal("100"))
        final_total = total + tax - discount_amount
        order_dict = {
            "user_id": user_id,
            "total": float(final_total),
            "tax": float(tax),
            "discount_code": checkout.discount_code,
            "discount_amount": float(discount_amount),
            "status": "completed",
            "payment_method": checkout.payment_method,
        }
        from app.models import Order, OrderItem

        order = Order(**order_dict)
        self.db.add(order)
        await self.db.flush()
        for cart in cart_items:
            oi = OrderItem(
                order_id=order.id,
                product_id=cart.product_id,
                quantity=cart.quantity,
                price=float(product_updates[cart_items.index(cart)].price),
            )
            self.db.add(oi)
        await self.db.delete(cart_items[0])
        from sqlalchemy import delete

        await self.db.execute(delete(CartItem).where(CartItem.user_id == user_id))
        await self.db.commit()
        await self.db.refresh(order)
        return {
            "order_id": order.id,
            "total": float(final_total),
            "subtotal": float(total),
            "tax": float(tax),
            "discount_code": checkout.discount_code,
            "discount_amount": float(discount_amount),
        }

    async def _get_cart_items(self, user_id: int):
        from sqlalchemy.future import select
        from app.models import CartItem

        result = await self.db.execute(select(CartItem).where(CartItem.user_id == user_id))
        return result.scalars().all()

    async def _validate_discount(self, code: str) -> DiscountCode:
        from sqlalchemy.future import select

        result = await self.db.execute(
            select(DiscountCode).where(
                DiscountCode.code == code, DiscountCode.active == True
            )
        )
        discount = result.scalars().first()
        if not discount:
            raise ValueError("Invalid discount code")
        if discount.expires_at and discount.expires_at < datetime.utcnow():
            raise ValueError("Discount code expired")
        return discount
