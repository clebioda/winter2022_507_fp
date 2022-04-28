import time
import goodwill_cache as Cache

def make_request_with_cache(driver, url, cache, cache_file_name, page_number=None, cache_expiration=120, sleep_time=4):
    '''Check the cache for a saved result for this url
    combo and the cache has yet to expire. If the result
    is found, return it. Otherwise send a new request,
    save it, then return it.
    ----------
    Parameters
    driver: WebDriver
        Browser that Selenium will run in
    url: string
        The URL for the website
    cache: dictionary
        A dictionary of url: time, response.text pairs
    cache_file_name: string
        The cache file name we are saving to
    cache_expiration: int
        An int that represents how many hours an item should persist in the cache
        defaults to two hours
    page_number: int
        An int that tells us if we are looking at the first page because we don't
        want to cache this
    sleep_time: int
        Allows browser to load Javascript on page before scrapping
    Returns
    -------
    string
        the results of the query as a driver object
    '''
    if url in cache.keys() and (((time.time() - cache[url]["time_written"])/60) < cache_expiration):
        print("cache hit!", url)
        return cache[url]
    else:
        print("cache miss!", url)
        driver.get(url)
        time.sleep(sleep_time)

        # Don't want to cache the first page because these items will update the most often since their auctions are ending the soonest
        if (page_number == 1):
            return driver.page_source
        cache[url] = { "time_written": time.time(), "source": driver.page_source }
        Cache.save_cache(cache, cache_file_name)
        return cache[url]