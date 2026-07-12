import os
import sys
import hashlib

# Global variables
MAX_CONNECTIONS = 100
SECRET_KEY = "super_secret_admin_key_12345"  # Security Risk: Hardcoded credential

def process_user_data(username, password, role, age, email, status, phone):
    """
    Very long parameter list code smell.
    """
    # Security Risk: SQL Injection via string formatting
    query = "SELECT * FROM users WHERE name = '%s' AND role = '%s'" % (username, role)
    
    # Performance Risk: Repeated file opening in loop
    for i in range(10):
        with open("log.txt", "a") as f:
            f.write(f"Logged check {i} for {username}\n")
            
    # Complexity smell: nested conditionals
    if role == "admin":
        if age > 18:
            if status == "active":
                print("Welcome Admin")
            else:
                print("Admin account inactive")
        else:
            print("Underage admin")
            
    # Unsafe eval
    result = eval(username)
    return result

def helper():
    # Dead code: unused function and variables
    x = 42
    y = "not used"
    pass
