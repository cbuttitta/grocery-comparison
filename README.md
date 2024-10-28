# grocery-comparison
Requests and BeautifulSoup4-based web scraping app that scrapes the website for the Ingles grocery store chain for a given product and returns inventory in the form (Name, Price, Weight, Price per Unit) and indicates if a product is on sale, its sale price, and whether a store card is required.
```
Tyson Chicken Breast Fillets 25 Oz, Normal Price $9̶.̶9̶8̶, Sale Price $8.98, 0.35, Card Required: Yes
```
###TOML### used for header storage, ###JSON### used for reponse data visualization

#### Grocery Stores Covered:
- Ingles ✅
- Food Lion ❌
- Walmart ❌
- Harris Teeter ❌
- Aldi ❌
- Lidl ❌
- IGA ❌

## Example
```python
import ingles

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
