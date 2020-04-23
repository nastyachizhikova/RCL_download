#!/usr/bin/env python
# coding: utf-8

# ### Эта программа может выкачать из поэтического корпуса НКРЯ все тексты одного подкорпуса
# #### Инструкция по применению:
# 1. Открыть Поэтический корпус НКРЯ, задать подкорпус (данная программа тестировалась на подкорпусе текстов с метром, размеченным как анапест)
# 2. Открыть страницу поиска в подкорпусе и, ничего не вводя в строки поиска, нажать "искать" в разделе лексико-грамматического поиска
# 3. Открыть вторую страницу с выдачами, вернуться на первую (я не поняла почему, при этом ссылка поиска меняется и в ней появляется нужный нам номер страницы)
# 4. Скопировать ссылку в указанное место и запустить программу
# 5. CSV-файл со всеми выкачанными текстами создастся в той же директории, где лежит программа

# In[87]:


import requests
import re
from bs4 import BeautifulSoup

#  ссылку на первую страницу - ниже (убедиться, что в конце нее есть 'p=0')
link = 'http://processing.ruscorpora.ru/search.xml?lang=ru&sort=i_grtagging&env=alpha&mydocsize=13276&dpp=10&spp=50&mysentsize=0&mysize=1992466&mycorp=%20%28s_meter%3A%22%D0%90%D0%BD%22%29&level1=0&ext=10&endyear=2016&mode=poetic&parent1=0&text=lexgramm&spd=10&nodia=1&startyear=1996&p=0'


# #### Функция, которая парсит одну страницу поиска

# In[99]:


def parse_one_page(page_link):
    result = requests.get(page_link)
    html = result.text
    soup = BeautifulSoup(html,'html.parser')
    
    poem_names = []  #  создаём список названий и авторов стихотворений на данной странице
    for name in soup.find_all('span', {'class': 'b-doc-expl'}):  
        poem_names.append(name.get_text())
        
    tables = []
    for table in soup.find_all('table'):
        tables.append(table)
    page_poems = tables[2:]  #  первые две таблицы страницы - это шапка, дальше - стихи
    
    poems_list = []  #  список текстов стихов
    for p in page_poems:
        poem_text = ''
        lines = p.find_all('li')
        for line in lines[:-1:]:    
            poem_text += line.text + '\n'
        poems_list.append(poem_text)
    
    poems = []  #  список словарей для каждого стихотворения
    for i, n in enumerate(poem_names):
        poem_dict = {}
        poem_dict['Название'] = n
        poem_dict['Текст'] = poems_list[i]
        poems.append(poem_dict)
    
    return poems


# #### Теперь пройдемся по всем и запишем их в файл

# Если в ссылке поиска указан номер страницы, которой не существует, она ведет на первую страницу.
# Это и будет наш критерий остановки - пока получившаяся страница не такая же, как первая, идем дальше

# In[100]:


import pandas as pd 


# In[101]:


new_link = re.split(r'&p=', link)[0] + '&p=' + '2'


# In[105]:


first_page = parse_one_page(link)
one_dict = first_page
new_page = parse_one_page(new_link)
i = 1  #  счетчик страниц

while new_page != first_page:
    print('Добавляем страницу номер', i)
    one_dict += new_page
    i += 1  
    new_link = re.split(r'&p=', link)[0] + '&p=' + str(i)
    new_page = parse_one_page(new_link)


# In[106]:


pd.DataFrame(one_dict).to_csv(r'RNC_poems.csv', sep='\t', encoding='utf-8')

