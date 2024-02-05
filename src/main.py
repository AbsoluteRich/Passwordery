from shared import *
from secrets import token_hex
from getpass import getpass
from hashlib import sha256
from sys import exit
from cryptography.fernet import Fernet


def pad_string_with_rotation(string: str, padding: str) -> str:
    for i in range(len(string), (len(padding))):
        string += padding[i % len(padding)]
    return string


def hash_password(raw_password: str, salt: str) -> str:
    hasher = sha256(usedforsecurity=True)
    raw_password = pad_string_with_rotation(raw_password, salt)
    hasher.update(raw_password.encode("utf-8"))
    return hasher.hexdigest()


db = Config("restricted.json")
user_credentials = [False, None]  # Is the user logged in? + username, if any

try:
    with open("fernet.key", "wb") as f:
        f.write(Fernet.generate_key())
except FileExistsError:
    pass

with open("fernet.key", "rb") as f:
    key = f.readline()
    fern = Fernet(key)

while True:
    if user_credentials[0]:
        console = sinput(sep="USER", mode="compare")
        match console:
            case "set" | "put":
                text_area = sinput("Start typing")
                encrypted = text_area.encode("utf-8")
                encrypted = fern.encrypt(encrypted)
                encrypted = encrypted.decode("utf-8")
                db.write(encrypted, user_credentials[1], "text")
                print("Success! You can now view your encrypted text area.")

            case "view" | "get":
                text_area = db.read(user_credentials[1], "text")
                if text_area:
                    decrypted = text_area.encode("utf-8")
                    decrypted = fern.decrypt(decrypted)
                    decrypted = decrypted.decode("utf-8")
                    print(decrypted)
                else:
                    print("Text area not found.")

            case "clear":
                db.delete(user_credentials[1], "text")
                print("Success. Your text area has been deleted.")

            case "delete":
                print("Deleting your account will permanently erase your login credentials and text area.")
                confirmation = sinput("Type 'CONFIRM' if you know what you're doing.")
                if confirmation == "CONFIRM":
                    db.delete(user_credentials[1])
                    print("Success. You will now be logged out.")
                    user_credentials = [False, None]
                else:
                    print("Cancelled.")

            case "logout":
                print(f"Deauthorising user '{user_credentials[1]}'.")
                user_credentials = [False, None]

            case "exit":
                print("Log out first!")

            case _:
                print("Invalid command.")

    else:
        console = sinput(sep="", mode="compare")
        match console:
            case "create":
                username = sinput("Choose a username")

                if username in db.dictionary.keys():
                    print("Invalid username.")
                else:
                    password = getpass("Choose a password (Your input will not be shown) >>")
                    password_salt = token_hex()
                    password = hash_password(password, password_salt)

                    db.write({
                        "password": password,
                        "salt": password_salt
                    }, username)
                    print(f"Success! You can now log in under '{username}'.")

            case "accounts":
                if db.dictionary:
                    for username in db.dictionary.keys():
                        print(username)
                else:
                    print("No accounts found.")

            case "login":
                input_username = sinput("Username")
                if input_username in db.dictionary.keys():
                    account_password = db.read(input_username, "password")
                    account_salt = db.read(input_username, "salt")
                    input_password = getpass("Password (Your input will not be shown) >>")

                    if hash_password(input_password, account_salt) == account_password:
                        user_credentials[0] = True
                        user_credentials[1] = input_username
                        print(f"Success! Logged in as '{input_username}'.")
                    else:
                        print("Invalid password.")
                else:
                    print("Invalid username.")

            case "exit":
                exit()

            case _:
                print("Invalid command.")

    print()
