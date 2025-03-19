import requests
from decimal import Decimal
from django.conf import settings
from django.core.cache import cache

class CurrencyConverter:
    @staticmethod
    def convert(amount, from_currency, to_currency):
        if from_currency == to_currency:
            return amount
            
        # Check cache first
        cache_key = f"exchange_rate_{from_currency}_{to_currency}"
        rate = cache.get(cache_key)
        
        if not rate:
            # Use a free currency API (you'll need to register for an API key)
            api_key = settings.EXCHANGE_RATE_API_KEY
            url = f"https://api.exchangerate-api.com/v6/{api_key}/latest/{from_currency}"
            response = requests.get(url)
            data = response.json()
            
            if 'rates' in data and to_currency in data['rates']:
                rate = Decimal(str(data['rates'][to_currency]))
                # Cache for 24 hours
                cache.set(cache_key, rate, 60*60*24)
            else:
                raise Exception(f"Could not get exchange rate for {from_currency} to {to_currency}")
                
        return amount * rate
