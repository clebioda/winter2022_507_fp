# My GameCube ShopGoodwill Tree

## Start

Clone or download this repository into a folder run ```goodwill.py```.
Flask will start and navigate to http://127.0.0.1:5000/ to see the GameCube Goodwill tree.

## Important Notes

1. Please see ```requirements.txt``` for all dependencies. Use ```pip3 install -r requirements.txt```.
2. Occasionally, the headless browser may go to the shopgoodwill website where all the scripts have not run and will result in the necessary
information not be there when the crawling and scrapping. Refresh the index (homepage) to resolve the problem.
3. The guide I used to setup my headless browser can be found [here](https://www.scrapingbee.com/blog/selenium-python/)
4. This app crawls the shopgoodwill website and scraps eBay and Wikipedia.

## Interaction

1. On the homepage, the user will be presented a tree with 16 different GameCube categories.
2. Hover over a category to see which inner categories it includes or select a category.
3. Once a category is selected the user will be presented a table of the GameCube items in that category ordered by time ending soonest.
4. Scroll through the table and find an item you want to know more about.
5. Click the hyperlink below the picture or the "See eBay price" button. Both take you to the item detail page.
6. On the item detail page, users may go back to the tree by clicking the logo in the top left or they can visit the [shopgoodwill.com](https://shopgoodwill.com/home) and see if they want to make a bid.
7. Repeat and enjoy! 
