# from datetime import datetime, timedelta
# from fastapi.responses import JSONResponse
# from typing import Dict

# # Konfigurasi rate limiting
# RATE_LIMIT_TIME_WINDOW = timedelta(seconds=8)
# RATE_LIMIT_MAX_REQUESTS = 8
# BLOCK_DURATION = timedelta(seconds=15)

# # Penyimpanan sementara untuk rate limit
# rate_limit_store: Dict[str, list] = {}
# block_time_store: Dict[str, datetime] = {}

# def apply_rate_limit(key: str) -> JSONResponse:
#     global rate_limit_store, block_time_store
#     now = datetime.now()

#     # Cek apakah kunci sedang diblokir
#     if key in block_time_store:
#         block_until = block_time_store[key]
#         if now < block_until:
#             return JSONResponse(
#                 status_code=429,
#                 content={
#                     "detail": f"Terlalu banyak permintaan. Silakan coba lagi setelah {int((block_until - now).total_seconds())} detik.",
#                 },
#             )
#         else:
#             del block_time_store[key]

#     if key not in rate_limit_store:
#         rate_limit_store[key] = []

#     recent_requests = [
#         request_time for request_time in rate_limit_store[key]
#         if now - request_time <= RATE_LIMIT_TIME_WINDOW
#     ]
#     rate_limit_store[key] = recent_requests

#     if len(recent_requests) >= RATE_LIMIT_MAX_REQUESTS:
#         block_time_store[key] = now + BLOCK_DURATION
#         return JSONResponse(
#             status_code=429,
#             content={
#                 "detail": "Terlalu banyak permintaan. Silakan coba lagi setelah 30 detik.",
#             },
#         )

#     rate_limit_store[key].append(now)
#     return None
