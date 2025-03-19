from django.db import migrations

def add_initial_currencies(apps, schema_editor):
    Currency = apps.get_model('budgets', 'Currency')
    
    currencies = [
        {'code': 'USD', 'name': 'US Dollar', 'symbol': '$'},
        {'code': 'EUR', 'name': 'Euro', 'symbol': '€'},
        {'code': 'GBP', 'name': 'British Pound', 'symbol': '£'},
        {'code': 'JPY', 'name': 'Japanese Yen', 'symbol': '¥'},
        {'code': 'NGN', 'name': 'Nigerian Naira', 'symbol': '₦'},
    ]
    
    for currency_data in currencies:
        Currency.objects.create(**currency_data)

def remove_currencies(apps, schema_editor):
    Currency = apps.get_model('budgets', 'Currency')
    Currency.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('budgets', '0002_add_currency_model'),  # Make sure this matches your previous migration
    ]
    
    operations = [
        migrations.RunPython(add_initial_currencies, remove_currencies),
    ]
