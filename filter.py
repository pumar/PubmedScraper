# -*- coding: utf-8 -*-
"""
Created on Mon Feb 10 14:35:40 2020

@author: z5g1327
"""

import pandas as pd

df = pd.read_csv('pfizer_pubmed.csv')
#%%
df.drop_duplicates(subset=["Article Title","Main Author","Keywords"],inplace=True)
#%%
df.dropna(subset=["Article Title", "Abstract"],inplace = True)

#dftest = df[df["Article Title"] == "Comparison of the Novel Oral Anticoagulants Apixaban, Dabigatran, Edoxaban, and Rivaroxaban in the Initial and Long-Term Treatment and Prevention of Venous Thromboembolism: Systematic Review and Network Meta-Analysis."]

df["URL"] = "https://www.ncbi.nlm.nih.gov/pubmed/" + df["PMID"].astype('str')

df.to_csv('pfizer_pubmed.csv',index=False)
