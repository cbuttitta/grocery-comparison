import ingles
#########
# Targets:
# Ingles
# Lowes Foods
# Food Lion
# Walmart
# Harris Teeter
# Aldi
# Lidl
# Publix
# IGA
# Whole Foods
# Trader Joe's
# IGA
# Wegman's
#########
url_map = {
    "Ingles": "https://shop.ingles-markets.com/",
    "Lowes Foods": "https://www.lowes.com/",
    "Food Lion": "https://www.foodlion.com/",
    "Walmart": "https://www.walmart.com/",
    "Harris Teeter": "https://www.harris-teeter.com/",
    "Aldi": "https://www.aldi.com/",
    "Lidl": "https://www.lidl.com/",
    "Publix": "https://www.publix.com/",
    "IGA": "https://www.iga.com/",
    "Whole Foods": "https://www.wholefoodsmarket.com/",
    "Trader Joe's": "https://www.traderjoes.com/",
    "Wegmans": "https://www.wegmans.com/",
    "Target": "https://target.com/",
}
product = input("Enter product: ")
number_items_to_consider = 2
ingles_scraper = ingles.Ingles(product)
ingles_scraper.find_discounts(number_items_to_consider)


