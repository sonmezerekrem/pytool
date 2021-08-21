import os
import random
import pyperclip
import string
from datetime import datetime
import pandas as pd


def generator():
    length = 16

    password = []
    punctuation = "-+?_!&"

    password.append(random.choice(string.ascii_lowercase))
    password.append(random.choice(string.ascii_uppercase))
    password.append(random.choice(string.digits))
    password.append(random.choice(punctuation))

    chars = list((string.ascii_letters + string.digits + punctuation) * 10)
    random.shuffle(chars)

    length = length - 5

    password.append(
        "".join(
            random.sample(
                chars,
                length,
            )
        )
    )

    random.shuffle([i for c in password for i in c])
    password = random.choice(string.ascii_letters) + "".join(password)

    return password


def writer(data):
    df = pd.DataFrame(data=data, index=[0])

    if not os.path.exists("data.csv"):
        df.to_csv("data.csv", index=False)
    else:
        df.to_csv("data.csv", mode="a", header=False, index=False)


def reader():
    keyword = input("Search keyword: ")
    if not os.path.exists("data.csv"):
        return None
    else:
        df = pd.read_csv("data.csv")
        df.dropna(inplace=True)
        df.apply(lambda row: row.astype(str).str.contains(
            keyword, case=False).any(), axis=1)
        print(df.to_string())


def creator():
    website = input("Website name or address to register: ")
    email = input("Email used for registiration: ")
    username = input("Username if exists: ")
    information = input("Additional information if exists: ")
    password = generator()
    data = {
        "Website": website,
        "Email": email,
        "Username": username,
        "Information": information,
        "Datetime": datetime.now().strftime("%d/%B/%Y %H:%M:%S"),
        "Password": password
    }
    print(data)
    writer(data)
    pyperclip.copy(password)
    print("Information is saved and password copied to clip board\n")
