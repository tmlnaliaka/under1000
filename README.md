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
