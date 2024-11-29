from django.shortcuts import render

# Create your views here.
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.middleware.csrf import get_token
from plaid.api import plaid_api
from plaid.model import (LinkTokenCreateRequest, ItemPublicTokenExchangeRequest, AccountsBalanceGetRequest)
from plaid.configuration import Configuration
from plaid.api_client import ApiClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Plaid client configuration
configuration = Configuration(
    host=os.getenv("PLAID_ENV"),
    api_key={
        "clientId": os.getenv("PLAID_CLIENT_ID"),
        "secret": os.getenv("PLAID_SECRET"),
        "Plaid-Version": "2020-09-14",
    },
)
api_client = ApiClient(configuration)
plaid_client = plaid_api.PlaidApi(api_client)

# Create Link Token
def create_link_token(request):
    try:
        link_token_request = LinkTokenCreateRequest(
            user={"client_user_id": request.session.session_key},
            client_name="Subsy's Tiny Quickstart",
            language="en",
            products=["auth"],
            country_codes=["US"],
            redirect_uri=os.getenv("PLAID_SANDBOX_REDIRECT_URI"),
        )
        link_token_response = plaid_client.link_token_create(link_token_request)
        return JsonResponse(link_token_response.to_dict(), safe=False)
    except Exception as e:
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
