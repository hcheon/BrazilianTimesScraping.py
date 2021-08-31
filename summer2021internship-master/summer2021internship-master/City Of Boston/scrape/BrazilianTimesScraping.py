#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# Import libraries
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re


# In[1]:


# Base URL Brazilian Times
URL = 'https://www.braziliantimes.com/noticias/comunidade-brasileira'

# Scrape data from page/tab 1 to below page/tab
# At the time of writing this code, Brazilian Times had news from Jan 2020 to Jun 2021 from pages 1 to 417
PAGES = 47


# In[ ]:


# Initiate an empty data frame
df = pd.DataFrame(columns=['Date', 'URL', 'Title', 'Article'])


# In[ ]:


i = 1
idx = 0
for i in range(1,PAGES+1):
    if i == 1:
        page = requests.get(URL) # for first page
    else:
        page = requests.get(URL + '/' + str(i)) # for other pages except first
    
    # create BeautifulSoup object
    soup = BeautifulSoup(page.content, 'html.parser')
    
    # URL's can be found under <div> with class as 'col-sm-8'
    # We take the first two <div> which have the URL's, the last <div> does not have URL's
    # Hence we take the first two <div>
    for div in soup.find_all('div', {'class': 'col-sm-8'})[0:2]:
        for a in div.find_all('a'): # URL's are under <a> inside <div>
            df.loc[idx, 'URL'] = a.get('href') # Save URL in dataframe
            idx += 1
    print('page ' + str(i) + ' done')


# In[ ]:


# Save dataframe to csv with encoding = 'utf-8'
df.to_csv('../data/BrazilianTimes_Jan2020_to_Jun2021.csv', encoding='utf-8', index=False)


# In[ ]:


# Read the csv
df = pd.read_csv('../data/BrazilianTimes_Jan2020_to_Jun2021.csv', encoding='utf-8')


# In[ ]:


# Below code reads the URL, request the site, gets the date, title and article of the news 
# and saves the data back to the dataframe 
for idx in df.index:
    url = df.loc[idx, 'URL']
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    # All data related to news is under <p> with class 'date margin-bottom-10'
    date = soup.find('p', {'class': 'date margin-bottom-10'}).text
    date = datetime.strptime(date[13:23].strip(), '%d/%m/%Y').strftime('%m/%d/%Y') # get the date
    title = soup.find('h1', {'class': 'title-page'}).text # get the title text
    article = soup.find('div', {'class': 'article-body'}).text # get the article text
    article = re.sub('[\t\n\r\s]+',' ', article).strip() # replace multiple tab, newline or whitespace with single space
    end = article.find('Apoiem os Pequenos negócios. Mantenha a economia girando!') # ad which displays on several pages
    if end != -1:
        article = article[:end] # remove ad text, if present
    df.loc[idx, ['Date', 'Title', 'Article']] = [date, title, article] # save data to dataframe
    print('article ' + str(idx) + ' done')


# In[ ]:


# convert date column to datetime object
df['Date'] = df['Date'].apply(lambda x: datetime.strptime(x,'%m/%d/%Y'))


# In[ ]:


df.sort_values(by='Date', ascending=False, inplace=True) # sort dataframe by date
df.reset_index(drop=True, inplace=True)


# In[ ]:


# Latest news of the day appears on top of every page
# This gets captured in every page/tab
# therefore, removing the duplicate entries
df.drop_duplicates(subset=['URL'], keep='first', inplace=True, ignore_index=True)


# In[ ]:


# Remove any rows, if they have data from 2019
df.drop(df[df.Date.dt.year==2019].index, inplace=True)
df.reset_index(drop=True, inplace=True)


# In[ ]:


# save to final csv
df.to_csv('../data/BrazilianTimes_Jun2021_to_Aug2021.csv', encoding='utf-8', index=False)

