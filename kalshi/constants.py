DEMO_BASE_URL = "https://demo-api.kalshi.co"
PROD_BASE_URL = "https://api.elections.kalshi.com"
BASE_PATH = "/trade-api/v2"

BASE_URL = DEMO_BASE_URL

def use_demo():
	global BASE_URL
	BASE_URL = DEMO_BASE_URL 

def use_prod():
	global BASE_URL
	BASE_URL = PROD_BASE_URL 

