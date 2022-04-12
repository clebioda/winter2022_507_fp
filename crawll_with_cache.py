from bs4 import BeautifulSoup
import requests
import time
import json
BASE_URL = 'https://www.si.umich.edu'
COURSES_PATH = '/programs/courses'
CACHE_FILE_NAME = 'cacheSI_Scrape.json'
CACHE_DICT = {}
headers = {'User-Agent': 'UMSI 507 Course Project - Python Web Scraping','From': 
'youremail@domain.com','Course-Info': 
'https://www.si.umich.edu/programs/courses/507'}
##### Make Soup for courses page
def load_cache():
    try:
        cache_file = open(CACHE_FILE_NAME, 'r')
        cache_file_contents = cache_file.read()
        cache = json.loads(cache_file_contents)
        cache_file.close()
    except:
        cache = {}
    return cache
def save_cache(cache):
    cache_file = open(CACHE_FILE_NAME, 'w')
    contents_to_write = json.dumps(cache)
    cache_file.write(contents_to_write)
    cache_file.close()
def make_url_request_using_cache(url, cache):
    if (url in cache.keys()): # the url is our unique key
        print("Using cache")
        return cache[url]
    else:
        print("Fetching")
        time.sleep(1)
        response = requests.get(url, headers=headers)
        cache[url] = response.text
        save_cache(cache)
        return cache[url]
# Load the cache, save in global variable
CACHE_DICT = load_cache()
courses_page_url = BASE_URL + COURSES_PATH
url_text = make_url_request_using_cache(courses_page_url, CACHE_DICT)
response = requests.get(courses_page_url)
soup = BeautifulSoup(response.text, 'html.parser')
'''
file1 = open("SoupPretty.txt", "a")
file1.write(soup.prettify())
file1.close()
'''
course_listing_parent = soup.find('div', class_='item-teaser-group')
#print(course_listing_parent)
course_listing_divs = course_listing_parent.find_all('div', recursive=False)
#print(len(course_listing_divs))
#print(course_listing_divs[0])
'''
<div>
<a href="/programs/courses/106"><h2><span> 106 - Programs, Information and People 
</span>
</h2></a>
<div class="body wysiwyg-content"><p>Introduction to programming with a focus on 
applications in informatics.  Covers the fundamental elements of a modern 
programming language and how to access data on the internet.  Explores how humans 
and technology complement one another, including techniques used to coordinate 
groups of people working together on software development.</p>
</div>
</div>
'''
for course_listing_div in course_listing_divs:
    ###extract course details url
    course_link_tag = course_listing_div.find('a')
    course_details_path = course_link_tag['href']
    course_details_url = BASE_URL + course_details_path
    ####CRAWL TO THE COURSE DETAIL PAGE AND EXTRACT:
    responseDetail = make_url_request_using_cache(course_details_url, CACHE_DICT)
    soupDetail = BeautifulSoup(responseDetail.text, 'html.parser')
    number_name = soupDetail.find('div', class_='column grid--3col-2').find('h1')
    #number_name2 = number_name.find('h1')
    print(number_name.text.strip())
    print("")
    #print("")
    course_desc = soupDetail.find('div', class_='column grid--3col-2').find_all('p')
    for x in course_desc:
        print(x.text.strip())
    #print(course_desc.text.strip())
    print("")
    credits = soupDetail.find('div', class_='credit-hours').find('span')
    print('Credits: ', credits.text.strip())
    prereqs_div = soupDetail.find('div', class_='prerequisites-enforced')
    if (prereqs_div is not None):
        prereqs = prereqs_div.find_all('li')
        for z in prereqs:
            print('Enforced Prereq:', z.text.strip())
    
    print('-' * 50) # seperator 
    #### NAME & NUMBER 
    #### YOU CAN DO DESCRIPTION, CREDIT HOURS & PREREQS TOO
#print(soupDetail.prettify())
'''
      <div class="column grid--3col-2">
       <div class="hidden" data-drupal-messages-fallback="">
       </div>
       <h1>
        <span>
         334 - Persuasion and Social Influence
        </span>
       </h1>
'''