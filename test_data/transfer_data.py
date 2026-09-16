valid_transfer_data = [
    {
        "test_case": "Valid transfer",
        "amount": 10
    }
]


invalid_transfer_test_data = [
    {
        "test_case": "Negative amount",
        "amount": -10
    },
    {
        "test_case": "Zero amount",
        "amount": 0
    },
    {
        "test_case": "Amount greater than balance",
        "amount": "balance+1"
    },
    {
        "test_case": "Empty amount",
        "amount": ""
    },
    {
        "test_case": "Non-numeric amount",
        "amount": "abc"
    }
]