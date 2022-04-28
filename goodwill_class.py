import goodwill_helper_functions as GoodwillHelper

class GoodwillItem:
    '''any Goodwill item (GameCube)

    Instance Attributes
    -------------------
    title: string
        the title of the item
    path: string
        the url path needed for the detail page
    price: string
        the price of the item
    bids: string
        the number of bids on the item
    time_left: string
        the time left on the item in human readable form
    time_parsed: int
        the time left on the item in seconds for sorting
    image: url string
        the image of the item
    category: string
        the category of the item used to place in tree
    '''
    def __init__(self, item_title=None, item_path=None, item_price=0, ebay_avg_price=0, item_bids=0, item_time_left=0, item_image=None):
        self.title = item_title
        self.path = item_path
        self.price = item_price
        self.bids = item_bids
        self.time_left = item_time_left
        self.time_parsed = GoodwillHelper.parseTimeLeft(item_time_left)
        self.image = item_image
        self.category = GoodwillHelper.parseKeyWords(item_title)