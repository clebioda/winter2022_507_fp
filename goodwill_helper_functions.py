from decimal import Decimal
from re import sub
import re
from bs4 import BeautifulSoup
import requests
import goodwill_cache as Cache
from goodwill_category import Category

CACHE_FILENAME_EBAY = "files/ebay_cache.json"
CACHE_EBAY_ITEMS = Cache.open_cache(CACHE_FILENAME_EBAY)

def parseTimeLeft(string:str):
    '''Parses the item's time left string into seconds
    Parameters
    ----------
    string: string
        item time left string
    Returns
    -------
    int
        time left in seconds
    '''

    string = string.split()
    time_in_seconds = 0
    for element in string:
        if element[-1] == 's':
            time_in_seconds += int(element[:-1])
        elif element[-1] == 'm':
            time_in_seconds += int(element[:-1]) * 60
        elif element[-1] == 'h':
            time_in_seconds += int(element[:-1]) * 3600
        elif element[-1] == 'd':
            time_in_seconds += int(element[:-1]) * 86400
    return time_in_seconds

def parseKeyWords(string:str):
    '''Parses the item's title to find which category fits it best
    Parameters
    ----------
    string: string
        item title string
    Returns
    -------
    string
        best category for the item
    '''

    # the following lists are common words and phrases used in listings
    # Because listings can be written by anyone, there is a lot of leeway in the title so there will be mistakes
    bundle_words = ["with", "w/", "more", "&", "assorted", "bundle", "games", "controllers", "lotof", "lot"]
    wireless_controller_words = ["wavebird", "wave bird", "wireless", "w/ reciever"]
    wired_controller_words = ["wired", "dol003", "wireless", "w/ reciever"]
    complete_in_box_words = ["completeinbox", "complete", "cib", "sealed", "new", "w/case"]
    disc_only_words = ["loose", "disconly", "diskonly", "disc", "disk", "gameonly"]
    case_manual_only_words = ["no game", "case only", "manualonly", "manuelonly"]
    accessories_words = ["adaptor", "adapter", "ac adaptor", "cable", "memory", "card", "gameboy", "dkbongos", "ereader", "guide"]
    parts_fix_words = ["parts", "fix", "parts/fix", "fix/parts"]

    # Removing some common words due to the listings missing words like "the" and "of" and all of them have "gamecube"
    string_lower_no_spaces = re.sub(r'[^A-Za-z0-9/&]+', '', string.lower()).replace("gamecube", "").replace('the', '').replace('of', '')
    # Accessories
    for word in accessories_words:
        if word in string_lower_no_spaces and "console" not in string_lower_no_spaces:
            return "Accessories"
    # Static list of games that will never change
    try:
        file = open("files/gamecubeGames.txt", "r")
        file_lines = file.read()
        games = file_lines.split("\n")
    except:
        games = getAllGameCubeTitles()
        with open("files/gamecubeGames.txt", "w") as file:
            file_lines = "\n".join(games)
            file.write(file_lines)
    # Check to see if the item is a game
    for game in games:
        if game.lower() in string_lower_no_spaces and "controller" not in string_lower_no_spaces and "console" not in string_lower_no_spaces:
            # Want to omit multiple games
            for word in complete_in_box_words:
                if word in string_lower_no_spaces:
                    return Category.complete_in_box.value
            for word in disc_only_words:
                if word in string_lower_no_spaces:
                    return Category.disk_only.value
            for word in case_manual_only_words:
                if word in string_lower_no_spaces:
                    return Category.case_manuel_only.value
            # Listings can still have multiple game titles in it
            for word in bundle_words:
                if word in string_lower_no_spaces:
                    return Category.bundles.value
            # These are usually games that are missing the manual, but have the case
            return Category.game_incomplete.value
    if "controller" in string_lower_no_spaces:
        for word in wireless_controller_words:
            if word in string_lower_no_spaces:
                return Category.wireless.value
        for word in wired_controller_words:
            if word in string_lower_no_spaces:
                return Category.wired.value
        # Bundle listings with the word controller
        for word in bundle_words:
            if word in string_lower_no_spaces or "console" in string_lower_no_spaces:
                return Category.bundles.value
        # Example: Nintendo GameCube Controller
        return Category.wired.value
    if "console" in string_lower_no_spaces:
        for word in bundle_words:
            if word in string_lower_no_spaces:
                return Category.bundles.value
        for word in parts_fix_words:
            if word in string_lower_no_spaces:
                return Category.for_parts.value
        return Category.working.value
    for word in bundle_words:
        if word in string_lower_no_spaces:
            return Category.bundles.value
    return Category.uncategorized.value

def getAllGameCubeTitles():
    '''Gets all the GameCube titles from Wikipedia (should never change)
    Parameters
    ----------
    None
    Returns
    -------
    list<strings>
        list of gamecube strings stripped
    '''

    url = "https://en.wikipedia.org/wiki/List_of_GameCube_games"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    table_body = soup.find_all("table", id="softwarelist")
    # Wikipedia styles all their titles with italics
    italic_items = table_body[0].find_all("i")
    # Common misspelled title headings that I know are games
    gamecube_titles = ["PhantasyStarOnlineEpisode12", "TheLegendofZelda", "Zelda", "Pokemon", "HarryPotter", "Mario", "TonyHawk", "StarWars", "BatenKaitos"]
    for item in italic_items:
        try:
            title = item.find("a").text
            # Keep only alphanumerics and spaces because each goodwill item is missing those characters
            # This will make all Pokémon games lose the é
            # Removing "the" and "of" because the people writing the auctions often skip them
            title_stripped = re.sub(r'[^A-Za-z0-9]+', '', title).replace('the', '').replace('of', '')
            gamecube_titles.append(title_stripped)
        except:
            continue
    return gamecube_titles

def getEbayItemAveragePrice(item_title:str):
    '''Uses the item title to look up recently sold and completed items on eBay
    Parameters
    ----------
    item_title: string
        the string used as a query parameter to look up the item
    Returns
    -------
    string
        returns average price of there are recent sales
        returns string if there are no recent sales
    '''

    item_parameters = item_title.replace(" ", '+')
    ebay_url = f'https://www.ebay.com/sch/i.html?_from=R40&_nkw={item_parameters}&LH_TitleDesc=0&_sop=13&LH_Complete=1&LH_Sold=1&_oac=1'
    ebay_source = Cache.make_request_with_cache(ebay_url, CACHE_EBAY_ITEMS, CACHE_FILENAME_EBAY)
    soup = BeautifulSoup(ebay_source["source"], 'html.parser')
    grid = soup.find("ul", class_="srp-results srp-list clearfix")
    try:
        # Some searchs will not have any results
        no_exact_matches_found = grid.find("h3", class_="srp-save-null-search__heading").text
        return "No exact matches found"
    except:
        matched_items = grid.find_all("li", attrs={'style': False, 'class': 's-item'})
        price_list = []
        for item in matched_items:
            price_text = item.find("div", attrs={'style': '', 'class': 's-item__detail s-item__detail--primary'}).text
            # If an eBay seller is selling multiple of an item, you can buy more than one
            if "to" in price_text:
                price_text = price_text.split()[0]
            price_decimal = Decimal(sub(r'[^\d.]', '', price_text))
            price_list.append(price_decimal)
        average_price = sum(price_list)/len(price_list)
        return "$" + str(round(average_price, 2))
