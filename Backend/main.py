from fastapi import FastAPI
import mysql.connector
import bcrypt
from pydantic import BaseModel
from fastapi import HTTPException
import random 
from datetime import datetime , timedelta , date
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins = ["*"] ,
    allow_credentials = True , 
    allow_methods = ["*"],
    allow_headers = ["*"],
)

# Pydantic Models
class UserRegister(BaseModel):
    full_name : str
    username : str 
    email : str
    mobile : str
    password : str
    confirm_password : str
    dob : str
    gender : str

class EmailRequest(BaseModel):
    email : str

class MobileRequest(BaseModel):
    mobile : str

class UserLogin(BaseModel):
    email : str
    password : str

class EmailOTPVerify(BaseModel):
    email : str 
    otp : str

class MobileOTPVerify(BaseModel):
    mobile: str
    otp: str

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

    # Check if username already exists
    cursor.execute("SELECT * FROM users WHERE username = %s",(user.username,))
    existing_username = cursor.fetchone()
    if existing_username:
        raise HTTPException(status_code=404 , detail="Username already taken!!!")
    
    # check if email already exists
    cursor.execute("SELECT * FROM users WHERE email = %s", (user.email,))
    existing_email = cursor.fetchone()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # check Password Confirmation
    if user.password != user.confirm_password :
        raise HTTPException(status_code=404,detail="Password do not match!!!")
    
    # Check age from dob
    dob_date = datetime.strptime(user.dob,"%Y-%m-%d").date()
    today = date.today()
    age = today.year - dob_date.year - ((today.month,today.day)<(dob_date.month,dob_date.day))
    if age < 18 :
        raise HTTPException(status_code=404,detail="User must be 18+")
    
    # Hash Password
    hashed_password = bcrypt.hashpw(
        user.password.encode(),
        bcrypt.gensalt()
    )

    # Insert User
    query = """
    INSERT INTO users (
    full_name,
    username,
    email,
    email_verification,
    mobile,
    mobile_verification,
    password_hash,
    dob,
    gender,
    is_active,
    created_at
    )
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """

    cursor.execute(query, (
        user.full_name,
        user.username,
        user.email,
        False,
        user.mobile,
        False,
        hashed_password.decode(),
        user.dob,
        user.gender,
        True,
        datetime.now()
    ))

    conn.commit()
    conn.close()

    return {"message" : "User Registered Successfully"}

@app.post("/send-email-otp")
def send_email_otp(data:EmailRequest):

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if User exists
    cursor.execute("SELECT email_verification FROM users WHERE email = %s", (data.email,))
    user = cursor.fetchone()

    if not user :
        raise HTTPException(status_code=404, detail="User not Found")
    
    (email_verification,) = user

    # Check if User is verified?
    if email_verification:
        raise HTTPException(status_code=400, detail="Email already verified")
    
    # Delete previous OTP if exists (clean practice)
    cursor.execute("DELETE FROM otp_codes WHERE contact_no = %s AND purpose = %s", (data.email,"email_verification"))
    
    # Generate OTP
    otp = str(random.randint(100000,999999))
    expiry = datetime.now() + timedelta(minutes=5)

    # Inserting new otp
    cursor.execute(
        "INSERT INTO otp_codes (contact_no, otp, purpose, expiry, created_at) VALUES (%s,%s,%s,%s,%s)", (data.email, otp, 'email_verification', expiry, datetime.now())
    )

    conn.commit()
    conn.close()

    print("Generated Email OTP :", otp)

    return {"message" : "Email otp sent successfully..."}

