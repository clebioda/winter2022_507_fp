from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import cssutils
from goodwill_category import Category
from goodwill_class import GoodwillItem
import goodwill_driver_cache as DriverCache
import goodwill_cache as Cache
from bs4 import BeautifulSoup
from flask import Flask, redirect, render_template, url_for
from goodwill_helper_functions import getEbayItemAveragePrice, parseKeyWords

from goodwill_tree_helper_functions import insertItem, returnMergedItemList

def createDriver():
    '''Creates the web driver to drive the browser to load pages
    to be scrapped and crawled due to the JS on the pages that need to
    load
    ----------
    Parameters
    None
    Returns
    -------
    Driver
        webdriver (Firefox because the Chrome one stopped working halfway through this project)
    '''

    #Chrome options
    options = Options()
    options.headless = True
    options.add_argument("--window-size=1920,1200")
    #driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)

    # Firefox options
    firefox_driver_path = 'geckodriver.exe'
    fireFoxOptions = webdriver.FirefoxOptions()
    fireFoxOptions.headless = True
    driver = webdriver.Firefox(options=fireFoxOptions, executable_path=firefox_driver_path)
    return driver

def getAllGoodWillItems(driver):
    '''Crawls the Goodwill GameCube search page and retrieves all the GameCube items until
    it finds a page with no results on it. It will cache the page unless it is the first or last page
    because the first page has auctions ended soon so it needs up to date data and the last page can
    have new items added to it. It will also insert the item into the correct portion of the global
    tree structure.
    ----------
    Parameters
    driver: Driver
        web driver to navigate to the page
    Returns
    -------
    None
    '''

    page_number = 1
    while True:
        current_url = f'https://shopgoodwill.com/categories/listing?st=gamecube&sg=&c=&s=&lp=0&hp=999999&sbn=&spo=false&snpo=false&socs=false&sd=false&sca=false&caed=4%2F7%2F2022&cadb=7&scs=false&sis=false&col=1&p={page_number}&ps=40&desc=false&ss=0&UseBuyerPrefs=true&sus=false&cln=1&catIds=&pn=&wc=false&mci=false&hmt=false&layout=grid'
        driver_source = DriverCache.make_request_with_cache(driver, current_url, CACHE_All_ITEMS, CACHE_FILENAME, page_number)
        soup = BeautifulSoup(driver_source["source"], 'html.parser') if page_number != 1 else BeautifulSoup(driver_source, 'html.parser')
        table = soup.find("div", class_="p-dataview-content")

        # If no items are on the page, does not account for the page still loading though
        if table == None:
            # Don't want to cache last first page because new items could get added
            del CACHE_All_ITEMS[current_url]
            Cache.save_cache(CACHE_All_ITEMS, CACHE_FILENAME)
            break
        items = table.find_all("div", class_="p-col-12 item-col p-md-4 ng-star-inserted")
        for item in items:
            # Sometimes the page does not load fully and will have 6 items with no href
            try:
                item = item.find("div", class_="feat-item ng-star-inserted")
                item_path = item.find("a")["href"]
            except:
                # If the page does not load, we do not want to cache this item
                del CACHE_All_ITEMS[current_url]
                Cache.save_cache(CACHE_All_ITEMS, CACHE_FILENAME)
                break
            item_name = item.find("a", class_="feat-item_name ng-star-inserted").text.strip()
            item_price = item.find("p", class_="feat-item_price").text.strip()
            item_bottom = item.find("ul", class_="feat-item_bottom ng-star-inserted").find_all("li")
            if len(item_bottom) >= 3:
                item_bids = item_bottom[0].text.strip().split()[1]
                item_time_left = item_bottom[1].text.strip()[16:]
            # Some items are not up for auction and are only available as "Buy It Now"
            elif len(item_bottom) == 2:
                item_bids = "Buy It Now Only"
                item_time_left = item_bottom[0].text.strip()[16:]
            # Some items are left up until they are bought (usually really expensive items)
            else:
                item_bids = "Buy It Now Only"
                item_time_left = "No Time Limit"
            item_image = item.find("a").find("img", class_="feat-item_img")["src"]
            goodwill_item = GoodwillItem(item_title=item_name, item_path=item_path, item_price=item_price, ebay_avg_price=0, item_bids=item_bids, item_time_left=item_time_left, item_image=item_image)
            insertItem(tree, goodwill_item)
        page_number += 1


