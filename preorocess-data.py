import numpy as np # calculation
import pandas as pd # Excel for Python
import datetime as dt # allow for date and time series manipulation
import seaborn as sns # a charting package
import matplotlib.pyplot as plt # the original Python chating package

df = pd.read_csv('datay.csv', encoding='ISO-8859-1')

# select the required columns
df = df[['CustomerID', 'InvoiceDate', 'Country']]

# drop rows with null values
df.dropna(inplace=True)

# update column types
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
df['CustomerID'] = df['CustomerID'].astype(int)

# change date format
df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"].dt.strftime('%m%Y'))

#Uses the datetime function to gets the month a datetime stamp and strips the time
def get_month(x):
    return dt.datetime(x.year, x.month, 1) #year, month, incremints of day

#Create a new column
df['InvoiceMonth'] = df['InvoiceDate'].apply(get_month)

#Create a CohortMonth column by grouping data and selecting the earliest instance in the data.
df['CohortMonth'] = df.groupby('CustomerID')['InvoiceMonth'].transform('min')

#When passed a datetime column this functions splits out year, month, day
def get_date(df, column):
    year = df[column].dt.year
    month = df[column].dt.month
    day = df[column].dt.day
    return year, month, day

#splits invoiced month and data into single variables
invoice_year, invoice_month, _ = get_date(df, 'InvoiceMonth')

#splits cohort month and data into single variables
cohort_year, cohort_month, _ = get_date(df, 'CohortMonth')

# Creating a variable which holds the differnce between the invoice and cohort year
year_diff = invoice_year - cohort_year

# Creating a variable which holds the differnce between the invoice and cohort month
month_diff = invoice_month - cohort_month

#Now creating a column that has the calclation shows the
df['CohortIndex'] = year_diff * 12 + month_diff + 13

# save dataframe
df.to_csv('cohorts.csv')

##### --------- Cohort Analysis Exploration --------- #####

# Group the data by columns CohortMonth','CohortIndex' then aggreate by column 'CustomerID'
cohort_data = df.groupby(
    ['CohortMonth', 'CohortIndex'])['CustomerID'].apply(pd.Series.nunique).reset_index()

#Take the cohort_data and plumb it into a Pivot Table. Setting index, columns and values as below.
cohort_count = cohort_data.pivot_table(index = 'CohortMonth',
                                       columns = 'CohortIndex',
                                       values = 'CustomerID')

cohort_size = cohort_count.iloc[:,0] #select all the rows : select the first column
retention = cohort_count.divide(cohort_size, axis=0) #Divide the cohort by the first column
retention.round(3) # round the retention to 3 places
retention.set_axis(range(1, len(retention.columns)+1), axis=1, inplace=True)
retention.set_axis(['Dec10', 'Jan11', 'Feb11', 'Mar11', 'Apr11', 'May11', 'Jun11', 'Jul11',
                    'Aug11', 'Sep11', 'Oct11', 'Nov11', 'Dec11'], axis=0, inplace=True)

plt.figure(figsize = (11,9))
plt.title('Cohort Analysis - Retention Rate')
sns.heatmap(data = retention,
            annot = True,
            fmt = '.0%',
            vmin = 0.0,
            vmax = 0.5,
            cmap = "YlGnBu")
plt.show()