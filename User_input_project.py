#this file combines the code from project_user_input.py and joindata.py 

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

#### Join Outputs of api_requests.py ####
## Read in .csv files
bigDF = pd.DataFrame()
foodDF = pd.read_csv("food_df.csv")
hosp_parkDF = pd.read_csv("hosp_park_df.csv")
schoolDF = pd.read_csv("school_df.csv")

## Combine .csv files to one df
bigDF = pd.concat([bigDF, foodDF, hosp_parkDF, schoolDF])
bigDF.to_csv("bigDF.csv")

#### Clean Data ####
## Pivot on ZIP & reset index
bigDF_pivot = bigDF.pivot(index="ZIP", columns="Search_keyword", values="Name")
bigDF_pivot.reset_index(inplace=True)
bigDF_pivot.to_csv("bigDF_pivot.csv")

## Fill NA with 0, change data types
bigDF_pivot.fillna(0, inplace=True)
bigDF_pivot = bigDF_pivot.astype({"ZIP": "str", "college": "Int32", "elementary school": "Int32", "food bank": "Int32", "grocery store": "Int32", "high school": "Int32", "hospital": "Int32", "middle school": "Int32", "park": "int32", "university": "Int32"})

## Drop rows that dont fit the pattern for ZIP
pattern = r"[0-9]{5}"
filter = bigDF_pivot['ZIP'].str.contains(pattern)
bigDF_pivot = bigDF_pivot[filter]

## Group keywords to SCHOOL, FOOD ACCESS, HEALTH CARE, GREEN SPACES
groups = {
    'SCHOOL': ['college', 'elementary school', 'high school', 'middle school', 'university'],
    'FOOD ACCESS': ['food bank', 'grocery store'],
    'HEALTH CARE': ['hospital'],
    'GREEN SPACES': ['park']
} 
grouped_bigDF = bigDF_pivot.copy()
for group, keywords in groups.items():
    grouped_bigDF[group] = grouped_bigDF[keywords].sum(axis=1)

## Drop extra columns
grouped_bigDF = grouped_bigDF.drop(columns = ["college", "elementary school", "food bank", "grocery store", "high school", "hospital", "middle school", "park", "university"])

## Sum Group
grouped_bigDF['TOTAL'] = grouped_bigDF.iloc[:, 1:].apply(lambda x: x.sum(), axis=1)

## Create SCORE, total / average of total
AVG = np.mean(grouped_bigDF["TOTAL"])
grouped_bigDF['SCORE'] = grouped_bigDF["TOTAL"].apply(lambda x: x / AVG)

## Create TAG based on SCORE
## 0-0.5 = HIGH NEED, 0.51-0.75 = MOD NEED, 
## 0.76-1.5 LOW NEED, 1.51+ = ABOVE AVERAGE

def tag(row):
    if row["SCORE"] <= 0.5:
        return "High need"
    elif row["SCORE"] <= 0.75:
        return "Moderate need"
    elif row["SCORE"] <= 1.5:
        return "Low need"
    else:
        return "Above average"

grouped_bigDF["TAG"] = grouped_bigDF.apply(tag, axis=1)

###############creating user inputs#######################################

zipcode= input('Enter zip code here')
row=grouped_bigDF[grouped_bigDF['ZIP']==zipcode]
cols=grouped_bigDF.columns.tolist()
labels= cols[1:-3]
values= row[labels].values[0]
tag = row['TAG'].values[0]
score= row['SCORE'].values[0]

# Bar graph for frequency of each resource
plt.figure(figsize=(10, 6))
plt.bar(labels, values)
plt.title('Neighborhood Index for Zip Code %s: \n %.2f \n %s' % (zipcode, score, tag))
plt.xlabel("Categories")
plt.ylabel("Values")
plt.xticks(rotation=45)
plt.grid(axis='y')