def getGoodWillItemDetails(driver, path):
    '''Crawls the Goodwill item page to be scraped and gets the average
    eBay price.
    ----------
    Parameters
    driver: Driver
        web driver to navigate to the page
    path: string
        item id used to navigate to the url to scrap
    Returns
    -------
    json:
        item detail in json form
    '''
    full_path = GOODWILL_PATH + path
    driver_source = DriverCache.make_request_with_cache(driver, full_path, CACHE_ITEM_DETAILS, CACHE_FILENAME_DETAIL, cache_expiration=10, sleep_time=0.5)
    item_soup = BeautifulSoup(driver_source["source"], 'html.parser')

    item_id = path.split('/')[-1]

    # Item Title
    item_title = item_soup.find(id=item_id).text

    # Image urls
    images_urls = item_soup.find_all("a", class_='ngx-gallery-thumbnail')
    item_image_list_urls = []
    for image_url in images_urls:
        style_unparsed = image_url['style']
        style = cssutils.parseStyle(style_unparsed, validate=False)
        url = style['background-image']
        url_trimmed = url[4: -1]
        item_image_list_urls.append(url_trimmed)

    item_time_left_and_bids = item_soup.find(class_="border-top border-bottom py-2 medium mb-4").find_all('span', class_="ng-star-inserted")
    # Stardard auction
    if len(item_time_left_and_bids) == 3:
        # Item Time Left
        start = item_time_left_and_bids[0].text.find(":")
        end = item_time_left_and_bids[0].text.find("(")
        item_time_left = item_time_left_and_bids[0].text[start+1: end].strip()
        # Item Bids
        item_bids = item_time_left_and_bids[1].find(class_="d-print-inline-block d-none").text
        # Item Current Price
        item_current_price = item_soup.find(class_='row mb-2').find(class_='col-4 text-right').find('h3').text.strip()
    # Buy it now with time limit
    elif len(item_time_left_and_bids) == 1:
        # Item Time Left
        start = item_time_left_and_bids[0].text.find(":")
        end = item_time_left_and_bids[0].text.find("(")
        item_time_left = item_time_left_and_bids[0].text[start+1: end]
        # Item Bids
        item_bids = "Buy it Now"
        # Item Current Price
        item_current_price = item_soup.find(class_='lead mb-0').find(class_='ng-star-inserted').text.strip()
    # BUy it now no time limit
    elif len(item_time_left_and_bids) == 0:
        item_time_left = "No Time Limit"
        item_bids = "Buy it Now"
        # Item Current Price
        item_current_price = item_soup.find(class_='lead mb-0').find(class_='ng-star-inserted').text.strip()

    # Item Handling Price
    item_handling_price = "Not Provided"
    info_table = item_soup.find(class_='py-3 py-md-4 px-3 px-md-4 item-info-box br7 mb-3 mb-md-0').find_all('tr')
    for row in info_table:
        if "handling" in row.text.lower():
            item_handling_price = row.find('td').text

    category = parseKeyWords(item_title)
    if category in [Category.bundles.value, Category.uncategorized.value]:
        ebay_price = "Could not find any recent sales"
    else:
        ebay_price = getEbayItemAveragePrice(item_title)

    item_detail = { "name": item_title, "link": full_path ,"time_left": item_time_left, "ebay_price": ebay_price, "price": item_current_price, "handling_price": item_handling_price ,"bids": item_bids, "images": item_image_list_urls}
    return item_detail

# GLOBALS
CACHE_FILENAME = "files/goodwill_cache.json"
CACHE_FILENAME_DETAIL = "files/goodwill_cache_detail.json"

CACHE_All_ITEMS = Cache.open_cache(CACHE_FILENAME)
CACHE_ITEM_DETAILS = Cache.open_cache(CACHE_FILENAME_DETAIL)

DRIVER_PATH = 'chromedriver'
GOODWILL_PATH = 'https://shopgoodwill.com'

