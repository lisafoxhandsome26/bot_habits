import requests
import json
id_chat = 921946846
result = requests.get(f"http://127.0.0.1:8000/profile_user/{id_chat}/")
if result.status_code == 200:
    print(json.loads(result.text))


# result = requests.patch(
#     f"http://127.0.0.1:8000/profile_user/authenticated/{id_chat}/",
#     json={"status": True}
# )
# print(result.status_code)

# result = requests.get(
#     f"http://127.0.0.1:8000/profile_user/authenticated/{id_chat}/",
#     json={"status": True}
# )
# print(result.status_code)
