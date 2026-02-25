from fastapi import FastAPI
import mysql.connector
import bcrypt
from pydantic import BaseModel
from fastapi import HTTPException
import random 
from datetime import datetime , timedelta
import os
from dotenv import load_dotenv


app = FastAPI()

# Pydantic Models
class UserRegister(BaseModel):
    username : str 
    email : str
    password : str

class UserLogin(BaseModel):
    email : str
    password : str

class OTPVerify(BaseModel):
    email : str 
    otp : str

# Root route
@app.get('/')
def root():
    return {"message": "Auth API Running"}

# Database connection function
load_dotenv()

def get_db_connection():
    conn = mysql.connector.connect(
        host = os.getenv("DB_HOST"),
        user = os.getenv("DB_USER"),
        password = os.getenv("DB_PASSWORD"),
        database = os.getenv("DB_NAME")
    )
    return conn

@app.post("/register")
def register(user : UserRegister):
    
    conn = get_db_connection()
    cursor = conn.cursor()

    # check if email already exists
    cursor.execute("SELECT * FROM users WHERE email = %s", (user.email,))
    existing_user = cursor.fetchone()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash Password
    hashed_password = bcrypt.hashpw(
        user.password.encode(),
        bcrypt.gensalt()
    )

    # Insert User
    query = """
    INSERT INTO users (username, email, password_hash)
    VALUES (%s, %s, %s)
    """

    cursor.execute(query, (
        user.username,
        user.email,
        hashed_password.decode()
    ))

    conn.commit()
    conn.close()

    return {"message" : "User Registered Successfully"}

@app.post("/login")
def login(user : UserLogin):

    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch user by Email
    cursor.execute("SELECT password_hash FROM users WHERE email = %s", (user.email,))
    db_user = cursor.fetchone()

    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    stored_hash = str(db_user[0]) #type: ignore 

    # Verify Password
    if not bcrypt.checkpw(
        user.password.encode(),
        stored_hash.encode()
    ):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    # Generate OTP 
    otp = str(random.randint(100000,999999))
    expiry = datetime.now() + timedelta(minutes=5)

    cursor.execute(
        "UPDATE users " 
        "SET otp = %s, otp_expiry = %s " 
        "WHERE email = %s ",
        (otp , expiry , user.email)
    )
    
    conn.commit()
    conn.close()

    print("Generated OTP:", otp)

    return {"message" : "Login Successfull"}

@app.post('/verify-otp')
def verify_otp(data : OTPVerify) :
    
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT otp , otp_expiry FROM users WHERE email = %s", 
        (data.email,)
    )

    user = cursor.fetchone() 

    if not user :
        raise HTTPException(status_code=400 , detail= "User not found")
    
    stored_otp , expiry = user 

    if isinstance(expiry,str):
        expiry = datetime.fromisoformat(expiry)

    if stored_otp != data.otp :
        raise HTTPException(status_code=400 , detail= "Invalid OTP")
    
    if datetime.now() > expiry :
        raise HTTPException(status_code=400 , detail= "OTP expired")

    cursor.execute(
        "UPDATE users SET otp = NULL , otp_expiry = NULL WHERE email = %s",
        (data.email,)
    )

    conn.commit()
    conn.close()

    return {"message" : "Login Successful🎉"}
