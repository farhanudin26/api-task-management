import jwt

from config import config

def get_payload(access_token: str, verify_exp: bool = True) -> dict:

    # Remove newline and split characters within the key
    key_without_newline_and_split = config.PUBLIC_KEY.replace('\n', '').split('-----')

    PUBLIC_KEY = f'-----{key_without_newline_and_split[1]}-----\n{key_without_newline_and_split[2]}\n-----{key_without_newline_and_split[3]}-----'

    payload = jwt.decode(
        access_token,
        PUBLIC_KEY,
        ['RS256'],
        options={'verify_exp': verify_exp}
    )

    return payload
