#!/bin/bash

# Django Backend Setup Script
# This script initializes the Django backend with migrations and seed data

echo "================================"
echo "Grand Royal Elite Trade Backend Setup"
echo "================================"
echo ""

# Change to backend directory
cd "$(dirname "$0")"

echo "Step 1: Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "Step 2: Running migrations..."
python manage.py makemigrations
python manage.py migrate

echo ""
echo "Step 3: Creating superuser..."
echo "Please enter credentials for the admin user:"
python manage.py createsuperuser

echo ""
echo "Step 4: Seeding initial data..."
python manage.py shell << END
from apps.finance.models import Plan, WalletAddresses

# Create investment plans
Plan.objects.get_or_create(
    name="Starter",
    defaults={
        "description": "Perfect for beginners",
        "min_amount": 100,
        "max_amount": 999,
        "roi": 5.0,
        "duration_days": 30
    }
)

Plan.objects.get_or_create(
    name="Silver",
    defaults={
        "description": "For growing investors",
        "min_amount": 1000,
        "max_amount": 4999,
        "roi": 8.0,
        "duration_days": 30
    }
)

Plan.objects.get_or_create(
    name="Gold",
    defaults={
        "description": "For serious investors",
        "min_amount": 5000,
        "max_amount": 24999,
        "roi": 12.0,
        "duration_days": 30
    }
)

Plan.objects.get_or_create(
    name="Platinum",
    defaults={
        "description": "Elite investor program",
        "min_amount": 25000,
        "max_amount": 999999,
        "roi": 15.0,
        "duration_days": 30
    }
)

# Create or update wallet addresses
WalletAddresses.objects.all().delete()
WalletAddresses.objects.create(
    btc="1A1z7agoat3QT8kw3neZrngSv5K6iuvnF7",
    eth="0x742d35Cc6634C0532925a3b844Bc9e7595f42a1f",
    usdt="0xdAC17F958D2ee523a2206206994597C13D831ec7"
)

print("✓ 4 investment plans created")
print("✓ Wallet addresses configured")
print("")
print("Backend setup complete!")
END

echo ""
echo "================================"
echo "Setup Complete!"
echo "================================"
echo ""
echo "To start the server, run:"
echo "  python manage.py runserver"
echo ""
echo "Server will be available at:"
echo "  http://localhost:8000"
echo ""
echo "Admin panel:"
echo "  http://localhost:8000/admin"
