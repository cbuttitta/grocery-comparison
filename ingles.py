import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import re

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
        url_specifier = self.__get_url("api",self.product) #gets the url and appropriate heards for the ingles product api
        self.url = url_specifier['url']
        self.headers = self.__make_headers(url_specifier['headers'])
        self.page = self.session.get(self.url, headers=self.headers) #, allow_redirects=False
        #print("Accessing", self.url) #Debug: displays the url being accessed
        #print("Got response", self.page.status_code) #Debug: response code
        #print("Headers:\n", self.page.headers) #Debug: displays headers sent
        #print("Cookies:\n", self.page.cookies) #Debug: cookies sent
        with open("headers.json","w") as f:
            json.dump(json.loads(self.page.text),f,indent=4) #loads() converts the given string to good json with indent for pretty print
        return self.__process_json(json.loads(self.page.text))

    def __process_json(self, data): #returns a list of the items to be dealt with in item_calculate
        items = []
        if(data == None):
            with open("headers.json", "r") as file:
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
    
    def __get_url(self, where,product): #gets the appropriate url and headers with the needed variables such as date (now) and location(#3 Merrimack Avenue, Asheville, North Carolina)
        product = product.replace(" ", "%20").replace("\'", "%27")
        header_strings = {
            "main": { 
                "url":"https://shop.ingles-markets.com/",
                "headers":f''':authority:
shop.ingles-markets.com
:method:
GET
:path:
/
:scheme:
https
accept:
text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
accept-encoding:
gzip, deflate, br, zstd
accept-language:
en-US,en;q=0.9
cookie:
_ga=GA1.1.285166733.1729690743; _gcl_au=1.1.1965432026.1729690756; fp-session=%7B%22token%22%3A%22e6b38065c5bd96d832c53989e11ef59c%22%2C%22shopIntentModalLastViewedAt%22%3A1729697724352%7D; fp-pref=%7B%22store_id%22%3A%224677%22%7D; pref=%7B%22store_id%22%3A%224677%22%7D; fp-history=%7B%220%22%3A%7B%22name%22%3A%22%2Fcurbside-faq%22%7D%7D; _ga_53ZMPVPQGP=GS1.1.1729862627.5.1.1729867646.0.0.0; _ga_0MCW5VWV52=GS1.1.1729862644.5.1.1729867648.0.0.0; _ga_D3913E5LX9=GS1.1.1729862644.5.1.1729867648.0.0.0
if-modified-since:
{datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")}
priority:
u=0, i
sec-ch-ua:
"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"
sec-ch-ua-mobile:
?0
sec-ch-ua-platform:
"Linux"
sec-fetch-dest:
document
sec-fetch-mode:
navigate
sec-fetch-site:
none
sec-fetch-user:
?1
upgrade-insecure-requests:
1
user-agent:
Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'''
            },
            "api":{
                "url":f"https://api.freshop.ncrcloud.com/1/products?app_key=ingles_markets&fields=id%2Cidentifier%2Cattribution_token%2Creference_id%2Creference_ids%2Cupc%2Cname%2Cstore_id%2Cdepartment_id%2Csize%2Ccover_image%2Cprice%2Csale_price%2Csale_price_md%2Csale_start_date%2Csale_finish_date%2Cprice_disclaimer%2Csale_price_disclaimer%2Cis_favorite%2Crelevance%2Cpopularity%2Cshopper_walkpath%2Cfulfillment_walkpath%2Cquantity_step%2Cquantity_minimum%2Cquantity_initial%2Cquantity_label%2Cquantity_label_singular%2Cvarieties%2Cquantity_size_ratio_description%2Cstatus%2Cstatus_id%2Csale_configuration_type_id%2Cfulfillment_type_id%2Cfulfillment_type_ids%2Cother_attributes%2Cclippable_offer%2Cslot_message%2Ccall_out%2Chas_featured_offer%2Ctax_class_label%2Cpromotion_text%2Csale_offer%2Cstore_card_required%2Caverage_rating%2Creview_count%2Clike_code%2Cshelf_tag_ids%2Coffers%2Cis_place_holder_cover_image%2Cvideo_config%2Cenforce_product_inventory%2Cdisallow_adding_to_cart%2Csubstitution_type_ids%2Cunit_price%2Coffer_sale_price%2Ccanonical_url%2Coffered_together%2Csequence&include_offered_together=true&limit=24&q={product}&relevance_sort=asc&render_id=1729865348812&sort=relevance&store_id=4677&token=e6b38065c5bd96d832c53989e11ef59c",
                "headers": f''':authority:
api.freshop.ncrcloud.com
:method:
GET
:path:
/1/products?app_key=ingles_markets&fields=id%2Cidentifier%2Cattribution_token%2Creference_id%2Creference_ids%2Cupc%2Cname%2Cstore_id%2Cdepartment_id%2Csize%2Ccover_image%2Cprice%2Csale_price%2Csale_price_md%2Csale_start_date%2Csale_finish_date%2Cprice_disclaimer%2Csale_price_disclaimer%2Cis_favorite%2Crelevance%2Cpopularity%2Cshopper_walkpath%2Cfulfillment_walkpath%2Cquantity_step%2Cquantity_minimum%2Cquantity_initial%2Cquantity_label%2Cquantity_label_singular%2Cvarieties%2Cquantity_size_ratio_description%2Cstatus%2Cstatus_id%2Csale_configuration_type_id%2Cfulfillment_type_id%2Cfulfillment_type_ids%2Cother_attributes%2Cclippable_offer%2Cslot_message%2Ccall_out%2Chas_featured_offer%2Ctax_class_label%2Cpromotion_text%2Csale_offer%2Cstore_card_required%2Caverage_rating%2Creview_count%2Clike_code%2Cshelf_tag_ids%2Coffers%2Cis_place_holder_cover_image%2Cvideo_config%2Cenforce_product_inventory%2Cdisallow_adding_to_cart%2Csubstitution_type_ids%2Cunit_price%2Coffer_sale_price%2Ccanonical_url%2Coffered_together%2Csequence&include_offered_together=true&limit=24&q={product}&relevance_sort=asc&render_id=1729865348812&sort=relevance&store_id=4677&token=e6b38065c5bd96d832c53989e11ef59c
:scheme:
https
accept:
application/json, text/javascript, */*; q=0.01
accept-encoding:
gzip, deflate, br, zstd
accept-language:
en-US,en;q=0.9
origin:
https://shop.ingles-markets.com
priority:
u=1, i
referer:
https://shop.ingles-markets.com/shop
sec-ch-ua:
"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"
sec-ch-ua-mobile:
?0
sec-ch-ua-platform:
"Linux"
sec-fetch-dest:
empty
sec-fetch-mode:
cors
sec-fetch-site:
cross-site
user-agent:
Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'''
            }
        }
        return header_strings[where]
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