import json
import requests
import time

def open_cache(cache_file_name):
    ''' opens the cache file if it exists and loads the JSON into
    the CACHE_DICT dictionary.
    if the cache file doesn't exist, creates a new cache dictionary
    Parameters
    ----------
    cache_file_name: string
        The filename to open where the cache located
    Returns
    -------
    The opened cache or an empty dictionary
    '''
    try:
        cache_file = open(cache_file_name, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict

def save_cache(cache_dict, cache_file_name):
    ''' saves the current state of the cache to disk
    Parameters
    ----------
    cache_dict: dict
        The dictionary to save
    cache_file_name: string
        The filename to save the cache to
    Returns
    -------
    None
    '''
    dumped_json_cache = json.dumps(cache_dict)
    fw = open(cache_file_name, "w")
    fw.write(dumped_json_cache)
    fw.close()

def make_request(url):
    '''Make a request to the url
    Parameters
    ----------
    url: string
        The URL we want to access
    Returns
    -------
    string
        the text results of the query
    '''
    response = requests.get(url)
    return response.text

def make_request_with_cache(url, cache, cache_file_name, cache_expiration=10080):
    '''Check the cache for a saved result for this url
    combo and the cache has yet to expire. If the result
    is found, return it. Otherwise send a new request,
    save it, then return it.
    Parameters
    ----------
    url: string
        The URL we want to access
    cache: dictionary
        A dictionary of url: time, response.text pairs
    cache_file_name: string
        The cache file name we are saving to
    cache_expiration: int
        An int that represents how many hours an item should persist in the cache
        defaults to one week
    Returns
    -------
    string
        the results of the query as a Python object loaded from JSON
    '''
    if url in cache.keys() and (((time.time() - cache[url]["time_written"])/60) < cache_expiration):
        print("cache hit!", url)
        return cache[url]
    else:
        print("cache miss!", url)
        cache[url] = { "time_written": time.time(), "source": make_request(url) }
        save_cache(cache, cache_file_name)
        return cache[url]