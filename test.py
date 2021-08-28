import requests
from bs4 import BeautifulSoup

BASE_URL = 'http://ce.um.ac.ir/index.php?lang=fa'


def get_news():
    URL = BASE_URL
    response = requests.get(URL)
    soup = BeautifulSoup(response.content, 'html.parser')
    title_result = soup.find_all('div', attrs={'class': 'aidanews2_positions'})
    title = [item.h1.a.text for item in title_result]
    links = [item.h1.a['href'] for item in title_result]
    print(title[:])
    print(links)

    date_time_result = soup.find_all('span', attrs={'class': 'aidanews2_date'})
    date_time = [item.text for item in date_time_result]
    # print(date_time)

    #  get every links on page
    project_href = [i['href'] for i in soup.find_all('a', href=True)]
    # print(project_href)


get_news()


def get_contact():
    URL = BASE_URL
    response = requests.get(URL)
    soup = BeautifulSoup(response.content, 'html.parser')
    contact_result = soup.find_all('ul', attrs={'class': 'contact-info'})
    contact_info = [item.li.text for item in contact_result]
    print(contact_info)


# get_contact()


def tmp():
    # 'http://ce.um.ac.ir/index.php?option=com_groups&view=enarticles&edugroups=3105&cur_stu_title=&Itemid=694&lang=fa'
    url = 'http://ce.um.ac.ir/index.php?option=com_groups&view=prarticles&edugroups=3105&cur_stu_title=&Itemid=620&lang=fa'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    number_result = soup.find_all('td', attrs={'style': 'padding:5px; border:1px solid #E6E6E6; text-align:center !important;'})
    title_result = soup.find_all('td', attrs={'style': 'padding:5px; border:1px solid #E6E6E6; text-align: justify !important; direction: ltr; '})
    date_result = soup.find_all('td', attrs={'style': 'padding:5px; border:1px solid #E6E6E6;'})
    author_result = soup.find_all('td', attrs={'style': 'padding:5px; border:1px solid #E6E6E6;'})
    authors = [item.text for item in author_result]  # odds
    date = [item.text for item in date_result]  # even
    titles = [item.text for item in title_result]
    links = [item.a['href'] for item in title_result]
    for z, y, i, l in list(zip(titles, authors[1::2], date, links)):
        print(z, y, i, l)


# tmp()
