import time

from typing import Tuple

import jwt

from config import config

def generate_access_token(payload: dict) -> Tuple[str, int]:
    current_time = int(time.time())
    expired_at = current_time + config.ACCESS_TOKEN_EXPIRATION

    payload.update({
        'exp' : expired_at,
        'iat' : current_time,
    })

    # Remove newline and split characters within the key
    key_without_newline_and_split = config.PRIVATE_KEY.replace('\n', '').split('-----')

    PRIVATE_KEY = f'-----{key_without_newline_and_split[1]}-----\n{key_without_newline_and_split[2]}\n-----{key_without_newline_and_split[3]}-----'

    access_token = jwt.encode(payload, PRIVATE_KEY, 'RS256')

    return access_token, expired_at
