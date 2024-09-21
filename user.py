from dataclasses import dataclass


@dataclass
class User:
    #id: int
    email: str
    password: str
    name: str
    age: int = ""
    aboutUser: str = ""
    photo: str = ""
