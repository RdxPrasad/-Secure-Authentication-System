🔐 Secure Authentication System (Production-Level Backend)

A production-style authentication backend built using FastAPI + MySQL, featuring multi-step verification, OTP-based validation, and secure login architecture.

🚀 Features
📝 User Registration

Full Name, Username, Email, Mobile

Password + Confirm Password validation

Age verification (18+ only)

Unique username & email enforcement

📧 Email Verification (OTP-Based)

Generate 6-digit OTP

OTP stored securely in otp_codes table

5-minute expiry

Auto-deletion after verification

📱 Mobile Verification (OTP-Based)

Separate mobile OTP flow

Independent verification flag

Clean OTP management

🔐 Secure Login

Login allowed only if:

Email is verified

Mobile is verified

Account is active

Password matches (bcrypt hashed)

🛡 Security Features

Password hashing using Bcrypt

Soft account disable (is_active)

OTP expiry handling

Old OTP cleanup before regeneration

Environment-based DB credentials

🏗 Database Architecture
👤 users Table

full_name

username (UNIQUE)

email (UNIQUE)

email_verification (boolean)

mobile (UNIQUE)

mobile_verification (boolean)

password_hash

dob

gender

is_active

created_at

🔑 otp_codes Table

contact_no

otp

purpose (email_verification / mobile_verification)

expiry

created_at

🛠 Tech Stack

Python

FastAPI

MySQL

Bcrypt

python-dotenv

▶️ How to Run
1️⃣ Clone the repository
git clone https://github.com/RdxPrasad/-Secure-Authentication-System
2️⃣ Create virtual environment
python -m venv venv
venv\Scripts\activate
3️⃣ Install dependencies
pip install -r requirements.txt
4️⃣ Create .env file
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=yourpassword
DB_NAME=auth_system
5️⃣ Run the server
uvicorn main:app --reload
🔄 Authentication Flow

Register user (stored with verification flags = False)

Send Email OTP

Verify Email OTP

Send Mobile OTP

Verify Mobile OTP

Login (allowed only if fully verified)

📌 Current Status

✅ Registration with validation
✅ Email OTP verification
✅ Mobile OTP verification
✅ Secure login enforcement
🟡 JWT integration (Next Phase)

🔜 Upcoming Enhancements

JWT Token Authentication

Protected Routes

Role-Based Authorization

Email SMTP Integration

Rate Limiting for OTP

Docker Deployment

📈 Project Level

This project demonstrates:

Multi-step authentication architecture

Secure database design

OTP lifecycle management

Production-style login validation