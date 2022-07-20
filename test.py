import json
import requests

__URL__ = "http://localhost:5000"

def request(method, *args, **kwargs):
    try:
        response = requests.request(method, *args, **kwargs)
        response.raise_for_status()
        print(response.request.method, response.url, ": HTTP", response.status_code)
        print(json.dumps(
            response.json(), indent=4, ensure_ascii=False
        ), sep='\n')
        return response.json()
    except requests.RequestException as err:
        print(err)
        print(err.request.method, err.response.url, ": HTTP", err.response.status_code)
        print(json.dumps(
            err.response.json(), indent=4, ensure_ascii=False
        ), sep='\n')
        raise Exception()

def main():
    try:
        # request(
        #     'POST', f"{__URL__}/api/users/create",
        #     data={
        #         'name': 'ABC',
        #         'username': 'ABC',
        #         'password': '12345678',
        #         'e-mail': 'abc@gmail.com',
        #         'contact': '',
        #         'designation': 'Student',
        #         'organization': 'ddbe2a38-075a-11ed-806a-3221e19b7403'
        #     }
        # )
        # login_data = request(
        #     'POST', f"{__URL__}/api/users/login",
        #     data={
        #         'username': 'ABC',
        #         'password': '12345678',
        #     }
        # )
        request(
            'GET', f"{__URL__}/api/users/view",
            headers={
                'Authorization': f"Bearer {''}"
            }
        )
    except:
        print("failed")

if __name__ == "__main__":
    main()