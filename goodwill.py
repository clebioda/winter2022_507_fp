from decimal import Decimal
from re import sub
import time
from numpy import imag
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import cssutils
import goodwill_driver_cache as DriverCache
import goodwill_cache as Cache
from bs4 import BeautifulSoup

def main():
    '''
    Main

    Parameters
    ----------
    None

    Returns
    -------
    None

    '''
    print("In Main!")
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

    # Test calls
    avg_price = getEbayItemAveragePrice()
    time_before_cached_item_start = time.time()
    items = getAllGoodWillItems(driver)
    Cache.save_cache(items, "items_dict_testing")
    time_before_cached_item_end = time.time()
    print("Time elapsed before cached items: ", time_before_cached_item_end - time_before_cached_item_start)
    time_after_cached_item_start = time.time()
    items = getAllGoodWillItems(driver)
    time_after_cached_item_end = time.time()
    print("Time elapsed after cached items: ", time_after_cached_item_end - time_after_cached_item_start)
    item = getGoodWillItemDetails(driver, items['142044908']["path"])
    driver.quit()

def getAllGoodWillItems(driver):
    page_number = 1
    goodwill_items_dict = {}
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
                path = item.find("a")["href"]
            except:
                # If the page does not load, we do not want to cache this item
                del CACHE_All_ITEMS[current_url]
                Cache.save_cache(CACHE_All_ITEMS, CACHE_FILENAME)
                break
            item_id = path.split('/')[-1]
            item_name = item.find("a", class_="feat-item_name ng-star-inserted").text.strip()
            item_price = item.find("p", class_="feat-item_price").text.strip()
            item_bottom = item.find("ul", class_="feat-item_bottom ng-star-inserted").find_all("li")
            # Some items are not up for auction and are only available as "Buy It Now"
            try:
                item_bids = item_bottom[0].text.strip()[-1:]
            except:
                item_bids = "Buy It Now Only"
            # Some really expensive items do not have time limits set
            try:
                item_time_left = item_bottom[1].text.strip()[16:]
            except:
                item_time_left = "Pure Buy Now No Time Limit"
            item_image = item.find("a").find("img", class_="feat-item_img")["src"]
            goodwill_items_dict[item_id] = {"name": item_name, "path": path, "price": item_price, "bids": item_bids, "time_left": item_time_left, "image": item_image}
        page_number += 1

    print(len(goodwill_items_dict))
    return goodwill_items_dict

def getGoodWillItemDetails(driver, path):
    full_path = GOODWILL_PATH + path
    driver_source = DriverCache.make_request_with_cache(driver, full_path, CACHE_ITEM_DETAILS, CACHE_FILENAME_DETAIL, cache_expiration=10, sleep_time=0.5)

    item_soup = BeautifulSoup(driver_source["source"], 'html.parser')

    item_id = path.split('/')[-1]

    # Item Title
    item_title = item_soup.find(id=item_id).text

    # Image urls
    images_urls = item_soup.find(class_='ngx-gallery-thumbnails').find_all('a')
    item_image_list_urls = []
    for image_url in images_urls:
        style_unparsed = image_url['style']
        style = cssutils.parseStyle(style_unparsed, validate=False)
        url = style['background-image']
        item_image_list_urls.append(url)

    item_time_left_and_bids = item_soup.find(class_="border-top border-bottom py-2 medium mb-4").find_all('span')

    # Item Time Left
    item_time_left = item_time_left_and_bids[1].text.strip()

    # Item Bids
    item_bids = item_time_left_and_bids[4].text.strip()

    # Item Current Price
    item_current_price = item_soup.find(class_='row mb-2').find(class_='col-4 text-right').find('h3').text.strip()

    # Item Handling Price
    item_handling_price = item_soup.find(class_='py-3 py-md-4 px-3 px-md-4 item-info-box br7 mb-3 mb-md-0').find_all('tr')[4].find('td').text.strip()

    item_detail = { "name": item_title, "price": item_current_price, "handling_price": item_handling_price ,"bids": item_bids, "time_left": item_time_left, "images": item_image_list_urls}
    return item_detail

def getEbayItemAveragePrice():
    ebay_url_test_1 = "https://www.ebay.com/sch/i.html?_from=R40&_nkw=silver+gamecube+controller+-lot+-bundle+-console&_sacat=1249&LH_TitleDesc=0&LH_Complete=1&LH_Sold=1&_ipg=120"
    ebay_url_test_2 = "https://www.ebay.com/sch/i.html?_from=R40&_trksid=p2334524.m570.l1313&_nkw=Nintendo+GameCube+Indigo+Console+IOB+w%2FWave+Bird+Controller&_sacat=0&LH_TitleDesc=0&rt=nc&_odkw=Luigi%27s+Mansion+Nintendo+GameCube+Game+w%2F+Manual&_osacat=0&LH_Complete=1"
    # TODO change this to use url supplied as parameter
    ebay_source = Cache.make_request_with_cache(ebay_url_test_1, CACHE_EBAY_ITEMS, CACHE_FILENAME_EBAY)
    soup = BeautifulSoup(ebay_source["source"], 'html.parser')
    grid = soup.find("ul", class_="srp-results srp-list clearfix")
    try:
        # Some searchs will not have any results
        no_exact_matches_found = grid.find("h3", class_="srp-save-null-search__heading").text
        return "No exact matches found"
    except:
        matched_items = grid.find_all("li", class_="s-item")
        price_list = []
        for item in matched_items:
            price_text = item.find("div", class_="s-item__detail s-item__detail--primary").text
            # If an eBay seller is selling multiple of an item, you can buy more than one
            if "to" in price_text:
                price_text = price_text.split()[0]
            price_decimal = Decimal(sub(r'[^\d.]', '', price_text))
            price_list.append(price_decimal)
        average_price = sum(price_list)/len(price_list)
        print(round(average_price, 2))
        return average_price

CACHE_FILENAME = "goodwill_cache.json"
CACHE_FILENAME_DETAIL = "goodwill_cache_detail.json"
CACHE_FILENAME_EBAY = "ebay_cache.json"
CACHE_All_ITEMS = Cache.open_cache(CACHE_FILENAME)
CACHE_ITEM_DETAILS = Cache.open_cache(CACHE_FILENAME_DETAIL)
CACHE_EBAY_ITEMS = Cache.open_cache(CACHE_FILENAME_EBAY)
DRIVER_PATH = 'chromedriver'
GOODWILL_PATH = 'https://shopgoodwill.com'

#
# The following two-line "magic sequence" must be the last thing in
# your file.  After you write the main() function, this line it will
# cause the program to automatically run the final project.
#
if __name__ == '__main__':
    main()