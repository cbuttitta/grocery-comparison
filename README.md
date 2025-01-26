# grocery-comparison
Requests-based data aggregation app that generates requests for the product inventory API of the Ingles and Walmart grocery store websites for a given product and returns a given quantity of the cheapest inventory in the form (Name, Price, Weight, Price per Unit) and indicates if a product is on sale, its sale price, and whether a store card is required. Requests for misspelled or non-existent products are handled using the website suggestion API to display suggested products that the user might have meant to search for.

### Example of output displaying data displayed
```
Tyson Chicken Breast Fillets 25 Oz, Normal Price $9̶.̶9̶8̶, Sale Price $8.98, 0.35, Card Required: Yes
```
Locally-hosted **TOML** used for http-header storage, **JSON** data generated dynamically for response data visualization

#### Grocery Stores Covered:
- Ingles ✅
- Food Lion ❌
- Walmart ✅
- Harris Teeter ❌
- Aldi ❌
- Lidl ❌
- IGA ❌
#### Files:
- **algorithms.py**: Individualized web scrapers for the Respective Inventory APIs
- **main.py**: Implementation of the algorithms
## Example
```python
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
```
## Output
```console
$~> Enter Product: chicken breast
2 Cheapest Items:
Fried Chicken Breast: Price: $2.19, Price per Measure: $2.19 per ea
Tyson Bone In Split Chicken Breast Family Pack: Price: $2.98, Price per Measure: $2.98 per lb
```
