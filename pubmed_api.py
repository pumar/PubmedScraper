# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup as bs
import os
import time


class PubMedScraper(object):
    
    def __init__(self,
                 proxy = None):
        
        
        self.proxies = {'https' : proxy}
        self.base = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/'
        self.db = 'pubmed'
        self.retmode = 'xml'
    
    def __query_builder(self,
                      input_keywords):
        return input_keywords.replace(' ','+')
    
    def search(self,
               query,
               max_results=15000):
        
        if ' ' in query:
            query = self.__query_builder(query)
        
        search_url = self.base + 'esearch.fcgi?db=' + self.db + '&retmode=' + \
        self.retmode + '&retmax=' + str(max_results) + '&term=' + query + \
        '&sort=relevance'+'&usehistory=y'

        search_response = requests.get(search_url,proxies = self.proxies)
        
        time.sleep(5)
        
        soup = bs(search_response.text, 'xml')
        
        webenv = soup.find('WebEnv').text
        qkey = soup.find('QueryKey').text
        article_count = int(soup.find('RetMax').text)
        
        if article_count > 10000:
            
            self.results = list()
            
            for retmin in range(0,article_count,10000):

                if (retmin + 10000) > article_count:
                    retmax = article_count
                    print('Making an API request for articles numbered ' + str(retmin)+ ' to ' + str(retmax))
                else:
                    retmax = retmin + 9999
                    print('Making an API request for articles numbered ' + str(retmin)+ ' to ' + str(retmax))
                    
                fetch_url = self.base + 'efetch.fcgi?db=' + self.db + \
                '&query_key=' + qkey + '&WebEnv=' + webenv +'&retmin=' + \
                str(retmin) +'&retmax='+\
                str(retmax)+'&rettype=xml&retmode=xml'
                
                fetch_response = requests.get(fetch_url, proxies = self.proxies)
                
                time.sleep(5)
                
                self.results.append(bs(fetch_response.text, 'xml'))
                
            
        else:
            
            fetch_url = self.base + 'efetch.fcgi?db=' + self.db + \
            '&query_key=' + qkey + '&WebEnv=' + webenv + '&retmax='+\
            str(article_count)+'&rettype=xml&retmode=xml'
            
            fetch_response = requests.get(fetch_url, proxies = self.proxies)
            
            fetch_soup = bs(fetch_response.text, 'xml')
            
            self.results = [fetch_soup]

    
    def __content_extract(self,
                       article):
        
        contents = list()
        
        contents.append(article.find('ArticleTitle').text) #Title
        try:
            contents.append(article.find('ArticleDate').find('Year').text + '-' +\
            article.find('ArticleDate').find('Month').text + '-' +\
            article.find('ArticleDate').find('Day').text)
        except:
            try:
                contents.append(article.find('History').find('Year').text + '-' +\
                article.find('History').find('Month').text + '-' +\
                article.find('History').find('Day').text)
            except:
                contents.append('')
        
        author_list = article.find_all('Author')
        if len(author_list) == 0:
            contents.append('')
            contents.append('')
            contents.append('')
            contents.append('')
            
        elif len(author_list) == 1:
            try:
                fname = author_list[0].find('ForeName').text
            except:
                fname = ''
            try:
                lname = author_list[0].find('LastName').text
            except:
                lname = ''
            contents.append(fname + ' ' + lname)
            
            try:
                contents.append(author_list[0].find('Affiliation').text)
            except:
                contents.append('')
            contents.append('')
            contents.append('')
            
        else:
            try:
                fname = author_list[0].find('ForeName').text
            except:
                fname = ''
            try:
                lname = author_list[0].find('LastName').text
            except:
                lname = ''
            contents.append(fname + ' ' + lname)
            
            try:
                contents.append(author_list[0].find('Affiliation').text)
            except:
                contents.append('')
            authors = ''
            insts = ''
            for i,author in enumerate(author_list):
                if i == 0:
                    continue
                try:
                    authors += author.find('ForeName').text + ' ' + \
                    author.find('LastName').text + ', '
                except:
                    pass
                try:
                    insts += author.find('Affiliation').text + ', '
                except:
                    pass
            contents.append(authors.strip(', '))
            contents.append(insts.strip(', '))
        
        keywords = article.find_all('Keyword')
        if len(keywords) >= 1:
            contents.append(', '.join([kw.text for kw in keywords]))
        else:
            contents.append('')
        
        contents.append(article.find('Journal').find('Title').text)
        
        contents.append(' '.join([abst.text for abst in article.find_all('AbstractText')]).replace('\n',''))
        
        contents = ['"' + content.replace('"','').replace('\n','').strip() + '"' for content in contents]
        return contents
            
       
    
    def saveas(self,
               filename=''):
        
        file = filename.split('.')[-1]
        ### Still broken, needs fixing
        if file == 'xml':
            for result in self.results:
                with open(filename,'w') as f:
                    f.write("\n".join(str(result,encoding='utf-8') ))
        ###
        if file == 'csv':
            article_line = list()
            
            for result in self.results:
                for article in result.find_all('PubmedArticle'):
                    article_line.append(self.__content_extract(article))
                    
            with open(filename, 'w',encoding='utf-8') as f:
                f.write('"Article Title","Published Date","Main Author","Main Author Affiliation","Secondary Author(s)","Secondary Author(s) Affiliation","Keywords","Journal Name","Abstract"\n')
                for row in article_line:
                    f.write(','.join(row) + '\n')
        


scraper = PubMedScraper(os.environ['http_proxy'])

scraper.search(query = 'warfarin+OR+apixaban+OR+dabigatran+OR+rivaroxaban+OR+edoxaban', max_results = 15000)

scraper.saveas(filename = 'pfizer_pubmed.csv')
