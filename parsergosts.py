import os, time
import requests
from bs4 import BeautifulSoup

start_url = 'https://internet-law.ru/gosts/3755'

MAIN_URL = 'https://internet-law.ru/gosts/'
DOMEN = 'https://internet-law.ru'

set_urls=[start_url]
visited_urls =[]

result = []

def get_page(url):
    session = requests.Session()
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36','Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'}
    try:
        page = session.get(url, headers=headers)
        page.encoding = 'windows-1251'
        return page.text
    except:
        print("СТРАНИЦА {} НЕДОСТУПНА!!!".format(url))

def parsing(set_urls):
    global visited_urls
    global result
    for url in set_urls:
        if url not in visited_urls:
            html = get_page(url)
            time.sleep(1)
            soup = BeautifulSoup(html, 'html.parser')
            if check_parsing_table(soup):
                result.append(get_parents(soup, url))
                result.append(parsing_all_tables(soup, url))
                visited_urls.append(url)
                print('Страница {} обработана и получены данные'.format(get_url_id(url)))
            else:
                get_links(soup, url)
                visited_urls.append(url)
                print('Категория {} обработана и получены ссылки'.format(get_url_id(url)))
                parsing(set_urls)


def get_links(soup, url):
    global set_urls
    try:
        for link in soup.find('div', id='p'+get_url_id(url)).next_sibling.find_all('a'):
            if 'href' in link.attrs:
                if get_full_url_for_spider(link.attrs['href'].rstrip('/')) not in set_urls:
                    set_urls.append(get_full_url_for_spider(link.attrs['href'].rstrip('/')))
    except:
        print('На странице {} ссылок НЕТ'.format(url))

def check_parsing_table(soup):
    if soup.find('table', class_='ListGost'):
        return True


def parsing_all_tables(soup, url):
    if len_inner_page(soup):
        parsing = {}
        for tables in get_inner_url(soup, url):
            html = get_page(url)
            time.sleep(1)
            soup = BeautifulSoup(html, 'html.parser')
            parsing.update(parsing_inner_table(soup, url))
        return parsing
    else:
        return parsing_inner_table(soup, url)


def parsing_inner_table(soup, url):
# Собирает данные из таблицы в словарь
        try:
            main_table = soup.find('table', class_='ListGost').tbody
            res = main_table.find_all('td', class_='c4')
            parsing = {}
            for data in res:
                if data.string == 'действующий':
                    childs = data.find_previous_siblings('td')
                    parsing[childs[2].string]=childs[1].string
            return parsing
        except:
            print('Для страницы {} не удалось получить данные таблицы'.format(url))

def get_parents(soup, url):
# Вытащить всех родителей из каталога гостов
    try:
        pick = soup.find('div', id='CatList')
        block = soup.find('div', id='p'+get_url_id(url))
        parents = []
        while block.parent != pick:
            parents.append(block.parent.previous_element.string)
            block = block.parent
        return parents
    except:
        print('Для страницы {} не удалост получить родителей'.format(url))

def category_title(soup):
# Для подзаголовка в json
    cat_title=soup.title
    return cat_title.string

def len_inner_page(soup):
# Найти кол-во внутренних страниц в основной таблице гостов
    try:
        inner_block = soup.find('table', class_="Links").find_all('td')
        return len(inner_block)-1
    except:
        return False

def get_url_id(url):
    base_name = url.replace('https://','').split('/')
    return base_name[-1]

def get_inner_url(soup, url):
# Генерация списка url для таблиц с пагинацией
    list_inner_url=[]
    for i in range(len_inner_page(soup)):
        modurl = MAIN_URL + get_url_id(url) + "/?p=" + str(i)
        list_inner_url.append(modurl)
    return list_inner_url

def get_full_url_for_parser(id):
    return MAIN_URL + id

def get_full_url_for_spider(link):
    return DOMEN + link

parsing(set_urls)
print(result)
