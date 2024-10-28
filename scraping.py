import ingles

product = input("Enter product: ")
number_items_to_consider = 2 #number of cheapest items to display
ingles_scraper = ingles.Ingles(product) #create Ingles object to start a session
ingles_scraper.find_discounts(number_items_to_consider) #displays the two cheapest items found


