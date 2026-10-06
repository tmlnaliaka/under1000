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

The starter catalog is intentionally empty. Previous sample listings had no
verifiable seller or product evidence, so they were removed rather than
presented as real businesses. Add listings only after confirming the business
and the specific item through a direct seller source. Do not copy catalog items
from Jumia or Kilimall.
