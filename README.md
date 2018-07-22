ebcrawler
=========

This is a simple tool to get prices from SAS using their api. 

Requirements
------------

* Python3
* requests library (can usually be installed with `pip install requests`)
* Pandas

Usage
------------

With the sasCrawler.py file or Jupyter Notebook, get results by calling function fetch_prices

```
a = fetch_prices(From, To, OutDate, Indate, Type)
```


From, To - IATA Airport Code  
OutDate, Indate - Format YYYYMMDD  
Type - "star"(Star Alliance award flights), "revenue" (Regular revenue fares) or "points" (SAS awards flights)  

The output of the fetch_prices function is for now in json.   

To parse the prices in to a Pandas DataFrame, use the function parse_results:  

Example in Jupyter notebook:  
´´´
from sasCrawler import fetch_price, parse_results

a = fetch_price("OSL", "HKG", "20190301", "20190308", "star")
df_out, df_in = parse_results(a)
´´´

The flights are now in their respective DataFrame table for exploration. 

Next in line is a crawler that can check availability!

