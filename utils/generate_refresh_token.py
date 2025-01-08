import time

import jwt

from config import config

def generate_refresh_token(payload: dict) -> str:
    current_time = int(time.time())

    payload.update({
        'iat' : current_time,
    })

    # Remove newline and split characters within the key
    key_without_newline_and_split = config.REFRESH_PRIVATE_KEY.replace('\n', '').split('-----')

    REFRESH_PRIVATE_KEY = f'-----{key_without_newline_and_split[1]}-----\n{key_without_newline_and_split[2]}\n-----{key_without_newline_and_split[3]}-----'

    refresh_token = jwt.encode(payload, REFRESH_PRIVATE_KEY, 'RS256')

    return refresh_token
