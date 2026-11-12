# SmartStay – Hotel & Cab Booking Platform

A web-based hotel and cab booking platform built using Python Flask, SQLite, HTML, and CSS. SmartStay helps users explore hotels, compare prices, estimate cab fares, and manage their bookings through a simple interface.

## Features

### User Features
- User registration and login
- Search hotels by city
- Sort hotels by price and rating
- View hotel details and prices
- Book hotel rooms
- Estimate cab fares based on distance
- Book cabs with pickup and drop locations
- View and cancel bookings through the user dashboard

### Admin Features
- Admin dashboard
- Add and delete hotel listings
- Add and delete cab listings
- View booking records

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| Flask | Web framework |
| SQLite | Database |
| HTML5 | Page structure |
| CSS3 | Styling |
| Jinja2 | Dynamic HTML templates |

## Project Structure

```text
SmartStay/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── templates/
├── static/
└── screenshots/
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/Annu29-ui/SmartStay-Hotel-Cab-Booking.git
```

### 2. Navigate to the project folder

```bash
cd SmartStay-Hotel-Cab-Booking/SmartStay
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

### 4. Activate the virtual environment (Windows PowerShell)

```powershell
.\venv\Scripts\Activate.ps1
```

### 5. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 6. Run the application

```bash
python app.py
```

### 7. Open in your browser

```text
http://127.0.0.1:5000
```

## Database

- SQLite is used for storing application data.
- The database is initialized automatically when the application starts.
- Sample hotel and cab records are provided for demonstration.

## Current Project Limitations

This is currently a functional local demonstration project.

- Hotel listings and prices use sample database data.
- Cab fares are calculated using predefined per-kilometre rates.
- Real-time hotel availability and cab APIs are not connected.
- Online payment integration is not implemented.
- Bookings are stored locally in SQLite.

## Future Enhancements

- Integrate real-world hotel APIs.
- Integrate live cab fare APIs.
- Add Google Maps for location and route information.
- Implement online payment gateway integration.
- Add email booking confirmations.
- Deploy the application to a cloud platform.

## Author

**Annu Yadav**

- GitHub: [Annu29-ui](https://github.com/Annu29-ui)

---

*SmartStay – Making hotel and cab comparison simpler.*
## Screenshots

### Homepage

![SmartStay Homepage](screenshots/homepage.png)