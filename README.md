# egr-info-service
This microservice provides an opportunity to extract data from the official state register of legal entities and individual entrepreneurs. You can also get information about their licenses (by parsing official licenses register which doesn't have open API). Service provides information only about belarussian subjects.

In order to start using the service, follow this instruction:
1. Clone this repo using https://github.com/wasted-idd/egr-info-service.git link or other ways described on the main page.
2. Install virtual environment in folder "egr-info-service" using (if python is already installed on your machine) this command: "python3 -m venv env".
3. Activate virtual envirinment: "source env/bin/activate".
4. Install all dependencies: "pip3 install -r requirements.txt".
5. Change working directory and run local server (uvicorn): "cd app && uvicorn main:app --reload".
6. For creating service account send POST request to localhost:8000/api/v1/users endpoint with raw data with "username" and "password" keys.
7. Get bearer token for further using via sending GET request (also attach to request data in form with username and password) to localhost:8000/api/v1/token.
8. (If necessary) Lock the possibility to create new service accounts (you can just comment handle (function) "create_user" in auth/routers.py).
9. Use given bearer token for authorization. Make queries by sending requests to API.