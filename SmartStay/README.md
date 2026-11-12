# SmartStay – Hotel & Cab Booking Demo

## Requirements
- Python 3.9+
- VS Code (recommended)

## Run on Windows
1. Extract the ZIP.
2. Open the `SmartStay` folder in VS Code.
3. Open Terminal > New Terminal.
4. Run:
   ```bash
   py -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   python app.py
   ```
5. Open http://127.0.0.1:5000

## Admin demo login
- Email: admin@smartstay.com
- Password: Admin@123

Change the admin password and SECRET_KEY before any real deployment.

## Included
- User registration/login with password hashing
- Hotel search, city filter and price/rating sort
- Cab fare estimates by distance
- Hotel booking by dates and guests
- Cab booking with pickup/drop and distance
- User booking dashboard and cancellation
- Admin dashboard to add/delete hotels and cabs and view bookings
- SQLite database auto-created with sample records

## Important limitations
This is a college-project demonstration. It does not connect to real hotel inventory, real cab fleets, payment gateways, maps, GPS, or live fares. A booking is stored locally in SQLite and is not a real-world reservation. Add CSRF protection, stronger secret management, HTTPS, validation, rate limiting and a production database before deployment.
