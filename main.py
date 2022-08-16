import requests
from bs4 import BeautifulSoup
import pandas

"""
Сбор данных с анкет на сайте https://nemez1da.ru/
"""


def get_requests(url):
    """получаем ответ от страницы, содержащий html"""
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:92.0) Gecko/20100101 Firefox/92.0',
               'Accept': '*/*'
               }
    return requests.get(url=url, headers=headers)


def get_pages_count(html):
    """получаем количество страниц выдачи"""
    soup = BeautifulSoup(html, 'html.parser')
    return int(soup.find('div', class_='nav-links').find_all('a', class_='page-numbers')[-2].text)


def get_links(html):
    """собираем все ссылки на анкеты"""
    soup = BeautifulSoup(html, 'html.parser')
    blocks = soup.find('div', class_='simple-grid-posts-content').find_all('div', class_='simple-grid-grid-post simple-grid-5-col simple-grid-360w-360h-grid-thumbnail')
    return [block.h3.a['href'] for block in blocks]


def get_content(link):
    """сбор данных с анкеты"""
    soup = BeautifulSoup(get_requests(link).text, 'html.parser')
    data = []
    name = soup.h1.text
    photo = [p['href'] for p in soup.find('div', class_='photos_single_place').find_all('a')]
    data_invite = soup.find('span', class_='simple-grid-entry-meta-single-date').text.strip()
    description = soup.find('div', class_='entry-content simple-grid-clearfix').text.strip()#.replace('\n', ' ')
    data.append({
        'ФИО': name,
        'Дата добавления': data_invite,
        'Фото': photo,
        'Известная информация': description,
        'Ссылка': link
    })
    # print(name)
    # print(*photo)
    # print(data_invite)
    # print(description)
    # print()
    return data


def save_to_excel(data):
    df = pandas.DataFrame(data)
    writer = pandas.ExcelWriter('data.xlsx')
    df.to_excel(writer)
    writer.save()
    print(f'Данные сохранены в data.xlsx')


def parser(url):
    req = get_requests(url)
    if req.status_code == 200:
        pages = get_pages_count(req.text)
        print(f'Всего страниц выдачи {pages}')
        links = []
        for page in range(1, pages + 1):
            r = get_requests(url + f'page/{page}/')
            links.extend(get_links(r.text))
            print(f'Идет сбор ссылок на анкеты. Собрано: {len(links)}')
        with open("links.txt", "w") as file:
            print(*links, file=file, sep='\n')
        with open('links.txt') as file:
            links = file.readlines()
        data = []
        for i, link in enumerate(links):
            print(f'{i + 1} из {len(links)}  анкет обработано')
            data.extend(get_content(link.strip()))
        save_to_excel(data)
    else:
        print(f"Ошибка доступа к сайту: {req.status_code}")


if __name__ == '__main__':
    parser('https://nemez1da.ru/voennye-prestupniki/gur/')

