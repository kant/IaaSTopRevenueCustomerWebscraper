# IaasTopRevenueCustomerWebscraper

A script (Python) to scrape specified websites containing the World's top companies by revenue and merge this inforation with secondary sources to detemine whether these companies use Azure/AWS or neither.

## Overview

The algorithm for this script is as follows:
1. Pull the list of top companies by revenue (listA)
2. Pull a list of AWS customers (listB)
3. Pull a list of Azure customers (listC)
4. Munge all the data retrieved
5. Compare listB to listA and search for matches
6. Where there is not a direct match, see if there is a less direct match and rate it 
7. Compare listC to listA and search for matches
8. Where there is not a direct match, see if there is a less direct match and rate it
9. Ouput the information to excel for review

## Caveats/Future work

### Prerequisites

1. This script runs in a python 3.6.2 environment 
2. The dependencies can be viewed in the requirements.txt file
3. Many of the dependencies are actually for jupyter notebook, which is useful for writing scripts in blocks in a webbrowser

## Installing Dependencies

Dependencies are managed via python pip and can be installed as follows:

* !pip install lxml
* !pip install requests
* !pip install pandas
* !pip install bs4
* !pip install openpyxl

## Deployment