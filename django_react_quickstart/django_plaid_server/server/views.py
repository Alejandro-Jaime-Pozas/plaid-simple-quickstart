# from django.shortcuts import render

# Create your views here.
import os, json, time
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.middleware.csrf import get_token
import plaid
from plaid.api import plaid_api
from plaid.model.products import Products
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.accounts_balance_get_request import AccountsBalanceGetRequest
from plaid.configuration import Configuration
from plaid.api_client import ApiClient
from plaid.model.country_code import CountryCode
from dotenv import load_dotenv

# Load environment variables
load_dotenv("../.env")

PLAID_CLIENT_ID = os.getenv('PLAID_CLIENT_ID')
PLAID_SECRET = os.getenv('PLAID_SECRET')
PLAID_ENV = os.getenv('PLAID_ENV', 'sandbox')
PLAID_PRODUCTS = os.getenv('PLAID_PRODUCTS', 'auth').split(',')
PLAID_COUNTRY_CODES = os.getenv('PLAID_COUNTRY_CODES', 'US').split(',')

def empty_to_none(field):
    value = os.getenv(field)
    if value is None or len(value) == 0:
        return None
    return value

host = plaid.Environment.Sandbox

if PLAID_ENV == 'sandbox':
    host = plaid.Environment.Sandbox

if PLAID_ENV == 'production':
    host = plaid.Environment.Production

# Parameters used for the OAuth redirect Link flow.
#
# Set PLAID_REDIRECT_URI to 'http://localhost:3000/'
# The OAuth redirect flow requires an endpoint on the developer's website
# that the bank website should redirect to. You will need to configure
# this redirect URI for your client ID through the Plaid developer dashboard
# at https://dashboard.plaid.com/team/api.
PLAID_REDIRECT_URI = empty_to_none('PLAID_REDIRECT_URI')

configuration = Configuration(
    host=host,
    api_key={
        'clientId': PLAID_CLIENT_ID,
        'secret': PLAID_SECRET,
        'plaidVersion': '2020-09-14'
    }
)
api_client = ApiClient(configuration)
plaid_client = plaid_api.PlaidApi(api_client)

products = []
for product in PLAID_PRODUCTS:
    products.append(Products(product))

# Create Link Token
def create_link_token(request):
    # print("PLAID_CLIENT_ID:", os.getenv("PLAID_CLIENT_ID"))
    # print("PLAID_SECRET:", os.getenv("PLAID_SECRET"))
    # print("PLAID_ENV:", os.getenv("PLAID_ENV"))
    try:
        link_token_request = LinkTokenCreateRequest(
            user=LinkTokenCreateRequestUser(
                client_user_id=str(time.time())
            ),
            client_name="Subsy's Tiny Quickstart",
            language="en",
            products=products,
            country_codes=list(map(lambda x: CountryCode(x), PLAID_COUNTRY_CODES)),
            redirect_uri=os.getenv('PLAID_SANDBOX_REDIRECT_URI'),
        )
        link_token_response = plaid_client.link_token_create(link_token_request)
        return JsonResponse(link_token_response.to_dict(), safe=False)
    except plaid.ApiException as e:
        print(e)
        return JsonResponse({"error": str(e)}, status=400)

# Exchange Public Token for Access Token
@csrf_exempt
def exchange_public_token(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            public_token = data.get("public_token")

            exchange_request = ItemPublicTokenExchangeRequest(public_token=public_token)
            exchange_response = plaid_client.item_public_token_exchange(exchange_request)

            # Store the access_token in the session (for demo purposes)
            request.session["access_token"] = exchange_response.to_dict()["access_token"]
            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "Invalid request method."}, status=405)

# Get Account Balances
def get_balance(request):
    try:
        access_token = request.session.get("access_token")
        if not access_token:
            return JsonResponse({"error": "Access token not found."}, status=403)

        balance_request = AccountsBalanceGetRequest(access_token=access_token)
        balance_response = plaid_client.accounts_balance_get(balance_request)
        return JsonResponse({"Balance": balance_response.to_dict()}, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

# CSRF Token endpoint for front-end use
def csrf_token(request):
    token = get_token(request)
    return JsonResponse({"csrfToken": token})