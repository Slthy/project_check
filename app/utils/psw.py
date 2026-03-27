from bcrypt import hashpw, gensalt

passwords = {
    "10000001": "psw1",
    "10000002": "psw2",
    "10000003": "psw3",  # reuse for all 5 faculty if you want
    "10000004": "psw4",
    "10000005": "psw5",
    "88888888": "psw6",
    "99999999": "psw7",
}

for name, pw in passwords.items():
    hashed = hashpw(pw.encode('utf-8'), gensalt()).decode('utf-8')
    print(f"{name}: {hashed}")