#################################
##### Name:
##### Uniqname:
#################################

from bs4 import BeautifulSoup
import requests
import json
import secrets # file that contains your API key


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
    def __init__(self, category = None, name = None, address = None, zipcode = None, phone = None):
        self.category = category
        self.name = name
        self.address = address
        self.zipcode = zipcode
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
    state_dict = {}
    html = requests.get('https://www.nps.gov/index.htm').text
    soup = BeautifulSoup(html, 'html.parser')
    search_div = soup.find(class_ ="SearchBar-keywordSearch input-group input-group-lg")
    state_list = search_div.find_all('a')
    for i in state_list:
        state_dict[i.text.lower()] = "https://www.nps.gov" + i['href']
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
    html = requests.get(site_url).text
    soup = BeautifulSoup(html, 'html.parser')
    banner = soup.find(class_="Hero-titleContainer clearfix")
    footer = soup.find(class_="ParkFooter-contact")

    name = banner.find("a").text
    category = banner.find("span", class_ = "Hero-designation").text
    address = footer.find("span", itemprop = "addressLocality").text + ', ' + footer.find("span", itemprop = "addressRegion").text
    zipcode = footer.find("span", itemprop = "postalCode").text.strip()
    phone = footer.find("span", itemprop = "telephone").text.strip()

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
    pass


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
    pass
    

if __name__ == "__main__":
    html = requests.get('https://www.nps.gov/deto/index.htm').text
    soup = BeautifulSoup(html, 'html.parser')
    banner = soup.find(class_="Hero-titleContainer clearfix")
    print(banner.find("a").text)
    print(banner.find("span", class_ = "Hero-designation").text)

    footer = soup.find(class_="ParkFooter-contact")
    print(footer.find("span", itemprop = "addressLocality").text + ' ,' + footer.find("span", itemprop = "addressRegion").text)
    print(footer.find("span", itemprop = "postalCode").text)
    print(footer.find("span", itemprop = "telephone").text.strip())
