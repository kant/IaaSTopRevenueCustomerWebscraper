
# coding: utf-8
import pandas as pd
from lxml import html
import requests
#This code as compiled on a mac, to ensure web requests pull successfully, ensure the 
#latest openssl version 1.0.2k installed for retrieving data from forbes.com as they have 
#strict certificate enforcement, to check:
# -> import ssl
# -> print(ssl.OPENSSL_VERSION)

#parse html table into a list of python dataframes for processing
#wikipedia is not the best reference or most comprehensive, future version to pull data from forbes
top30CompanyByRevenueURL = 'https://en.wikipedia.org/wiki/List_of_largest_companies_by_revenue'
htmlList = pd.read_html(top30CompanyByRevenueURL)

#retrieves relevant columns and assigns column names for combining and munging of data
def generateTopCompaniesDataFrame(htmlList):
    topCompanyRawDataFrame = htmlList[0]
    topCompanyNameRevenueDataFrame = cleanupDataframe(topCompanyRawDataFrame)
    topCompanyNameRevenueDataFrame['UsesAWS'] = False
    topCompanyNameRevenueDataFrame['AWSMatchRatio'] = 0
    topCompanyNameRevenueDataFrame['UsesAzure'] = False
    topCompanyNameRevenueDataFrame['AzureMatchRatio'] = 0
    return topCompanyNameRevenueDataFrame

#format data frame columns for readability and extract relevant fields for task
def cleanupDataframe(rawDataFrame):
    cleanedDataFrame = rawDataFrame[[1,3,5]].copy()
    cleanedDataFrame.columns = cleanedDataFrame.iloc[0]
    cleanedDataFrame = cleanedDataFrame[1:]
    return cleanedDataFrame

top30CompanyNameRevenueDataFrame = generateTopCompaniesDataFrame(htmlList)


# In[6]:


def generateHTMLTree(linkToScrape):
    pageResponse = requests.get(linkToScrape)
    tree = html.fromstring(pageResponse.content)
    return tree
    
def extractCompanyNames(htmlTree,htmlTagFilter):
    companies = htmlTree.xpath(htmlTagFilter)
    return companies    

def cleanList(listToClean,phraseList):
    tempCompanyList=[]
    for company in listToClean:
        for phrase in phraseList:
            company = company.replace(phrase,'')
        tempCompanyList.append(company)
    
    tempCompanyList = list(filter(None, tempCompanyList))
    return tempCompanyList
    
AWSCustomerlinkToScrape='https://aws.amazon.com/solutions/case-studies/all/'
AWSHtmlTagFilter = './/h2/a[contains(@href,"//aws.amazon.com/solutions/case-studies")]//text()'

#Terms to clean out form the data
AWSPhraseList = ['AWS Case Study: ','Case Study']

AWSTree = generateHTMLTree(AWSCustomerlinkToScrape)
AWSCompanies = extractCompanyNames(AWSTree,AWSHtmlTagFilter)
cleanedAWSCompanyList = cleanList(AWSCompanies,AWSPhraseList)


# In[7]:


azureCustomerLinkToScrape='https://www.quora.com/What-are-publicly-known-biggest-customers-of-the-Microsoft-Azure-Platform'
azureHtmlTagFilter='//div[@class="AnswerWiki"]//text()'
azurePhraseList = ['find more at ','Customer and Partner Success Stories for Microsoft Azure']

azureTree = generateHTMLTree(azureCustomerLinkToScrape)
azureCompanyNames = extractCompanyNames(azureTree,azureHtmlTagFilter)
cleanedAzureCompanyList = cleanList(azureCompanyNames,azurePhraseList)


# In[8]:


from difflib import SequenceMatcher

def checkStringMatchingRatio(stringOne,stringTwo):
    return SequenceMatcher(None,stringOne,stringTwo).ratio()

#print(checkStringMatchingRatio('Walmart','Walmart')) gives 1.0
#print(checkStringMatchingRatio('Walmart','Wal-Mart')) gives 0.8
#print(checkStringMatchingRatio('Walmart','Mart-Wal')) gives 0.4


# In[9]:


def checkDirectCompanyMatch(company1,company2):
    matchMinimumThreshold = 0.8
    matchRatio = checkStringMatchingRatio(company1.replace(' ',''),company2.replace(' ',''))
    if (matchRatio > matchMinimumThreshold):
        closeMatch = True
    else: 
        closeMatch = False
    return closeMatch,matchRatio
    
#for the case that Samsung appears in Samsung Electronics etc.
def checkForAbbreviation(company1Name,company2Name):
    if (company1Name.find(company2Name)) >= 0:
        return True
    elif (company2Name.find(company1Name)) >= 0:
        return True
    else:
        return False
        
def checkForCompanyMatchInMasterList(companyListToCompare,top30CompanyNameRevenueDataFrame,providerFields):
    exactMatch=False
    isAbbreviated=False
    for companyToCheck in companyListToCompare:
        for index, row in top30CompanyNameRevenueDataFrame.iterrows():
            exactMatch,matchRatio = checkDirectCompanyMatch(companyToCheck,row['Name'])
            isAbbreviated = checkForAbbreviation(companyToCheck,row['Name'])
            if (exactMatch or isAbbreviated):
                print(row['Name'],'-',companyToCheck,index)
                #flag an absolute match
                top30CompanyNameRevenueDataFrame.loc[index,providerFields[0]] = True 
                #flag a possible match, with a rating
                top30CompanyNameRevenueDataFrame.loc[index,providerFields[1]] = round(matchRatio,3)
    
    return top30CompanyNameRevenueDataFrame

AWSFields = ['UsesAWS','AWSMatchRatio']
AzureFields = ['UsesAzure','AzureMatchRatio']
checkForCompanyMatchInMasterList(cleanedAWSCompanyList,top30CompanyNameRevenueDataFrame,AWSFields)
checkForCompanyMatchInMasterList(cleanedAzureCompanyList,top30CompanyNameRevenueDataFrame,AzureFields)

# In[10]:


def displayMaskedDataFrame(dataFrame,columnNames):
    for columnName in columnNames:
        mask = dataFrame[columnName] == 0
        dataFrame.loc[mask, columnName] = '-'
    print(dataFrame)

displayMaskedDataFrame(top30CompanyNameRevenueDataFrame[:].copy(),['AWSMatchRatio','AzureMatchRatio'])

