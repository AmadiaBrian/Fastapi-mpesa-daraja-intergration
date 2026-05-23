from fastapi import FastAPI, Request, Form, Query
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import requests
from datetime import datetime
import json
import base64
import importlib.util
from jinja2 import Environment, FileSystemLoader

# Import get_access_token from genrateAcesstoken.py
spec = importlib.util.spec_from_file_location("genrateAcesstoken", "genrateAcesstoken.py")
genrateAcesstoken = importlib.util.module_from_spec(spec)
spec.loader.exec_module(genrateAcesstoken)
get_access_token = genrateAcesstoken.get_access_token

# Import callback function from callback.py
callback_spec = importlib.util.spec_from_file_location("callback", "callback.py")
callback_module = importlib.util.module_from_spec(callback_spec)
callback_spec.loader.exec_module(callback_module)
process_stk_callback = callback_module.process_stk_callback

# Import database
from database import init_db, SessionLocal, Transaction

app = FastAPI(
    docs_url=None,
    redoc_url=None,
    openapi_url=None
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()

# Custom Jinja2 environment without caching
env = Environment(
    loader=FileSystemLoader("templates"),
    auto_reload=True,
    cache_size=0
)

@app.get('/')
async def main(request: Request):
    template = env.get_template('index.html')
    return HTMLResponse(template.render(request=request))

@app.get('/accesstoken/')
async def get_access_token_route():
    access_token = get_access_token()
    if access_token:
        return JSONResponse({'access_token': access_token})
    else:
        return JSONResponse({'error': 'Failed to retrieve access token. Check console for details.'})

@app.get('/stkpush/')
async def stk_push_form(request: Request):
    template = env.get_template('stk_push_form.html')
    return HTMLResponse(template.render(request=request))

@app.post('/initiate/')
async def initiate_stk_push(
    amount: str = Form(...),
    phone: str = Form(''),
    callback_url: str = Form('https://brayooapi.onrender.com/stk-callback'),
    passkey: str = Form('bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'),
    business_short_code: str = Form('174379'),
    party_b: str = Form('254708374149'),
    account_reference: str = Form('TECHSOLUTIONS'),
    transaction_desc: str = Form('stkpush test')
):
    access_token = get_access_token()
    if access_token:
        # Convert amount to integer
        try:
            amount = int(amount)
        except (ValueError, TypeError):
            amount = 1
        
        process_request_url = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password = base64.b64encode((business_short_code + passkey + timestamp).encode()).decode()
        party_a = phone
        
        stk_push_headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + access_token
        }
        
        stk_push_payload = {
            'BusinessShortCode': business_short_code,
            'Password': password,
            'Timestamp': timestamp,
            'TransactionType': 'CustomerPayBillOnline',
            'Amount': amount,
            'PartyA': party_a,
            'PartyB': business_short_code,
            'PhoneNumber': party_a,
            'CallBackURL': callback_url,
            'AccountReference': account_reference,
            'TransactionDesc': transaction_desc
        }

        try:
            response = requests.post(process_request_url, headers=stk_push_headers, json=stk_push_payload)
            response.raise_for_status()
            response_data = response.json()
            checkout_request_id = response_data['CheckoutRequestID']
            response_code = response_data['ResponseCode']
            
            if response_code == "0":
                return JSONResponse({'CheckoutRequestID': checkout_request_id})
            else:
                return JSONResponse({'error': 'STK push failed.', 'response': response_data})
        except requests.exceptions.RequestException as e:
            print(f"STK Push Error: {e}")
            print(f"Response status: {response.status_code if 'response' in locals() else 'N/A'}")
            print(f"Response text: {response.text if 'response' in locals() else 'N/A'}")
            return JSONResponse({'error': str(e), 'details': response.text if 'response' in locals() else 'N/A'})
    else:
        return JSONResponse({'error': 'Access token not found.'})

@app.get('/query/')
async def query_stk_status(checkout_request_id: str = Query('ws_CO_03072023054410314768168060')):
    access_token = get_access_token()
    if access_token:
        query_url = 'https://sandbox.safaricom.co.ke/mpesa/stkpushquery/v1/query'
        business_short_code = '174379'
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        passkey = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"
        password = base64.b64encode((business_short_code + passkey + timestamp).encode()).decode()

        query_headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + access_token
        }

        query_payload = {
            'BusinessShortCode': business_short_code,
            'Password': password,
            'Timestamp': timestamp,
            'CheckoutRequestID': checkout_request_id
        }

        try:
            response = requests.post(query_url, headers=query_headers, json=query_payload)
            response.raise_for_status()
            response_data = response.json()

            if 'ResultCode' in response_data:
                result_code = response_data['ResultCode']
                if result_code == '1037':
                    message = "1037 Timeout in completing transaction"
                elif result_code == '1032':
                    message = "1032 Transaction has been canceled by the user"
                elif result_code == '1':
                    message = "1 The balance is insufficient for the transaction"
                elif result_code == '0':
                    message = "0 The transaction was successful"
                else:
                    message = "Unknown result code: " + result_code
            else:
                message = "Error in response"

            return JSONResponse({'message': message})
        except requests.exceptions.RequestException as e:
            return JSONResponse({'error': 'Error: ' + str(e)})
        except json.JSONDecodeError as e:
            return JSONResponse({'error': 'Error decoding JSON: ' + str(e)})
    else:
        return JSONResponse({'error': 'Access token not found.'})

@app.post('/stk-callback')
async def stk_callback_endpoint(request: Request):
    return await process_stk_callback(request)

@app.get('/transactions/')
async def transactions_page(request: Request):
    db = SessionLocal()
    try:
        transactions = db.query(Transaction).order_by(Transaction.created_at.desc()).all()
        template = env.get_template('transactions.html')
        return HTMLResponse(template.render(request=request, transactions=transactions))
    finally:
        db.close()

@app.get('/check-status/')
async def check_transaction_status(checkout_request_id: str = Query(...)):
    db = SessionLocal()
    try:
        transaction = db.query(Transaction).filter(Transaction.checkout_request_id == checkout_request_id).first()
        if transaction:
            return JSONResponse({
                'status': 'found',
                'result_code': transaction.result_code,
                'result_desc': transaction.result_desc,
                'amount': transaction.amount,
                'mpesa_receipt': transaction.mpesa_receipt
            })
        else:
            return JSONResponse({'status': 'not_found'})
    finally:
        db.close()
