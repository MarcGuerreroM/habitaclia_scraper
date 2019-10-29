'''
Builds a dataset from habitaclia website
'''
# coding=utf-8
import requests
from bs4 import BeautifulSoup
import pandas as pd

cat_provinces = ["barcelona", "lleida", "tarragona", "girona"]
def get_website(url):
    '''
    Gets the website
    :param url: website's url to get
    :return: if success: request object containing the web result otherwise: -1
    '''
    main_page = requests.get(url)
    if main_page.status_code == 200:
        return main_page
    else:
        return -1
def get_sub_websites_link(main_page):
    '''
    Returns the link of every house in the page
    :param main_page: main page to extract the links
    :return: a list with the links
    '''
    pass
def get_info(page):
    '''
    Gets the imporant info from the page
    :param page: page to extract the info
    :return: the info in a list of a dictionaries
    '''
    info = []
    divs = page.findAll("div", {"class": "list-item-info"})
    for child in divs:
        success = 1
        dic = dict()
        dic['title'] = child.a['title']
        dic['link'] = child.a.get('href')
        dic['town'] = child.find("p", {"class": "list-item-location"}).span.string
        l = child.find("p", {"class": "list-item-feature"}).get_text().split("-")
        try:
            dic['surface'] = int(l[0].split('m2')[0])
            dic['rooms'] = int(l[1].split('habitaciones')[0])
            dic['n_bathrooms'] = int(l[2].encode('UTF-8').split('baño')[0])
            precio_metro_aux = l[3].encode('UTF-8').split("€")[0].split('.')
            dic['price_meter'] = int(str(precio_metro_aux[0]) + str(precio_metro_aux[1]))

            precio_total_aux = child.find("span", {"itemprop": "price"}).string.split(".")
            dic['total_price'] = int(str(precio_total_aux[0]) + str(precio_total_aux[1].split(" ")[0]))
        except:
            #it means that it does not have all features -> it is discarted
            success = 0
        if success:
            info.append(dic)
    return info
def check_page_exists(url):
    '''
    Checks if the page exists
    :param url: page to check
    :return: True if exists, otherwise False
    '''
    main_page = requests.get(url)
    if main_page.status_code == 200:
        soup = BeautifulSoup(main_page.content, features="html.parser")
        # print(soup.prettify())
        no_result = soup.find("div", {"class": "list-no-result-title"})
        if no_result == None:
            return True
        else:
            return False
    else:
        return False
def get_available_pages(url):
    '''
    Gets all available web pages from an url in habitaclia
    :param url: main url
    :return: list with other url including the main url
    '''
    first_url = url
    pages = []
    stop = False
    counter = 1
    while(not stop):
        if (check_page_exists(url)):
            pages.append(url)
            url = first_url.split(".htm")
            new_url = url[0] +str("-") + str(counter) + ".htm"
            url = new_url
            counter += 1
        else:
            stop = True
    return pages
def get_provinces_url(hab_url, provinces):
    '''
    Gets all provinces url from hab_url
    :param hab_url: url
    :param provinces: province
    :return: list with tupples containing the url and the province
    '''
    provinces_url = []
    for province in provinces:
        string_to_add = "/comprar-vivienda-en-" + str(province) +"/buscador.htm"
        provinces_url.append([province, hab_url + string_to_add])
    return provinces_url

def get_regions_urls(url):
    '''
    Gets all regions url from provinces region
    :param url: url from the province
    :return: list with tupples containing the url and the region
    '''
    page = requests.get(url)
    final_urls = []
    if page.status_code == 200:
        soup = BeautifulSoup(page.content, features="html.parser")
        #print(soup.prettify())
        divs = soup.find("ul", {"class": "verticalul"}).find_all("li")
        for div in divs:
            url_to_append = div.a.get('href').split('/')
            region = url_to_append[3].split("-")[-1]
            region_link = "viviendas-en-" + region
            url_to_append = url_to_append[0] + '//' + url_to_append[2] + "/" + region_link + ".htm"
            final_urls.append([region, url_to_append])
        return final_urls

if __name__ == "__main__":
    url = "https://www.habitaclia.com"
    first = True

    provinces_urls = get_provinces_url(url, cat_provinces)
    for province_url in provinces_urls:
        regions = get_regions_urls(province_url[1])
        for region in regions:
            available_pages = get_available_pages(region[1])
            info = []
            df = pd.DataFrame(columns=['TITLE','TOWN', 'PROVINCE', 'REGION','SURFACE', 'N_ROOMS', 'N_BATHROOMS', 'PRICE_METER', 'TOTAL_PRICE', 'LINK'])
            for page in available_pages:
                main_page = get_website(page)
                encoding = main_page.encoding if 'charset' in main_page.headers.get('content-type', '').lower() else None
                soup = BeautifulSoup(main_page.content, from_encoding=encoding, features="html.parser")
                partial_info = get_info(soup)
                for p_info in partial_info:
                    info.append(p_info)
            for item in info:
                df = df.append({'TITLE': item['title'].encode('utf-8'),'TOWN': item['town'].encode('utf-8'),'PROVINCE': province_url[0], 'REGION': region[0], 'SURFACE': item['surface'],
                                'N_ROOMS':item['rooms'],'N_BATHROOMS': item['n_bathrooms'],'PRICE_METER': item['price_meter'],'TOTAL_PRICE': item['total_price'],
                                'LINK': item['link'].encode('utf-8')}, ignore_index=True)
            print(df)
            #only header when it is the first time
            if first:
                df.to_csv("habitaclia_dataset.csv", mode='wb', header=True, index=False)
                first = False
            else:
                df.to_csv("habitaclia_dataset.csv", mode='ab', header=False, index=False)

