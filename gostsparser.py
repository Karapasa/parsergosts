import sys, time
import json
import requests
from bs4 import BeautifulSoup

'''
Программа парсит действующие госты с сайта internet-law.ru и сохраняет их в формате json
Запускается из командной строки, в качестве параметра передается абсолютная ссылка на категорию каталога ГОСТОВ
'''


start_url = None

MAIN_URL = 'https://internet-law.ru/gosts/'
DOMEN = 'https://internet-law.ru'

set_urls=[]
visited_urls =[]

result = {start_url:{}}

def get_start_page():
    global set_urls
    global start_url
    global result
    if len(sys.argv) > 1:
        result.clear()
        start_url = ''.join(sys.argv[1])
        result[start_url] = {}
        set_urls.append(start_url)


def dump_json(result, start_url):
    file_name = get_url_id(start_url) + '.json'
    with open(file_name, 'w', encoding ='utf-8') as file:
        try:
            jsonfile = json.dump(result,file, indent=4)
            print('Данные сохранены в файле {}'.format(file_name))
        except:
            print('Не удалось сохранить данные!')

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
            if soup.find('table', class_='ListGost'):
                result[start_url][soup.title.string] = {'parents': get_parents(soup, url), 'gosts': parsing_all_tables(soup, url)}
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
                if DOMEN + link.attrs['href'].rstrip('/') not in set_urls:
                    set_urls.append(DOMEN + link.attrs['href'].rstrip('/'))
    except:
        print('На странице {} ссылок НЕТ'.format(url))

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
            main_table = soup.find('table', class_='ListGost').tbody.find_all('td', class_='c4')
            parsing = {}
            for data in main_table:
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
        print('Для страницы {} не удалось получить родителей'.format(url))

def len_inner_page(soup):
# Найти кол-во внутренних страниц в основной таблице гостов
    try:
        return len(soup.find('table', class_="Links").find_all('td'))-1
    except:
        return False

def get_url_id(url):
    return url.replace('https://','').split('/')[-1]

def get_inner_url(soup, url):
# Генерация списка url для таблиц с пагинацией
    return [MAIN_URL + get_url_id(url) + "/?p=" + str(i) for i in range(len_inner_page(soup))]

if __name__ == '__main__':
    get_start_page()
    parsing(set_urls)
    dump_json(result, start_url)
