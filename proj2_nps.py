#################################
##### Name: Buyao Lyu
##### Uniqname: wqrydqk@umich.edu
#################################

from bs4 import BeautifulSoup
import requests
import json
import secrets  # file that contains your API key
import datetime


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
    def __init__(self, category='', name='', address='', zipcode='', phone=''):
        self.category = category
        self.name = name
        self.address = address
        self.zipcode = zipcode
        self.phone = phone

    def info(self):
        return f'{self.name} ({self.category}): {self.address} {self.zipcode}'


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
    filename = 'states.json'
    cache_dict = open_cache(filename)
    if cache_dict:
        print('Using cache-1')
        return cache_dict
    else:
        print('Fetching-1')
        url_to_scrape = 'https://www.nps.gov/index.htm'
        base_url = 'https://www.nps.gov'
        response = requests.get(url_to_scrape)
        soup = BeautifulSoup(response.text, 'html.parser')
        result_1 = soup.find('div', class_='SearchBar-keywordSearch input-group input-group-lg').find('ul').find_all('li')
        dict_name_url_state = {}
        for element in result_1:
            state_name = element.text.lower()
            state_url = base_url + element.find('a')['href']
            dict_name_url_state[state_name] = state_url
        save_cache(dict_name_url_state, filename)
        return dict_name_url_state


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
    filename = 'sites_url.json'
    cache_dict = open_cache(filename)
    if site_url in cache_dict:
        print('Using cache!-2')
        site_instance = NationalSite(category=cache_dict[site_url]['category'],
                                     name=cache_dict[site_url]['name'],
                                     address=cache_dict[site_url]['address'],
                                     zipcode=cache_dict[site_url]['zipcode'],
                                     phone=cache_dict[site_url]['phone'])
        return site_instance
    else:
        print('Fetching!-2')
        response = requests.get(site_url)
        text_to_parse = response.text
        site_url_dict = {}
        soup = BeautifulSoup(text_to_parse, 'html.parser')
        result_1 = soup.find('div', class_='Hero-titleContainer clearfix')
        if result_1 is not None:
            site_name = result_1.find('a').text.strip()
            site_type = result_1.find('div').find('span', class_="Hero-designation").text.strip()
        else:
            site_name = 'Site working on!'
            site_type = 'Site working on!'
        result_2 = soup.find('div', class_="vcard")
        if result_2 is not None:
            try:
                site_add_1 = result_2.find('div', itemprop="address").find('span', itemprop="addressLocality").text.strip()
                site_add_2 = result_2.find('div', itemprop="address").find('span', itemprop="addressRegion").text.strip()
                site_add = f"{site_add_1}, {site_add_2}"
            except:
                site_add = 'Not provided!'
            try:
                site_zipcode = result_2.find('div', itemprop="address").find('span', itemprop="postalCode").text.strip()
            except:
                site_zipcode = 'Not provided!'

            site_phone_1 = result_2.find('p', recursive=False).find('span', itemprop="telephone").text.strip()
            site_phone_2_res = result_2.find('p', recursive=False).find('span', itemprop="telephoneExtension")
            if site_phone_2_res:
                site_phone_2 = site_phone_2_res.text.strip()
                site_phone = site_phone_1 + " " + site_phone_2
            else:
                site_phone = site_phone_1
        else:
            site_add = 'Site working on!'
            site_zipcode = 'Site working on!'
            site_phone = 'Site working on!'
        site_instance = NationalSite(category=site_type, name=site_name, address=site_add, zipcode=site_zipcode, phone=site_phone)
        site_url_dict['category'] = site_type
        site_url_dict['name'] = site_name
        site_url_dict['address'] = site_add
        site_url_dict['zipcode'] = site_zipcode
        site_url_dict['phone'] = site_phone
        cache_dict[site_url] = site_url_dict
        save_cache(cache_dict, filename)
        return site_instance


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

    national_sites = []
    filename = 'states_url.json'
    cache_dict = open_cache(filename)
    if state_url in cache_dict:
        print('Using cache!-3')
        href_list = cache_dict[state_url]
    else:
        print('Fetching!-3')
        response = requests.get(state_url)
        text_to_parse = response.text
        cache_dict[state_url] = text_to_parse
        save_cache(cache_dict, filename)
        soup = BeautifulSoup(text_to_parse, 'html.parser')
        result_1 = soup.find(id='list_parks').find_all('li', recursive=False)
        href_list = []
        for element in result_1:
            href_tag = element.find('h3').find('a')
            href_part = href_tag['href']
            href = 'https://www.nps.gov' + href_part + 'index.htm'
            href_list.append(href)
        cache_dict[state_url] = href_list
        save_cache(cache_dict, filename)

    for each_href in href_list:
        national_site = get_site_instance(each_href)
        national_sites.append(national_site)
    return national_sites


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

    filename = 'near_by.json'
    cache_dict = open_cache(filename)
    if site_object.zipcode in cache_dict:
        print('Using cache-4!')
        return cache_dict[site_object.zipcode]
    else:
        print('Fetching-4!')
        base_url = 'https://www.mapquestapi.com/search/v2/radius'
        params = {'key': secrets.API_KEY,
                  'origin': site_object.zipcode,
                  'radius': 10,
                  'maxMatches': 10,
                  'ambiguities': 'ignore',
                  'outFormat': 'json'}
        rep = requests.get(base_url, params)
        dict_to_save = rep.json()
        cache_dict[site_object.zipcode] = dict_to_save
        save_cache(cache_dict, filename)
        return dict_to_save
    

