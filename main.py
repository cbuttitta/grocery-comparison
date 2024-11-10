from algorithms import Ingles, Walmart

product = ""
while product == "": #product can't be blank
    product = input("Enter product: ")
number_items_to_consider = 2 #number of cheapest items to display
item_list = [] #empty list to store items
walmart_scraper = Walmart(product) #create Walmart object to start a session
item_list += walmart_scraper.find_discounts(number_items_to_consider) #returns the two cheapest items found and adds the to a list
ingles_scraper = Ingles(product) #create Walmart object to start a session
item_list += ingles_scraper.find_discounts(number_items_to_consider) #returns the two cheapest items found and adds the to a list
print("Name, Price, Price per Measure, Size, Price per Measure")
print("-" * 25)
for item in item_list:
    if(item.on_sale):
        print("{} {}: Old Price ${:.2f}, Sale Price ${:.2f}, Card Required: {}, Price per Measure: {}".format(item.type, item.name, float(item.old_price/100), float(item.price/100), item.card_needed, item.price_per_measure ))
    else:
        print("{} {}: Price: ${:.2f}, Price per Measure: {}".format(item.type, item.name, float(item.price/100), item.price_per_measure))

