import requests
from bs4 import BeautifulSoup

BASE_URL = 'http://ce.um.ac.ir/index.php?lang=fa'


# def get_news():
#     URL = BASE_URL
#     response = requests.get(URL)
#     soup = BeautifulSoup(response.content, 'html.parser')
#     title_result = soup.find_all('div', attrs={'class': 'aidanews2_positions'})
#     title = [item.h1.a.text for item in title_result]
#     print(title[:])
#
#     date_time_result = soup.find_all('span', attrs={'class': 'aidanews2_date'})
#     date_time = [item.text for item in date_time_result]
#     print(date_time)
#
#     project_href = [i['href'] for i in soup.find_all('a', href=True)]
#     print(project_href)
#
#
# get_news()
#
#
# def get_contact():
#     URL = BASE_URL
#     response = requests.get(URL)
#     soup = BeautifulSoup(response.content, 'html.parser')
#     contact_result = soup.find_all('ul', attrs={'class': 'contact-info'})
#     contact_info = [item.li.text for item in contact_result]
#     print(contact_info)
#
#
# get_contact()
def tmp():
    URL = 'http://ce.um.ac.ir/index.php?option=com_content&view=article&id=187:2016-09-08-14-52-51&catid=108:2016-09-09-10-57-46&lang=fa'
    response = requests.get(URL)
    soup = BeautifulSoup(response.content, 'html.parser')
    contact_result = soup.find_all('div', attrs={'class': 'tab-content'})
    print([item.li.text for item in contact_result])


tmp()