def open_cache(cache_filename):
    ''' opens the cache file if it exists and loads the JSON into
        a dictionary, which it then returns.
        if the cache file doesn't exist, creates a new cache dictionary

    Parameters
    ----------
    cache_filename: str
        the name of the json file to open

    Returns
    -------
    The opened cache
    '''

    try:
        cache_file = open(cache_filename, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict


def save_cache(cache_dict, cache_filename):
    ''' saves the current state of the cache to disk
    Parameters
    ----------
    cache_dict: dict
        The dictionary to save
    cache_filename: str
        The name of the cache file

    Returns
    -------
    None
    '''

    dumped_json_cache = json.dumps(cache_dict)
    fw = open(cache_filename,"w")
    fw.write(dumped_json_cache)
    fw.close()


def func_for_part3(state_name, state_dict):
    url_to_use = state_dict[state_name]
    my_sites_list = get_sites_for_state(url_to_use)
    num_of_sites = len(my_sites_list)
    print('-'*40)
    print(f'List of national sites in {state_name.title()}')
    print('-'*40)
    for i in range(num_of_sites):
        print(('[' + str(i+1) + ']').ljust(5), end='')
        print(my_sites_list[i].info())
    return my_sites_list


def func_for_part4(site_object):
    result_dict = get_nearby_places(site_object)
    print('-'*40)
    print(f"Places near {site_object.name}")
    print('-'*40)
    if result_dict['resultsCount'] != 0:
        result_list = result_dict['searchResults']
        total_dict = {}
        for num in range(len(result_list)):
            information_dict = {}
            information_dict['name'] = result_list[num]['name']
            information_dict['category'] = result_list[num]['fields']['group_sic_code_name_ext']
            # information_dict['category'] = 'ppp'
            information_dict['street_address'] = result_list[num]['fields']['address']
            information_dict['city_name'] = result_list[num]['fields']['city']
            total_dict[num] = information_dict

        modified_total_dict = {}
        for key1 in total_dict:
            place = total_dict[key1]
            modified_dict = {}
            for key2 in place:
                if key2 == 'name':
                    if place[key2] == '':
                        modified_dict[key2] = 'no name'
                    else:
                        modified_dict[key2] = place[key2]

                if key2 == 'category':
                    if place[key2] == '':
                        modified_dict[key2] = 'no category'
                    else:
                        modified_dict[key2] = place[key2]

                if key2 == 'street_address':
                    if place[key2] == '':
                        modified_dict[key2] = 'no address'
                    else:
                        modified_dict[key2] = place[key2]

                if key2 == 'city_name':
                    if place[key2] == '':
                        modified_dict[key2] = 'no city'
                    else:
                        modified_dict[key2] = place[key2]
            modified_total_dict[key1] = modified_dict

        for key in modified_total_dict:
            temp_value = modified_total_dict[key]
            string_to_print = f"- {temp_value['name']} ({temp_value['category']}): {temp_value['street_address']}, {temp_value['city_name']}"
            print(string_to_print)

    else:
        print('No information collected!!!!!!')



if __name__ == "__main__":
    # part 3 starts here##
    # state_dict = build_state_url_dict()
    # while True:
    #     prompt = 'Enter a state name (e.g. Michigan, michigan) or "exit":'
    #     input_str = input(prompt)
    #     if input_str == "exit":
    #         break
    #     else:
    #         if input_str.strip().lower() in state_dict:
    #             func_for_part3(input_str.strip().lower(), state_dict)
    #         else:
    #             print('this is not a name of a state, try again!')

    # test
    # state_dict = build_state_url_dict()
    # i = 1
    # for state in state_dict:
    #     print('********************************')
    #     print(f'state: {state}')
    #     print('*******************************')
    #     func_for_part3(state, state_dict)
    #     print(i)
    #     i = i + 1

    ## part 4 starts here
    # test_url = 'https://www.nps.gov/slbe/index.htm'
    # new_site_obj = get_site_instance(test_url)
    # func_for_part4(new_site_obj)

    # test ##
    # not_valid = ['Site working on!', 'Not provided!']
    # site_urls_dict = open_cache('states_url.json')
    # for key in site_urls_dict:
    #     sites_url_list = site_urls_dict[key]
    #     for element in sites_url_list:
    #         print('******************************************')
    #         temp_site_obj = get_site_instance(element)
    #         func_for_part4(temp_site_obj)
    #         print('+++++++++++++++++++++++++++++++++++++++++++++++++++++')

    # part 5 starts here #
    # Create an interactive search interface
    my_state_dict = build_state_url_dict()
    sites_list = []
    while True:
        if len(sites_list) == 0:
            input_str = input('Enter a state name (e.g. Michigan, michigan) or "exit":')
            if input_str.lower() == "exit":
                break
            else:
                if input_str.strip().lower() in my_state_dict:
                    sites_list = func_for_part3(input_str.strip().lower(), my_state_dict)
                else:
                    print('[Error] Enter a proper state name!')
        if len(sites_list) != 0:
            input_str = input('Choose a number for detail search or "exit" or "back":')
            if input_str.isnumeric():
                if 0 < int(input_str) <= len(sites_list):
                    site_instance_picked = sites_list[int(input_str) - 1]
                    func_for_part4(site_instance_picked)
                else:
                    print('[Error] Invalid input!!')
            elif input_str.lower() == "exit":
                break
            elif input_str.lower() == "back":
                sites_list = []
            else:
                print('you should input a valid number, "exit" or "back" here!')

    # test
    # t1 = datetime.datetime.now().timestamp()
    # test_dict = build_state_url_dict()
    # for state in test_dict:
    #     sites = func_for_part3(state, test_dict)
    #     for site in sites:
    #         func_for_part4(site)
    #
    # t2 = datetime.datetime.now().timestamp()
    # print("time without caching: ", (t2 - t1) * 1000, "ms")

