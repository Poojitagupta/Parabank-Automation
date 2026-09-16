VALID_LOGIN = [
    {
        "username": "rahul_12345",
        "password": "Rahul@123"
    },
    {
        "username": "ananya_12345",
        "password": "Ananya@123"
    },
    {
        "username": "arjun_12345",
        "password": "Arjun@123"
    }
]

INVALID_LOGIN_DATA = [

    {
        "username": "invalid_user",
        "password": "WrongPassword123",
        "scenario": "Invalid username and password",
        "message" : "The username and password could not be verified."
    },

    {
        "username": "invalid_user",
        "password": "ValidPassword123",
        "scenario": "Invalid username",
        "message" : "The username and password could not be verified."
    },

    {
        "username": "arjun_12345",
        "password": "WrongPassword123",
        "scenario": "Invalid password",
        "message" : "The username and password could not be verified."
    },

    {
        "username": "",
        "password": "ValidPassword123",
        "scenario": "Empty username",
        "message" : "Please enter a username and password."
    },

    {
        "username": "arjun_12345",
        "password": "",
        "scenario": "Empty password",
        "message" : "Please enter a username and password."
    },

    {
        "username": "",
        "password": "",
        "scenario": "Empty username and password",
        "message" : "Please enter a username and password."
    }
]