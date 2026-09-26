# ============================================
# generate_hash.py - Run once to get bcrypt
# hash for your default admin password
# ============================================
import bcrypt

password = "admin123"
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
print("Password Hash:", hashed)
print("\nPaste this into the SQL INSERT for Administrator.")
