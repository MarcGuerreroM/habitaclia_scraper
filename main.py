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
        dic['location'] = child.find("p", {"class": "list-item-location"}).span.string
        l = child.find("p", {"class": "list-item-feature"}).get_text().split("-")
        try:
            dic['surface'] = int(l[0].split('m2')[0])
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



if __name__ == "__main__":
    url = "https://www.habitaclia.com/viviendas-en-valles_oriental.htm"
    info = []
    available_pages = get_available_pages(url)
    df = pd.DataFrame(columns=['TITLE','LOCATION', 'SURFACE', 'N_BATHROOMS', 'PRICE_METER', 'TOTAL_PRICE', 'LINK'])
    for page in available_pages:
        main_page = get_website(page)
        encoding = main_page.encoding if 'charset' in main_page.headers.get('content-type', '').lower() else None
        soup = BeautifulSoup(main_page.content, from_encoding=encoding, features="html.parser")
        partial_info = get_info(soup)
        for i in partial_info:
            info.append(i)
    for item in info:
        df = df.append({'TITLE': item['title'].encode('utf-8'),'LOCATION': item['location'].encode('utf-8'), 'SURFACE': item['surface'],
                        'N_BATHROOMS': item['n_bathrooms'],'PRICE_METER': item['price_meter'],'TOTAL_PRICE': item['total_price'],
                        'LINK': item['link'].encode('utf-8')}, ignore_index=True)
    print(df)
    df.to_csv("habitaclia_dataset.csv")

