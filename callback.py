from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import json
from datetime import datetime
from database import SessionLocal, Transaction

app = FastAPI()

@app.post("/stk-callback")
async def process_stk_callback(request: Request):
    try:
        # Get JSON response from Safaricom
        stk_callback_response = await request.json()

        # Add timestamp to the response for logging
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "callback_data": stk_callback_response
        }

        # Save response to log file with proper JSON formatting
        log_file = "Mpesastkresponse.json"

        with open(log_file, "a") as log:
            json.dump(log_entry, log, indent=2)
            log.write("\n")

        print(f"Callback received at {datetime.now().isoformat()}")
        print(f"Full response: {json.dumps(stk_callback_response, indent=2)}")

        # Extract callback data
        callback = stk_callback_response['Body']['stkCallback']

        merchant_request_id = callback['MerchantRequestID']
        checkout_request_id = callback['CheckoutRequestID']
        result_code = callback['ResultCode']
        result_desc = callback['ResultDesc']

        # Log account reference if present
        account_reference = callback.get('AccountReference', 'N/A')
        print(f"Account Reference: {account_reference}")

        # Check if payment was successful
        if result_code == 0:

            callback_items = callback['CallbackMetadata']['Item']

            amount = callback_items[0]['Value']
            mpesa_receipt = callback_items[1]['Value']
            transaction_date = callback_items[3]['Value']
            user_phone_number = callback_items[4]['Value']

            print("Payment Successful")
            print("Amount:", amount)
            print("Receipt:", mpesa_receipt)
            print("Phone:", user_phone_number)
            print("Account Reference:", account_reference)

            # Save payment to database
            db = SessionLocal()
            try:
                transaction = Transaction(
                    merchant_request_id=merchant_request_id,
                    checkout_request_id=checkout_request_id,
                    result_code=result_code,
                    result_desc=result_desc,
                    amount=amount,
                    mpesa_receipt=mpesa_receipt,
                    transaction_date=str(transaction_date),
                    phone_number=str(user_phone_number),
                    account_reference=account_reference,
                    callback_data=json.dumps(stk_callback_response)
                )
                db.add(transaction)
                db.commit()
                print("Transaction saved to database")
            except Exception as e:
                db.rollback()
                print(f"Error saving to database: {e}")
            finally:
                db.close()

        else:
            print("Payment Failed")
            print(result_desc)
            print("Account Reference:", account_reference)

            # Save failed transaction to database as well
            db = SessionLocal()
            try:
                transaction = Transaction(
                    merchant_request_id=merchant_request_id,
                    checkout_request_id=checkout_request_id,
                    result_code=result_code,
                    result_desc=result_desc,
                    account_reference=account_reference,
                    callback_data=json.dumps(stk_callback_response)
                )
                db.add(transaction)
                db.commit()
                print("Failed transaction saved to database")
            except Exception as e:
                db.rollback()
                print(f"Error saving to database: {e}")
            finally:
                db.close()

        return JSONResponse({
            "ResultCode": 0,
            "ResultDesc": "Accepted"
        })

    except Exception as e:
        print("Error:", str(e))

        return JSONResponse({
            "ResultCode": 1,
            "ResultDesc": "Error processing callback"
        })