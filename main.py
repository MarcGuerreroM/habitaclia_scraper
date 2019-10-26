# coding=utf-8
import requests
from bs4 import BeautifulSoup

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
if __name__ == "__main__":
    url = "https://www.habitaclia.com/viviendas-en-valles_oriental.htm"
    main_page = get_website(url)
    encoding = main_page.encoding if 'charset' in main_page.headers.get('content-type', '').lower() else None
    soup = BeautifulSoup(main_page.content, from_encoding=encoding)
    info = get_info(soup)
    for i in info:
        print i
