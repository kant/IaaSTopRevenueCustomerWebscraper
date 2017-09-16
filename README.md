# IaasTopRevenueCustomerWebscraper

A script (Python) to scrape specified websites containing the World's top companies by revenue and merge this inforation with secondary sources to detemine whether these companies use Azure/AWS or neither.

## Overview

The script pulls data from static web pages. 
First the top companies by revenue is retrieved: https://en.wikipedia.org/wiki/List_of_largest_companies_by_revenue
Then lists of customer for AWS is retrieved: https://aws.amazon.com/solutions/case-studies/all/
These a list Azure are retrieved: https://www.quora.com/What-are-publicly-known-biggest-customers-of-the-Microsoft-Azure-Platform
A comparison is done and this data is then combined to give an indication of whether the top companies use Azure/AWS/both/neither.

## Running the script

After installing dependencies in `requirements.txt` script can be executed by entering a python 3.6.2 environment and calling ```python Webscraper.py```

## Caveats/Future work
**Note: An future improvmenent is to pull dynamic content (i.e. data rendered at a later stage by javascript/AJAX).**

Libraries to achieve such functionality could be Dryscraper or Selenium 

With Dynamic content, more comrehensive data is available: 
1. Better top company data sources: 
   https://www.forbes.com/global2000/list/#header:revenue_sortreverse:true
2. Comprehensive list of Azure customers (will need to handle pagination):
   https://azure.microsoft.com/en-us/case-studies/

## Algorithm

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

## Prerequisites

1. This script runs in a python 3.6.2 environment 
2. The dependencies can be viewed in the requirements.txt file
3. Many of the dependencies are actually for jupyter notebook, which is useful for writing scripts in blocks in a webbrowser

## Installing Dependencies

Dependencies are managed via python pip and can be installed as follows:

* `!pip install lxml`
* `!pip install requests`
* `!pip install pandas`
* `!pip install bs4`
* `!pip install openpyxl`
