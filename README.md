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

# Description of Tree

The Tree has the following format:
- All Items
  - Individual Items
    - Consoles
      - For Parts
      - Working
    - Controllers
      - Wired
      - Wireless
    - Games
      - CIB
      - Game Incomplete
      - Disk Only
      - Case or Manual only
    - Accessories
  - Bundles
  - Uncategorized

The global tree is defined in the Flask index/homepage route. It is a global variable because the other routes need to have access to the tree see it can navigate to the node where it contains the items it needs for each category. It is defined in the index route function because when the homepage is refreshed, we want to easily reset the tree, so items are not inserted into the tree more than once. The tree is a tuple of tuples to easily group multiple item sets into a category so they can be easily retrieved.

There are two types of nodes in this tree:
1. Leaf nodes: these nodes contain a list of Goodwill class objects as it’s last parameter. Only leaf nodes have a list as their last element and these nodes always have a length of two: the category and the list of Goodwill items.
2. Internal nodes: these nodes consist of 3 or more items. The first item in the tuple will always be a string that defines the top-level category and following items are categories/leaf nodes it contains. It can have as many child categories as it wants preceding the top-level element.

To create and populate the tree, you can look at the follow code:
- Declaration of tree: line 210 ```goodwill.py```
- Creation of Goodwill Item: ```getAllGoodWillItems()``` when the user navigates to the home screen
- Categorization of Goodwill item ```parseKeyWords()``` in ```goodwill_helper_functions.py```
  - TL;DR categorizes item based on the item name and predefined list of words of commonly used words in listings determined by me
- Insertion of Goodwill item into tree after it gets scrapped line 95 goodwill.py
- ```goodwill_tree_helper_functions.py```
  - ```insertItem()``` - recursively goes through the tree and inserts the item
  - ```returnMergedItemList()``` - Goes through the entire tree structure to count the number of items in the given string category and returns the items. Always go throughs the whole tree.
