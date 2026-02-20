# 🔐 Secure Authentication System (Phase 1)

Backend authentication system built using:

- FastAPI
- MySQL
- Bcrypt
- OTP Verification
- Environment Variables (.env)

---

## 🚀 Features

- User Registration
- Password Hashing using Bcrypt
- Login with OTP Generation
- OTP Expiry (5 minutes)
- Secure DB credentials using .env

---

## 🛠 Tech Stack

- Python
- FastAPI
- MySQL
- Bcrypt
- python-dotenv

---

## ▶️ How to Run

1. Clone the repository

    git clone https://github.com/RdxPrasad/-Secure-Authentication-System


2. Create virtual environment

    python -m venv venv
    venv\Scripts\activate


3. Install dependencies

    pip install -r requirements.txt


4. Create a `.env` file in project root:

    DB_HOST=localhost
    DB_USER=root
    DB_PASSWORD=yourpassword
    DB_NAME=auth_system


5. Run the server

    uvicorn main:app --reload


---

## 📌 Phase 1 Completed

Next Phase:
- JWT Integration
- Email-based OTP
- Role-based Authorization
- Docker Setup