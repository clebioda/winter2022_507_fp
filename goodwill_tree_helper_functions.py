from goodwill_class import GoodwillItem

'''
testTree = \
    ("All_Items",
        (("Individual_Items",
            ("Consoles",
                ("For_Parts", [1]),
                ("Working", [1, 2])),
            ("Controllers",
                ("Wired", [1, 2, 3]),
                ("Wireless", [1, 2, 3, 4])),
            ("Games",
                ("CIB", [1, 2, 3, 4, 5]),
                ("Game_Incomplete", [1, 2, 3, 4, 5, 6]),
                ("Disk Only", [1, 2, 3, 4, 5, 6, 7]),
                ("Case_Only_Case_Manual_Only", [1, 2, 3, 4, 5, 6, 7, 8])),
            ("Accessories", [1, 2, 3, 4, 5, 6, 7, 8, 9])),
        ("Bundles", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]),
        ("Uncategorized", [1, 2, 3, 4, 5, 6, 7, 8, 9, 10 ,11])))
'''

def isLeaf(tree):
    '''Checks if the tree has a list at the end
    ----------
    Parameters
    tree: tuples
        global tree structure of all the Goodwill items
    Returns
    -------
    Bool
        True if it's a leaf, false otherwise
    '''

    last_element = tree[-1]
    if type(last_element) == list:
        return True
    return False

def insertItem(tree, item:GoodwillItem):
    '''Recursively goes through the tree and inserts the item
    Parameters
    ----------
    tree: tuples
        global tree structure of all the Goodwill items
    item: GoodWillItem
        item to be inserted
    Returns
    -------
    None
    '''

    if isLeaf(tree):
        if item.category == tree[0]:
            tree[-1].append(item)
            return True
        else:
            return False
    else:
        for i in range(len(tree)):
            if type(tree[i]) == tuple:
                wasInserted = insertItem(tree[i], item)
                if wasInserted == True:
                    break

def returnMergedItemList(tree, category:str, items:list=None, inCorrectTree=False):
    '''Goes through the entire tree structure to count the number of items in the
        given string category and returns the items. Always go throughs the whole tree.
    ----------
    Parameters
    tree: tuples
        global tree structure of all the Goodwill items
    category: string
        the category of items we want
    items: list
        list of Goodwill items to be returned
    inCorrectTree: bool
        True if we are in the right category for the tree, False otherwise
    Returns
    -------
    List
        returns all items in the given category string
    '''

    # Because lists are a mutuable object and this is only evulated once, need to set the list to None by default
    if items == None:
        items = []
    if isLeaf(tree) and inCorrectTree:
        items.extend(tree[-1])
    if tree[0] == category and inCorrectTree == False:
        returnMergedItemList(tree, category, items, True)
    else:
        for i in range(len(tree)):
            if type(tree[i]) == tuple:
                returnMergedItemList(tree[i], category, items, inCorrectTree)
    return items


