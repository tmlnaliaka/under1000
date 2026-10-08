# Under 1000/= 🛍
Nairobi town clothes & accessories marketplace — all under Ksh 1,000.

## Setup & Run

1. Install dependencies:
   pip install -r requirements.txt

2. Run the app:
   python app.py

3. Open browser at:
   http://localhost:5000

## Admin Logins (go to /admin/login)

| Username        | Password      | Role                    |
|-----------------|---------------|-------------------------|
| chief_admin     | chief123      | 👑 Chief Admin           |
| listings_admin  | listings123   | 🛍 Listings Manager      |
| sellers_admin   | sellers123    | 🤝 Sellers Manager       |
| content_admin   | content123    | ✏️  Content Moderator    |
| reports_admin   | reports123    | 📊 Reports & Analytics   |

## Pages
- /              → Shop (browse & filter by price)
- /register      → Buyer registration
- /login         → Buyer login
- /sell          → Submit a listing (must be logged in)
- /admin         → Admin dashboard
- /admin/login   → Admin login

## Product data

Catalog entries must come from direct seller posts, not Jumia, Kilimall, or
other marketplaces. Listings link to their first-party seller posts or product
pages and use seller-provided media. Post dates or the date the seller's stock
was checked are shown so buyers can confirm current price and availability.
Video listings embed the seller's original post rather than copying expiring
media URLs. Do not invent seller contacts or fill the catalog with products
that lack a direct source.
