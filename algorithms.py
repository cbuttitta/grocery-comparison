import requests
import json
from datetime import datetime
import re
import tomllib
class _Item():
    def __init__(self, item, store):
        self.name = item["name"] #name of the item
        match store:
            case "walmart":
                self.type="walmart"
                #self.in_stock = (item["availabilityStatusV2"]["display"] == "In Stock")
                self.price = int(re.sub(r'[^0-9]', '', item["priceInfo"]["currentPrice"]["priceString"])) #remove all non-numeric values and make an int $7.19 -> 719
                self.on_sale = False   
                if item["priceInfo"]["unitPrice"] and "unitPrice" in item["priceInfo"]:
                    self.price_per_measure = item["priceInfo"]["unitPrice"]["priceString"] 
                else:
                     self.price_per_measure = "N/A" #price per listed measure in size
            case "ingles":                           
                self.type = "ingles"
                self.price = int(re.sub(r'[^0-9]', '', item["price"])) #remove all non-numeric values and make an int $7.19 -> 719
                self.on_sale = False                
                if("sale_price" in item): #check if item is on sale and display that price
                    self.old_price = self.price #the usual price                    
                    self.price = int(re.sub(r'[^0-9]', '', item["sale_price"])) #resets price to the sales price for calculaiton purposes
                    self.on_sale = True
                    if("store_card_required" in item):
                        self.card_needed = 'Yes' if bool(item["store_card_required"]) == True else 'No'
                if(re.sub('[a-zA-Z]', '', item["size"]) == ''): #size is something like 'lb' and has no numeric value
                    self.size = (1,item["size"])
                else: #size has a numeric value like '7oz'
                    self.size = (float(re.sub('[a-zA-Z]', '', item["size"])),re.sub(r'[^a-z]', '', item["size"])) #'7oz' -> (7, 'oz')
                self.unit = "$" if float((self.price/100)/self.size[0]) > 1 else "¢" 
                self.price_per_measure = str(round(float((self.price/100)/self.size[0]),2)) + " "+ self.unit + "/" + self.size[1] #price per listed measure in size
            case _:
                self.type = "unknown"
                self.price = 0        
                self.price_per_measure = 0             
                self.store = store
                self.size=(0,"")
