# Imports
import mysql.connector
import bcrypt


# Utility functions
# 🔐 Password verification function
def verify_password(plain_password,stored_hash):
    return bcrypt.checkpw(
        plain_password.encode(),
        stored_hash.encode()
    )

# Main execution logic
password = "mypassword"

hashed = bcrypt.hashpw(password.encode() , bcrypt.gensalt())

print (hashed)

conn = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "Onepiece",
    database = "auth_system"
)

cursor = conn.cursor()

query = """
INSERT INTO users (username,email,password_hash)
VALUES ( %s, %s, %s )
"""

values = ("john","john@email.com",hashed)

cursor.execute(query,values)

conn.commit()

print("user inserted successfully")

conn.close()