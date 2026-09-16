VALID_USERS = [
    {
        "first_name": "Rahul",
        "last_name": "Sharma",
        "address": "12 MG Road",
        "city": "Delhi",
        "state": "Delhi",
        "zip_code": "110001",
        "phone": "9876543210",
        "ssn": "123456789",
        "username": "rahul_12345",
        "password": "Rahul@123",
        "confirm_password": "Rahul@123"
    },

    {
        "first_name": "Ananya",
        "last_name": "Verma",
        "address": "45 Park Street",
        "city": "Kolkata",
        "state": "West Bengal",
        "zip_code": "700016",
        "phone": "9876543211",
        "ssn": "223456789",
        "username": "ananya_12345",
        "password": "Ananya@123",
        "confirm_password": "Ananya@123"
    },

    {
        "first_name": "Arjun",
        "last_name": "Patel",
        "address": "78 Ring Road",
        "city": "Ahmedabad",
        "state": "Gujarat",
        "zip_code": "380001",
        "phone": "9876543212",
        "ssn": "323456789",
        "username": "arjun_12345",
        "password": "Arjun@123",
        "confirm_password": "Arjun@123"
    }
]

INVALID_USERS = [
    {
        "name": "Missing first name",
        "first_name": "",
        "last_name": "Sharma",
        "address": "12 MG Road",
        "city": "Delhi",
        "state": "Delhi",
        "zip_code": "110001",
        "phone": "9876543210",
        "ssn": "123456789",
        "username": "invalid_user_1",
        "password": "Rahul@123",
        "confirm_password": "Rahul@123"
    },

    {
        "name": "Missing last name",
        "first_name": "Rahul",
        "last_name": "",
        "address": "12 MG Road",
        "city": "Delhi",
        "state": "Delhi",
        "zip_code": "110001",
        "phone": "9876543210",
        "ssn": "123456789",
        "username": "invalid_user_2",
        "password": "Rahul@123",
        "confirm_password": "Rahul@123"
    },

    {
        "name": "Missing username",
        "first_name": "Rahul",
        "last_name": "Sharma",
        "address": "12 MG Road",
        "city": "Delhi",
        "state": "Delhi",
        "zip_code": "110001",
        "phone": "9876543210",
        "ssn": "123456789",
        "username": "",
        "password": "Rahul@123",
        "confirm_password": "Rahul@123"
    },

    {
        "name": "Password mismatch",
        "first_name": "Rahul",
        "last_name": "Sharma",
        "address": "12 MG Road",
        "city": "Delhi",
        "state": "Delhi",
        "zip_code": "110001",
        "phone": "9876543210",
        "ssn": "123456789",
        "username": "invalid_user_4",
        "password": "Rahul@123",
        "confirm_password": "Wrong@123"
    }
]