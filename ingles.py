import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re
import tomllib
class _Item():
    def __init__(self, item):
        self.name = item["name"]
        self.price = int(re.sub(r'[^0-9]', '', item["price"])) #remove all non-numeric values and make an int $7.19 -> 719
        if("sale_price" in item): #check if item is on sale and display that price
            self.old_price = self.price
            self.price = int(re.sub(r'[^0-9]', '', item["sale_price"]))
            self.on_sale = True
            if("store_card_required" in item):
                self.card_needed = 'Yes' if bool(item["store_card_required"]) == True else 'No'
        else:   
            self.on_sale = False
        if(re.sub('[a-zA-Z]', '', item["size"]) == ''): #size is 'lb'and has no numeric value
            self.size = (1,item["size"])
        else: #size has a numeric value
            self.size = (float(re.sub('[a-zA-Z]', '', item["size"])),re.sub(r'[^a-z]', '', item["size"])) #'7oz' -> (7, 'oz')
        self.price_per_measure = int(self.price/self.size[0])
class Ingles():
    def __init__(self, product):
        print("\033[31mIngles\033[0m") #prints Ingles in red
        self.name = "Ingles"
        self.session = requests.Session() #create sesison for coherency and authentic-looking requests
        self.product = product
        #self.soup = BeautifulSoup(self.page.content, "html.parser")
    
    def find_discounts(self,number_items_to_consider):
        items = self.__access_api()
        return self.__item_calculate(items,number_items_to_consider) #number of cheapest items to show
    def __access_api(self):
        url_specifier = self.__get_url(self.product) #gets the url and appropriate heards for the ingles product api
        self.url = url_specifier[1]
        self.headers = self.__make_headers(url_specifier[0])
        self.page = self.session.get(self.url, headers=self.headers) #, allow_redirects=False
        #print("Accessing", self.url) #Debug: displays the url being accessed
        #print("Got response", self.page.status_code) #Debug: response code
        #print("Headers:\n", self.page.headers) #Debug: displays headers sent
        #print("Cookies:\n", self.page.cookies) #Debug: cookies sent
        with open("data.json","w") as f:
            json.dump(json.loads(self.page.text),f,indent=4) #loads() converts the given string to good json with indent for pretty print
        return self.__process_json(json.loads(self.page.text))

    def __process_json(self, data): #returns a list of the items to be dealt with in item_calculate
        items = []
        if(data == None):
            with open("data.json", "r") as file:
                data = json.load(file)
        number_of_items = data["total"]
        for entity in data["items"]:
            items.append(_Item(entity)) #create a list of Item objects
        return items    
    def __item_calculate(self, items, number_of_items):
        print("Name, Price, Price per Measure, Size, Price per Measure")
        print("-" * 25)
        for item in items:
            if(item.on_sale):
                print("{}, Normal Price ${}, Sale Price ${}, {}, Card Required: {}".format(item.name, self.__strikethrough(str(float(item.old_price/100))), float(item.price/100), float(item.price_per_measure/100), item.card_needed)) #convert cents to dollars with /100
            else:
                print("{}, ${}, ${}".format(item.name, float(item.price/100), float(item.price_per_measure/100))) #convert cents to dollars with /100
        sorted_items = self.__quick_sort(items)
        print("\n{} Cheapest Items:".format(number_of_items))
        for item in sorted_items[0:number_of_items]:
            if(item.on_sale):
                print("{}: Old Price ${:.2f}, Sale Price ${:.2f}, {}, Card Required: {}".format(item.name, float(item.old_price/100), float(item.price/100), float(item.price_per_measure/100), item.card_needed))
            else:
                print("{}: Price: ${:.2f}, Price per Measure: ${:.2f} per {}".format(item.name, float(item.price/100), float(item.price_per_measure/100), item.size[1]))
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
    
    def __get_url(self, product): #gets the appropriate url and headers with the needed variables such as date (now) and location(#3 Merrimack Avenue, Asheville, North Carolina)
        product = product.replace(" ", "%20").replace("\'", "%27")
        with open("headers/ingles.toml", "rb") as file:
            data = tomllib.load(file)

        # Access multiline strings
        headers = data["headers"]["api"].format(product=product, date=datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT"))
        url = data["url"]["api"].format(product=product)
        return (headers,url)
'''
Process:
1. Access Ingles Product Inventory API
2. Set the location and requets time in the headers and request website
4. Process response json and create an array of items: their names,their prices, price per given unit, on sale?, the sale price (if so). Format like so: Boar's Head Swiss Cheese, With Interleaf $7.19, price(7.19)/amount(7 oz)
5. Find the given number of lowest prices
6. Display them
7. Return them
8. Overhead program will display the cheapest option among those found
'''