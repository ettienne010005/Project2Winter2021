#################################
##### Name:
##### Uniqname:
#################################

from bs4 import BeautifulSoup
import requests
import json
import secrets # file that contains your API key

CACHE_FILENAME = "cache.json"
CACHE_DICT = {}

class NationalSite:
    '''a national site

    Instance Attributes
    -------------------
    category: string
        the category of a national site (e.g. 'National Park', '')
        some sites have blank category.
    
    name: string
        the name of a national site (e.g. 'Isle Royale')

    address: string
        the city and state of a national site (e.g. 'Houghton, MI')

    zipcode: string
        the zip-code of a national site (e.g. '49931', '82190-0168')

    phone: string
        the phone of a national site (e.g. '(616) 319-7906', '307-344-7381')
    '''
    def __init__(self, category = "no category", name = "no name", address = "no address", zipcode = "no zipcode", phone = "no phone"):
        if category == "":
            self.category = "no category"
        else:
            self.category = category
        if name == "":
            self.name = "no name"
        else:
            self.name = name
        if address == "":
            self.address = "no address"
        else:
            self.address = address
        if zipcode == "":
            self.zipcode = "no zipcode"
        else:    
            self.zipcode = zipcode
        if phone == "":
            self.phone = "no phone"
        else:
            self.phone = phone

    def info(self):
        return f"{self.name} ({self.category}): {self.address} {self.zipcode}"


def build_state_url_dict():
    ''' Make a dictionary that maps state name to state page url from "https://www.nps.gov"

    Parameters
    ----------
    None

    Returns
    -------
    dict
        key is a state name and value is the url
        e.g. {'michigan':'https://www.nps.gov/state/mi/index.htm', ...}
    '''
    if 'https://www.nps.gov/index.htm' in CACHE_DICT:
        print("Using Cache")
        return CACHE_DICT['https://www.nps.gov/index.htm']

    else:
        print("Fetching")
        state_dict = {}
        html = requests.get('https://www.nps.gov/index.htm').text
        soup = BeautifulSoup(html, 'html.parser')
        search_div = soup.find(class_ ="SearchBar-keywordSearch input-group input-group-lg")
        state_list = search_div.find_all('a')
        for i in state_list:
            state_dict[i.text.lower()] = "https://www.nps.gov" + i['href']
        CACHE_DICT['https://www.nps.gov/index.htm'] = state_dict
        save_cache(CACHE_DICT)
        return state_dict

def get_site_instance(site_url):
    '''Make an instances from a national site URL.
    
    Parameters
    ----------
    site_url: string
        The URL for a national site page in nps.gov
    
    Returns
    -------
    instance
        a national site instance
    '''
    if site_url in CACHE_DICT:
        print("Using Cache")
        return NationalSite(CACHE_DICT[site_url][0],CACHE_DICT[site_url][1],CACHE_DICT[site_url][2],CACHE_DICT[site_url][3],CACHE_DICT[site_url][4])

    else:
        print("Fetching")
        html = requests.get(site_url).text
        soup = BeautifulSoup(html, 'html.parser')
        banner = soup.find(class_="Hero-titleContainer clearfix")
        footer = soup.find(class_="ParkFooter-contact")
        try:
            name = banner.find("a",class_ = "Hero-title").text
        except:
            name = "no name"
        try:
            category = banner.find("span", class_ = "Hero-designation").text
        except:
            category = "no category"
        try:
            address = footer.find("span", itemprop = "addressLocality").text + ', ' + footer.find("span", itemprop = "addressRegion").text
        except:
            address = "no address"
        try:
            zipcode = footer.find("span", itemprop = "postalCode").text.strip()
        except:
            zipcode = "no zipcode"
        try:
            phone = footer.find("span", itemprop = "telephone").text.strip()
        except:
            phone = "no phone"

        CACHE_DICT[site_url] = [category,name,address,zipcode,phone]
        save_cache(CACHE_DICT)

        return NationalSite(category,name,address,zipcode,phone)
    

