import requests
from decimal import Decimal
from django.core.cache import cache

class CalculatorService:
    """Service for working with cryptocurrencies"""
    
    COINGECKO_API = 'https://api.coingecko.com/api/v3'
    CACHE_TIMEOUT = 300
    
    @staticmethod
    def get_crypto_price(crypto_id, vs_currency='usd'):
        """Getting cryptocurrency prices with caching"""
        cache_key = f'crypto_price_{crypto_id}_{vs_currency}'
        cached_price = cache.get(cache_key)
        
        if cached_price:
            return cached_price
        
        try:
            url = f'{CalculatorService.COINGECKO_API}/simple/price'
            params = {
                'ids': crypto_id,
                'vs_currencies': vs_currency,
                'include_market_cap': 'false',
                'include_24hr_vol': 'false'
            }
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            price = data.get(crypto_id, {}).get(vs_currency)
            
            if price:
                cache.set(cache_key, price, CalculatorService.CACHE_TIMEOUT)
                return price
            
            return None
        except requests.exceptions.RequestException as e:
            print(f'Error fetching price: {e}')
            return None
    
    @staticmethod
    def convert_crypto(from_crypto, to_crypto, amount):
        """Converting one cryptocurrency to another"""
        from_price = CalculatorService.get_crypto_price(from_crypto)
        to_price = CalculatorService.get_crypto_price(to_crypto)
        
        if not from_price or not to_price:
            return None, None
        
        result = Decimal(str(amount)) * (Decimal(str(from_price)) / Decimal(str(to_price)))
        rate = Decimal(str(from_price)) / Decimal(str(to_price))
        
        return float(result), float(rate)
    
    @staticmethod
    def convert_crypto_to_fiat(crypto_id, amount, fiat_currency='usd'):
        """Converting cryptocurrency to fiat currency"""
        price = CalculatorService.get_crypto_price(crypto_id, fiat_currency)
        
        if not price:
            return None
        
        result = Decimal(str(amount)) * Decimal(str(price))
        return float(result)