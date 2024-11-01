# grocery-comparison
Requests-based data aggregation app that generates requests for the product inventory API of the Ingles grocery store chain website for a given product and returns a given quantity of the cheapest inventory in the form (Name, Price, Weight, Price per Unit) and indicates if a product is on sale, its sale price, and whether a store card is required. Requests for misspelled or non-existent products are handled using the website suggestion API to display suggested products that the user might have meant to search for.

### Example of output displaying data displayed
```
Tyson Chicken Breast Fillets 25 Oz, Normal Price $9̶.̶9̶8̶, Sale Price $8.98, 0.35, Card Required: Yes
```
Locally-hosted **TOML** used for http-header storage, **JSON** data generated dynamically for response data visualization

#### Grocery Stores Covered:
- Ingles ✅
- Food Lion ❌
- Walmart ❌
- Harris Teeter ❌
- Aldi ❌
- Lidl ❌
- IGA ❌
#### Files:
- **ingles.py**: Webscraper for the Ingles Inventory API
- **main.py**: Implementation of the Ingles scraper

## Example
```python
import ingles

product = ""
while product == "": #product can't be blank
    product = input("Enter product: ")
number_items_to_consider = 2 #number of cheapest items to display
ingles_scraper = ingles.Ingles(product) #create Ingles object to start a session
ingles_scraper.find_discounts(number_items_to_consider) #displays the two cheapest items found
```
## Output
```console
$~> Enter Product: chicken breast
2 Cheapest Items:
Fried Chicken Breast: Price: $2.19, Price per Measure: $2.19 per ea
Tyson Bone In Split Chicken Breast Family Pack: Price: $2.98, Price per Measure: $2.98 per lb
```