TITLE_DICT = {
    "All_Items": "GameCube All Items",
    "Individual_Items": "GameCube Individual Items",
    "Consoles": "GameCube Consoles",
    Category.for_parts.value: "GameCube Consoles For Parts",
    Category.working.value: "GameCube Consoles Working",
    "Controllers": "GameCube Controllers",
    Category.wired.value: "GameCube Controllers Wired",
    Category.wireless.value: "GameCube Controllers Wireless",
    "Games": "GameCube Games",
    Category.complete_in_box.value: "GameCube Games Complete in Box",
    Category.game_incomplete.value: "GameCube Games Incomplete",
    Category.disk_only.value: "GameCube Games Disc Only",
    Category.case_manuel_only.value: "GameCube Games Case/Manuel Only",
    Category.accessories.value: "GameCube Accessories",
    Category.bundles.value: "GameCube Bundles",
    Category.uncategorized.value: "Uncategorized GameCube Items",
}

app = Flask(__name__)

@app.route('/')
def index():
    global tree
    tree = \
    ("All_Items",
        (("Individual_Items",
            ("Consoles",
                (Category.for_parts.value, []),
                (Category.working.value, [])),
            ("Controllers",
                (Category.wired.value, []),
                (Category.wireless.value, [])),
            ("Games",
                (Category.complete_in_box.value, []),
                (Category.game_incomplete.value, []),
                (Category.disk_only.value, []),
                (Category.case_manuel_only.value, [])),
            (Category.accessories.value, []))),
        (Category.bundles.value, []),
        (Category.uncategorized.value, []))
    driver = createDriver()
    getAllGoodWillItems(driver)
    item_count_list = [
        len(returnMergedItemList(tree, "All_Items")),
        len(returnMergedItemList(tree, "Individual_Items")),
        len(returnMergedItemList(tree, "Consoles")),
        len(returnMergedItemList(tree, Category.for_parts.value)),
        len(returnMergedItemList(tree, Category.working.value)),
        len(returnMergedItemList(tree, "Controllers")),
        len(returnMergedItemList(tree, Category.wired.value)),
        len(returnMergedItemList(tree, Category.wireless.value)),
        len(returnMergedItemList(tree, "Games")),
        len(returnMergedItemList(tree, Category.complete_in_box.value)),
        len(returnMergedItemList(tree, Category.game_incomplete.value)),
        len(returnMergedItemList(tree, Category.disk_only.value)),
        len(returnMergedItemList(tree, Category.case_manuel_only.value)),
        len(returnMergedItemList(tree, Category.accessories.value)),
        len(returnMergedItemList(tree, Category.bundles.value)),
        len(returnMergedItemList(tree, Category.uncategorized.value)),
    ]
    driver.quit()
    return render_template('home.html',
        all_item_count=item_count_list[0],
        individual_item_count=item_count_list[1],
        console_item_count=item_count_list[2],
        for_parts_console_item_count=item_count_list[3],
        working_console_item_count=item_count_list[4],
        controller_item_count=item_count_list[5],
        wired_controller_item_count=item_count_list[6],
        wireless_controller_item_count=item_count_list[7],
        games_item_count=item_count_list[8],
        games_cib_item_count=item_count_list[9],
        games_incomplete_item_count=item_count_list[10],
        games_disk_only_item_count=item_count_list[11],
        games_cm_item_count=item_count_list[12],
        accessories_item_count=item_count_list[13],
        bundles_item_count=item_count_list[14],
        uncategorized_item_count=item_count_list[15])

@app.route('/table/<string:Category>')
def table(Category):
    try:
        item_list = returnMergedItemList(tree, Category)
        item_list.sort(key=lambda x: x.time_parsed)
        for item in item_list:
            item.category = item.category.replace('_', ' ')
        return render_template('table.html',
            items=item_list,
            page_title = TITLE_DICT[Category])
    except:
        return redirect(url_for('index'))

@app.route('/item/<int:Number>')
def item(Number):
    driver = createDriver()
    item_detail = getGoodWillItemDetails(driver, "/item/" + str(Number))
    driver.quit()
    return render_template('detail.html', item=item_detail)

#
# The following two-line "magic sequence" must be the last thing in
# your file.  After you write the main() function, this line it will
# cause the program to automatically run the final project.
#
if __name__ == '__main__':
    print('starting Flask app', app.name)
    app.run(debug=True)
