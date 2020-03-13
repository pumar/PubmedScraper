# -*- coding: utf-8 -*-


import pandas as pd
import numpy as np

df = pd.read_csv('pfizer_pubmed.csv')

df.drop_duplicates(subset=["Article Title","Main Author"],inplace=True)

df.dropna(subset=["Article Title", "Abstract"],inplace = True)

df["URL"] = "https://www.ncbi.nlm.nih.gov/pubmed/" + df["PMID"].astype('str')
df["Number of Citations"] = np.nan
#dftest = df[df["Article Title"] == "Comparison of the Novel Oral Anticoagulants Apixaban, Dabigatran, Edoxaban, and Rivaroxaban in the Initial and Long-Term Treatment and Prevention of Venous Thromboembolism: Systematic Review and Network Meta-Analysis."]


from selenium import webdriver

options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument('window-size=1920x1080')
options.add_argument("disable-gpu")

driver = webdriver.Chrome('chromedriver/chromedriver.exe',chrome_options=options)

def numCitations(url):
        
    driver.get(url)
    opts = driver.find_elements_by_class_name('portlet_title')
    
    for opt in opts:
        if "Cited by" in opt.text:
            try:
                return int((opt.text).split(" ")[2])
            except:
                print(url)
                return int((opt.text).split(" ")[3])
            
    return 0


for i in df.index:
    df.at[i,"Number of Citations"] = numCitations(df.at[i,"URL"])

print(df["Number of Citations"].describe())

#df.to_csv('pfizer_pubmed.csv',index=False)
