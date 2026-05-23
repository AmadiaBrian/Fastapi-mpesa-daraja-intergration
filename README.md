# M-Pesa Daraja API - FastAPI

A comprehensive FastAPI application for M-Pesa STK push payments with real-time transaction tracking, callback handling, and database integration.

## Features

- **STK Push Payment Initiation** - Send payment requests to M-Pesa users
- **Real-time Payment Status Tracking** - Professional modals showing payment progress (initiated, cancelled, successful, timeout, insufficient balance, wrong PIN, invalid credentials, invalid amount, invalid phone)
- **Database Integration** - Store all transactions in SQLite database with full details
- **Transaction History** - View all transactions via dedicated endpoint
- **Callback Handling** - Receive and log M-Pesa callbacks with timestamps
- **Phone Number Validation** - Format validation (07XXXXXXXX or 01XXXXXXXX) with auto-conversion to international format (254 prefix)
- **Professional UI** - Modern black/orange theme with responsive design
- **Polling System** - Database-based status checking to avoid API rate limits
- **Comprehensive Error Handling** - Modals for all common M-Pesa error codes

## Setup

### Prerequisites
- Python 3.7 or higher
- M-Pesa Daraja Developer Account
- Valid Consumer Key and Consumer Secret from Safaricom Developer Portal

### Installation

1. Clone or download the project

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Configuration

1. **Update M-Pesa Credentials** in `genrateAcesstoken.py`:
```python
consumer_key = "YOUR_CONSUMER_KEY"
consumer_secret = "YOUR_CONSUMER_SECRET"
```

2. **Update Callback URL** in `app.py` (line 48):
   - Use your public URL (Safaricom requires publicly accessible callback URL)
   - Example: `callback_url: str = Form('https://your-domain.com/stk-callback')`
   - For local testing, use ngrok: `ngrok http 8000`

3. **Database Configuration** in `database.py`:
   - Default: `sqlite:///database.db`
   - Change the filename if needed

## Running the Application

### Start the Main Application
```bash
uvicorn app:app --reload
```
Or double-click `run.bat` (if available)

Access at: `http://127.0.0.1:8000`

### Using the Payment System

1. Navigate to `http://127.0.0.1:8000`
2. Enter the amount (minimum 1)
3. Enter phone number in format: 07XXXXXXXX or 01XXXXXXXX
4. Click "Send Payment Request"
5. Enter PIN on your phone when prompted
6. Watch the modal for real-time payment status updates

## API Endpoints

### Main Endpoints
- `GET /` - Main payment form page
- `POST /initiate/` - Initiate STK push payment
  - Parameters: amount, phone, callback_url, passkey, business_short_code, party_b, account_reference, transaction_desc
  - Returns: CheckoutRequestID or error message

### Status & Query Endpoints
- `GET /check-status/?checkout_request_id=<id>` - Check transaction status from database
  - Returns: Transaction details (result_code, result_desc, amount, mpesa_receipt)

- `GET /transactions/` - View all transaction history
  - Returns: HTML page with all transactions sorted by date (newest first)

### Utility Endpoints
- `GET /accesstoken/` - Get M-Pesa access token
- `GET /query/` - Query STK status from Safaricom (legacy, not used by UI)

### Callback Endpoint
- `POST /stk-callback` - Receive M-Pesa callbacks
  - Automatically logs to `Mpesastkresponse.json`
  - Saves transaction to database

## Database Schema

The SQLite database (`database.db`) stores transactions with the following fields:

- `id` - Primary key
- `merchant_request_id` - Unique merchant request ID
- `checkout_request_id` - M-Pesa checkout request ID
- `result_code` - Transaction result code (0=success, 1032=cancelled, 1=insufficient balance, etc.)
- `result_desc` - Transaction result description
- `amount` - Transaction amount
- `mpesa_receipt` - M-Pesa receipt number
- `transaction_date` - Transaction date
- `phone_number` - Customer phone number
- `account_reference` - Account reference
- `callback_data` - Full callback JSON data
- `created_at` - Database record creation timestamp

## Payment Status Codes

| Code | Description | Modal Shown |
|------|-------------|-------------|
| 0 | Success | Green checkmark - Payment Successful |
| 1 | Insufficient balance | Warning icon - Insufficient Balance |
| 1032 | Cancelled by user | Red X - Payment Cancelled |
| 1037 | Timeout | Clock icon - Payment Timed Out |
| 2001 | Invalid initiator information (wrong PIN) | Lock icon - Wrong PIN |
| 2002 | Invalid credentials | Red X - Invalid Credentials |
| 2004 | Invalid amount | Red X - Invalid Amount |
| 2005 | Invalid phone number | Red X - Invalid Phone Number |

## File Structure

```
mpesa-python1/
├── app.py                      # Main FastAPI application
├── database.py                 # SQLAlchemy database models and setup
├── callback.py                 # Callback handler for M-Pesa responses
├── genrateAcesstoken.py        # M-Pesa access token generation
├── requirements.txt            # Python dependencies
├── database.db                 # SQLite database (auto-created)
├── Mpesastkresponse.json       # Callback log file
├── templates/
│   ├── index.html             # Main payment form
│   └── transactions.html      # Transaction history page
└── static/
    ├── css/
    │   └── style.css          # Application styles
    └── js/
        └── script.js          # Frontend JavaScript
```

## Troubleshooting

### "Access token not found" error
- Verify your Consumer Key and Secret in `genrateAcesstoken.py`
- Check your internet connection
- Ensure you're using sandbox credentials for testing

### Callback not received
- Ensure callback URL is publicly accessible
- Use ngrok for local testing: `ngrok http 8000`
- Check firewall settings
- Verify callback URL format in app.py

### Payment status not updating
- Check browser console for JavaScript errors
- Verify database file exists and is writable
- Check server logs for database errors
- Ensure polling is working (check console logs)

### Database connection issues
- Ensure `database.db` file exists in project root
- Check file permissions
- Verify DATABASE_URL in `database.py`

## Security Notes

- Never commit Consumer Key and Secret to version control
- Use environment variables for credentials in production
- Implement proper authentication for production deployment
- Use HTTPS for all production endpoints
- Validate and sanitize all user inputs

## Production Deployment

1. Use environment variables for credentials
2. Deploy to a cloud provider (Heroku, AWS, etc.)
3. Use a production-grade database (PostgreSQL, MySQL)
4. Implement proper logging and monitoring
5. Set up SSL/TLS certificates
6. Implement rate limiting
7. Add authentication and authorization

## Support

For issues or questions:
- Check the M-Pesa Daraja documentation: https://developer.safaricom.co.ke/
- Review callback logs in `Mpesastkresponse.json`
- Check browser console for JavaScript errors
- Review server logs for backend errors
