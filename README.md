# Secure Login System

A secure web-based authentication system developed using Python and Flask.

## Features

- Secure user registration and login
- bcrypt password hashing
- SQLite database
- Parameterized SQL queries
- SQL injection protection
- Input validation
- Session management
- Protected dashboard
- Secure logout
- TOTP-based Two-Factor Authentication (2FA)
- QR-code based 2FA setup
- Google Authenticator support

## Security

### Password Security
Passwords are never stored in plaintext.
The system uses bcrypt to securely hash user passwords.

### SQL Injection Protection
Parameterized SQL queries are used to prevent malicious SQL input.

### Session Protection
Unauthenticated users cannot directly access the dashboard.

### Two-Factor Authentication
TOTP-based 2FA provides an additional authentication layer.

## Technologies

- Python
- Flask
- SQLite
- bcrypt
- PyOTP
- QRCode
- HTML5
- CSS3

## Project Structure

SecureLoginSystem/
├── app.py
├── database.py
├── requirements.txt
├── .gitignore
├── static/
│   └── style.css
└── templates/
    ├── login.html
    ├── register.html
    ├── dashboard.html
    ├── setup_2fa.html
    └── verify_2fa.html

## Installation

Clone the repository:
git clone https://github.com/pranavteja30/SecureLoginSystem.git

Create a virtual environment:
python -m venv venv

Activate the environment:
venv\Scripts\activate

Install dependencies:
pip install -r requirements.txt

Create a .env file with:
SECRET_KEY=your_random_secret_key

Run the application:
python app.py

Open http://127.0.0.1:5000 in your browser.

## Testing

Tested for password hashing, SQL injection, input validation,
session protection, logout, dashboard protection, and TOTP 2FA.

## Security Note

.env, users.db, venv/, and __pycache__/ are excluded from GitHub.

## Author

Pranav Teja
Cybersecurity Internship Project