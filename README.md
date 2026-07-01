# Django Backend Setup Guide

## Installation

1. Navigate to the backend folder:

```bash
cd backend
```

2. Create a virtual environment:

```bash
python -m venv venv
source venv/Scripts/activate  # On Windows
# or
source venv/bin/activate  # On Mac/Linux
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the backend root:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
JWT_SECRET=your-jwt-secret-key-here
```

5. Run migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

6. Create superuser:

```bash
python manage.py createsuperuser
```

7. Seed initial data:

```bash
python manage.py shell
```

Then run:

```python
from apps.finance.models import Plan, WalletAddresses

# Create plans
Plan.objects.create(
    name='Starter',
    description='Perfect entry point for new investors.',
    min_amount=100,
    max_amount=999,
    roi=10,
    duration_days=14
)

Plan.objects.create(
    name='Silver',
    description='Balanced growth for serious investors.',
    min_amount=1000,
    max_amount=4999,
    roi=15,
    duration_days=21
)

Plan.objects.create(
    name='Gold',
    description='Higher returns for confident portfolios.',
    min_amount=5000,
    max_amount=9999,
    roi=20,
    duration_days=30
)

Plan.objects.create(
    name='Platinum',
    description='Premium tier with maximum yield.',
    min_amount=10000,
    max_amount=1000000,
    roi=25,
    duration_days=45
)

# Create wallet addresses
WalletAddresses.objects.create(
    btc='bc1qroyaledemoaddressbtcxxxxxxxxxxxxxxxxx',
    eth='0xRoyaleDemoEthAddress00000000000000000000',
    usdt='TRoyaleDemoUsdtTrc20Addressxxxxxxxxxxxx'
)

exit()
```

8. Run the development server:

```bash
python manage.py runserver 0.0.0.0:8000
```

## API Endpoints

### Authentication

- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Login user
- `GET /api/auth/profile/` - Get user profile
- `POST /api/auth/profile/update/` - Update profile
- `POST /api/auth/profile/verify-password/` - Verify password

### Finance

- `GET /api/finance/plans/` - Get all plans
- `GET /api/finance/wallets/` - Get wallet addresses
- `GET /api/finance/summary/` - Get dashboard summary
- `POST /api/finance/deposits/create/` - Create deposit
- `POST /api/finance/withdrawals/create/` - Create withdrawal
- `POST /api/finance/investments/create/` - Create investment
- `GET /api/finance/transactions/` - Get user transactions
- `GET /api/finance/my-data/` - Get user data

### KYC

- `POST /api/kyc/submit/` - Submit KYC
- `GET /api/kyc/get/` - Get user KYC
- `POST /api/kyc/contact-message/` - Submit contact message

### Admin (requires admin role)

- `GET /api/admin/users/` - List all users
- `GET /api/admin/transactions/` - List all transactions
- `POST /api/admin/kyc/status/` - Set KYC status
- `POST /api/admin/deposits/status/` - Set deposit status
- `POST /api/admin/withdrawals/status/` - Set withdrawal status
- `POST /api/admin/plans/upsert/` - Create/update plan
- `POST /api/admin/plans/delete/` - Delete plan
- `POST /api/admin/wallets/update/` - Update wallet addresses
- `GET /api/admin/messages/` - List messages
- `POST /api/admin/messages/status/` - Set message status
- `POST /api/admin/messages/delete/` - Delete message
- `GET /api/admin/data/` - Get all admin data

## Authentication

All authenticated endpoints require a Bearer token in the Authorization header:

```
Authorization: Bearer <JWT_TOKEN>
```

## Database Models

### Users

- User (Django built-in)
- UserRole (user/admin)
- Profile (referral code, referred_by)

### Finance

- Plan
- Deposit
- Withdrawal
- Investment
- Transaction
- WalletAddresses

### KYC

- KYC
- ContactMessage
"# grandroyaletrade-backend" 
"# grandroyaletrade-backend" 
"# grandroyaletrade-backend" 