@app.post("/verify-email-otp")
def verify_email_otp(data : EmailOTPVerify):

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT otp, expiry FROM otp_codes " \
        "WHERE contact_no = %s AND purpose = %s " \
        "ORDER BY id DESC LIMIT 1",
        (data.email,"email_verification")
    )

    record = cursor.fetchone() 

    if not record:
        raise HTTPException(status_code=400,detail="OTP not found")
    
    stored_otp , expiry = record 

    # Check Expiry
    if datetime.now() > expiry :
        raise HTTPException(status_code=400, detail="OTP expired")
    
    # Check OTP match
    if(stored_otp != data.otp):
        raise HTTPException(status_code=400 , detail="Invalid OTP")
    
    # Update user as verified
    cursor.execute(
        "UPDATE users SET email_verification = TRUE WHERE email = %s",(data.email,)
    )

    # Delete used OTP
    cursor.execute(
        "DELETE FROM otp_codes WHERE contact_no = %s and purpose = %s ",
        (data.email,"email_verification")
    )
    
    conn.commit()
    conn.close()

    return {"message" : "Email verified successfully 🎉"}



@app.post("/send-mobile-otp")
def send_mobile_otp(data:MobileRequest):

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if user exists
    cursor.execute(
        "SELECT mobile_verification FROM users WHERE mobile = %s", 
        (data.mobile,)
    )

    user = cursor.fetchone() 

    if user :
        (mobile_verification,) = user
    else :
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if user verified or not 
    if mobile_verification :
        raise HTTPException(status_code=400,detail="Mobile already verified")
    else :
        # Delete Previous otp if any present 
        cursor.execute(
            "DELETE FROM otp_codes WHERE contact_no = %s AND purpose = %s",
            (data.mobile , "mobile_verification")
        )

        otp =  str(random.randint(100000,999999))
        expiry = datetime.now() + timedelta(minutes=5)

        # Create new OTP if not present 
        cursor.execute(
            "INSERT INTO otp_codes (contact_no,otp,purpose,expiry,created_at) " \
            "VALUES (%s,%s,%s,%s,%s)",
            (data.mobile,
             otp,
             "mobile_verification",
             expiry,
             datetime.now()
            )
        )

    conn.commit()
    conn.close()

    print("Generated mobile OTP: " ,otp)
    return{"message" : "Mobile otp sent successfully🎉"}

@app.post("/verify-mobile-otp")
def verify_mobile_otp(data:MobileOTPVerify):

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT otp , expiry FROM otp_codes " \
        "WHERE contact_no = %s AND purpose = %s " \
        "ORDER BY id DESC LIMIT 1",
        (data.mobile,"mobile_verification")
    )

    record = cursor.fetchone()

    if record :
        stored_otp , expiry = record

        if datetime.now() > expiry :
            raise HTTPException(status_code=400,detail="OTP expired")
        
        if stored_otp != data.otp:
            raise HTTPException(status_code=400, detail="Invalid OTP")

        # Update user as verified
        cursor.execute(
            "UPDATE users SET mobile_verification = TRUE WHERE mobile = %s",
            (data.mobile,)
        )

        # Deleting the OTP after verified
        cursor.execute(
            "DELETE FROM otp_codes WHERE contact_no = %s AND purpose = %s",
            (data.mobile,"mobile_verification")
        )

        
    else :
        raise HTTPException(status_code=400,detail="OTP not found!")

    conn.commit()
    conn.close()

    return {"message" : "Mobile Otp verified successfully🎉"}




@app.post("/login")
def login(user : UserLogin):

    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch user by Email
    cursor.execute(
        "SELECT password_hash , email_verification , mobile_verification , is_active " \
        "FROM users WHERE email = %s", 
        (user.email,)
    )

    db_user = cursor.fetchone()

    if db_user :
            
        password_hash ,email_verification , mobile_verification , is_active = db_user

        # Veryfing password
        if not bcrypt.checkpw( user.password.encode() , password_hash.encode() ) :
            raise HTTPException(status_code=400, detail="Invalid Credentials❌")

        # Veryfing Account is Active or Disabled
        if is_active :
            
            # Veryfing email
            if not email_verification :
                raise HTTPException(status_code=400 , detail="Email not verified❌")
            
            # Veryfing mobile number
            if not mobile_verification :
                raise HTTPException(status_code=400, detail="Mobile not verified❌")
               
        else :
            raise HTTPException(status_code=403 , detail= "Account Disabled🚫")
        
    else :
        raise HTTPException(status_code=400 , detail="Invalid Credentials!❌")

    conn.close()

    return {"message" : "Login Successfull🎉"}