def get_sites_for_state(state_url):
    '''Make a list of national site instances from a state URL.
    
    Parameters
    ----------
    state_url: string
        The URL for a state page in nps.gov
    
    Returns
    -------
    list
        a list of national site instances
    '''
    park_list = []
    html = requests.get(state_url).text
    soup = BeautifulSoup(html, 'html.parser')
    search_ul = soup.find('ul',id ="list_parks")
    url_list = search_ul.find_all('h3')
    for i in url_list:
        url = i.find('a')['href']
        park_list.append(get_site_instance("https://www.nps.gov" + url + "index.htm"))
    return park_list


def get_nearby_places(site_object):
    '''Obtain API data from MapQuest API.
    
    Parameters
    ----------
    site_object: object
        an instance of a national site
    
    Returns
    -------
    dict
        a converted API return from MapQuest API
    '''
    zipcode = site_object.zipcode
    if zipcode in CACHE_DICT:
        print("Using Cache")
    
    else:
        print("Fetching")
        BASE_URL = "http://www.mapquestapi.com/search/v2/radius"
        parameter = {"key": secrets.consumer_key, "origin": zipcode, "radius": 10, "maxMatches": 10, "ambiguities": "ignore", "outFormat": "json" }
        resp = requests.get(BASE_URL, parameter)
        resp_json = resp.json()
        CACHE_DICT[zipcode] = resp_json
        save_cache(CACHE_DICT)

    print("--------------------------------------")
    print(f"Places near {site_object.name}")
    print("--------------------------------------")
    for i in  CACHE_DICT[zipcode]["searchResults"]:
        if i['name'] == "":
            name = "no name"
        else:
            name = i['name'] 
        if i['fields']['group_sic_code_name'] == "":
            category = "no category"
        else:
            category = i['fields']['group_sic_code_name'] 
        if i['fields']["address"] == "":
            address = "no address"
        else:
            address = i['fields']["address"]
        if i['fields']["city"] == "":
            city = "no city"
        else:
            city = i['fields']["city"]   
        
        print(f"-{name} ({category}): {address}, {city}")
    return CACHE_DICT[zipcode]

def open_cache():
    ''' Opens the cache file if it exists and loads the JSON into
    the CACHE_DICT dictionary.
    if the cache file doesn't exist, creates a new cache dictionary
    
    Parameters
    ----------
    None
    
    Returns
    -------
    The opened cache: dict
    '''
    try:
        cache_file = open(CACHE_FILENAME, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict

def save_cache(cache_dict):
    ''' Saves the current state of the cache to disk
    
    Parameters
    ----------
    cache_dict: dict
        The dictionary to save
    
    Returns
    -------
    None
    '''
    dumped_json_cache = json.dumps(cache_dict)
    fw = open(CACHE_FILENAME,"w")
    fw.write(dumped_json_cache)
    fw.close()    

if __name__ == "__main__":    
    CACHE_DICT = open_cache()
    state_dict = build_state_url_dict()

    while(True):
        f = 0
        state = input("Enter a state name (e.g. Michigan, michigan) or \"exit\": ").lower()
        if state == "exit":
            break
        try: 
            state_url = state_dict[state] 
            park_list = get_sites_for_state(state_url)
            print("--------------------------------------")
            print(f"List of national sites in {state}")
            print("--------------------------------------")
            cnt = 1
            for i in park_list:
                print(f"[{cnt}]"+i.info())
                cnt += 1 
            while(True):
                print("--------------------------------------")
                num = input("Choose the number for detail search or \"exit\" or \"back\": ")
                if num == "exit":
                    f = 1
                    break
                elif num == "back":
                    f = 0
                    break
                elif num.isnumeric() and int(num) > 0 and int(num) <= len(park_list):
                    d = get_nearby_places(park_list[int(num)-1])
                else:
                    print("[Error] Invalid input")
                    print("--------------------------------------")
            if f == 1:
                break

        except:
            print("[Error] Enter proper state name ")
            print("--------------------------------------")
            
    



    