class Ingles():
    def __init__(self, product):
        print("\033[31mIngles\033[0m") #prints Ingles in red
        self.store = "ingles"
        self.session = requests.Session() #create sesison for coherency and authentic-looking requests
        self.product = product
    def find_discounts(self,number_items_to_consider):
        items = self.__access_api()
        return self.__item_calculate(items,number_items_to_consider) #number of cheapest items to show
    def __access_api(self):
        url_specifier = self.__get_url(self.product,"api") #gets the url and appropriate heards for the ingles product api
        self.url = url_specifier[1]
        self.headers = self.__make_headers(url_specifier[0])
        self.page = self.session.get(self.url, headers=self.headers)
        with open(f"data/{self.store}_data.json""w") as f:
            json.dump(json.loads(self.page.text),f,indent=4) #loads() converts the given string to good json with indent for pretty print
        return self.__process_json(json.loads(self.page.text))

    def __process_json(self, data): #returns a list of the items to be dealt with in item_calculate
        items = []
        if(data == None):
            with open(f"data/{self.store}_data.json", "r") as file:
                data = json.load(file)
        number_of_items = data["total"]
        if(number_of_items == 0): #check if there are any items listed, and if not check suggestions url
            print("No items found!")
            print("Did you mean?:",self.__get_suggestions())
            exit()
        for entity in data["items"]:
            items.append(_Item(entity, self.store)) #create a list of Item objects
        return items    
    def __item_calculate(self, items, number_of_items):
        sorted_items = self.__quick_sort(items)
        return sorted_items[0:number_of_items]
    def __quick_sort(self, array):
        elements = len(array)
    
        #Base case
        if elements < 2:
            return array
        current_position = 0 #Position of the partitioning element

        for i in range(1, elements): #Partitioning loop
            if array[i].price <= array[0].price:
                current_position += 1
                temp = array[i]
                array[i] = array[current_position]
                array[current_position] = temp

        temp = array[0]
        array[0] = array[current_position] 
        array[current_position] = temp #Brings pivot to it's appropriate position
        
        left = self.__quick_sort(array[0:current_position]) #Sorts the elements to the left of pivot
        right = self.__quick_sort(array[current_position+1:elements]) #sorts the elements to the right of pivot

        array = left + [array[current_position]] + right #Merging everything together
        
        return array
    def __strikethrough(self, text):
        return ''.join(char + '\u0336' for char in text)
    def __make_headers(self, header_string): #makes python dicitonary of copy and paste headers from network inspect
        headers = {} 
        for x in range(0,len(header_string.splitlines()),2):
            headers[header_string.splitlines()[x].replace(":","")] = header_string.splitlines()[x+1]
        return headers
    
    def __get_suggestions(self):
        url_specifier = self.__get_url(self.product,"suggestions") #gets the url and appropriate heards for the ingles product api
        self.url = url_specifier[1]
        self.headers = self.__make_headers(url_specifier[0])
        self.page = self.session.get(self.url, headers=self.headers) #, allow_redirects=False
        data = json.loads(self.page.text)
        if("did_you_mean" in data):
            response = ", ".join(data["did_you_mean"]) if type (data["did_you_mean"]) == list else data["did_you_mean"]
        else:
            response = "No suggestions found"
        return response
    def __get_url(self, product, which): #gets the appropriate url and headers with the needed variables such as date (now) and location(#3 Merrimack Avenue, Asheville, North Carolina)
        product = product.replace(" ", "%20").replace("\'", "%27")
        with open("headers/headers.toml", "rb") as file:
            data = tomllib.load(file)

        # Access multiline strings
        #headers = data["headers"][which].format(product=product, date=datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT"))
        #url = data["url"][which].format(product=product)
        headers = data["headers"][f"{self.store}.{which}"].format(product=product, date=datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT"))
        url = data["url"][f"{self.store}.{which}"].format(product=product)
        return (headers,url)

class Walmart():
    def __init__(self, product):
        print("\033[34mWalmart\033[0m") #prints Walmart in blue
        self.store = "walmart"
        self.session = requests.Session() #create sesison for coherency and authentic-looking requests
        self.product = product
    def find_discounts(self,number_items_to_consider):
        items = self.__access_api()
        return self.__item_calculate(items,number_items_to_consider) #number of cheapest items to show
    def __access_api(self):
        url_specifier = self.__get_url(self.product,"api") #gets the url and appropriate headers for the walmart product api
        self.url = url_specifier[1]
        self.headers = self.__make_headers(url_specifier[0])
        self.page = self.session.get(self.url, headers=self.headers)
        with open(f"data/{self.store}_data.json","w") as f:
            json.dump(json.loads(self.page.text),f,indent=4) #loads() converts the given string to good json with indent for pretty print
        return self.__process_json(json.loads(self.page.text))

    def __process_json(self, data): #returns a list of the items to be dealt with in item_calculate
        items = []
        if(data == None):
            with open(f"data/{self.store}_data.json", "r") as file:
                data = json.load(file)
        #number_of_items = data["ItemStacks"][0]["total"]
        '''if(number_of_items == 0): #check if there are any items listed, and if not check suggestions url
            print("No items found!")
            print("Did you mean?:",self.__get_suggestions())
            exit()'''
        item_catalog = data["data"]["search"]["searchResult"]["itemStacks"][0]["itemsV2"]
        with open(f"data/{self.store}_data_catalog.json","w") as f:
            json.dump(item_catalog,f,indent=4)
        for entity in item_catalog:
            if entity["__typename"] == "Product":
                items.append(_Item(entity,self.store)) #create a list of Item objects
        
        return items    
    def __item_calculate(self, items, number_of_items):
        sorted_items = self.__quick_sort(items)
        return sorted_items[0:number_of_items]
    def __quick_sort(self, array):
        elements = len(array)
    
        #Base case
        if elements < 2:
            return array
        current_position = 0 #Position of the partitioning element

        for i in range(1, elements): #Partitioning loop
            if array[i].price <= array[0].price:
                current_position += 1
                temp = array[i]
                array[i] = array[current_position]
                array[current_position] = temp

        temp = array[0]
        array[0] = array[current_position] 
        array[current_position] = temp #Brings pivot to its appropriate position
        
        left = self.__quick_sort(array[0:current_position]) #Sorts the elements to the left of pivot
        right = self.__quick_sort(array[current_position+1:elements]) #sorts the elements to the right of pivot

        array = left + [array[current_position]] + right #Merging everything together
        
        return array
    def __strikethrough(self, text):
        return ''.join(char + '\u0336' for char in text)
    def __make_headers(self, header_string): #makes python dicitonary of copy and paste headers from network inspect
        headers = {} 
        for x in range(0,len(header_string.splitlines()),2):
            headers[header_string.splitlines()[x].replace(":","")] = header_string.splitlines()[x+1]
        return headers
    
    def __get_suggestions(self):
        url_specifier = self.__get_url(self.product,"suggestions") #gets the url and appropriate heards for the ingles product api
        self.url = url_specifier[1]
        self.headers = self.__make_headers(url_specifier[0])
        self.page = self.session.get(self.url, headers=self.headers) #, allow_redirects=False
        data = json.loads(self.page.text)
        if("did_you_mean" in data):
            response = ", ".join(data["did_you_mean"]) if type (data["did_you_mean"]) == list else data["did_you_mean"]
        else:
            response = "No suggestions found"
        return response
    def __get_url(self, product, which): #gets the appropriate url and headers with the needed variables such as date (now) and location(#3 Merrimack Avenue, Asheville, North Carolina)
        product = product.replace(" ", "%20").replace("\'", "%27")
        with open("headers/headers.toml", "rb") as file:
            data = tomllib.load(file)

        # Access multiline strings
        headers = data["headers"][f"{self.store}.{which}"].format(product=product, date=datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT"))
        url = data["url"][f"{self.store}.{which}"].format(product=product)
        return (headers,url)   