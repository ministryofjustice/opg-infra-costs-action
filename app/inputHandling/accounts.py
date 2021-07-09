import json

def accounts(raw: str):
    parsed = json.loads(raw)
    if len(parsed) < 1:
        raise Exception('Account Data', 'Account data missing, requires at least 1 account.')
    return parsed
