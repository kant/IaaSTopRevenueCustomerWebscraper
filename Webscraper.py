
# coding: utf-8
import pandas as pd
from lxml import html
import requests
from difflib import SequenceMatcher
#This code as compiled on a mac, to ensure web requests pull successfully, ensure the 
#latest openssl version 1.0.2k installed for retrieving data from forbes.com as they have 
#strict certificate enforcement, to check:
# -> import ssl
# -> print(ssl.OPENSSL_VERSION)

##Functions for creating top companies dataframes from static web content
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

##Functions for creating lists of companies using various services, generated from static web content
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
    
#helper function to compare two strings and return a comparison ratio  
#print(checkStringMatchingRatio('Walmart','Walmart')) gives 1.0
#print(checkStringMatchingRatio('Walmart','Wal-Mart')) gives 0.8
#print(checkStringMatchingRatio('Walmart','Mart-Wal')) gives 0.4  
def checkStringMatchingRatio(stringOne,stringTwo):
    return SequenceMatcher(None,stringOne,stringTwo).ratio()

##Allows for setting of a threshold and evaluating whether name match is acceptable
def checkDirectCompanyMatch(company1,company2):
    matchMinimumThreshold = 0.8
    matchRatio = checkStringMatchingRatio(company1.replace(' ',''),company2.replace(' ',''))
    if (matchRatio > matchMinimumThreshold):
        closeMatch = True
    else: 
        closeMatch = False
    return closeMatch,matchRatio
    
##For the case that Samsung appears in Samsung Electronics etc.
def checkForAbbreviation(company1Name,company2Name):
    if (company1Name.find(company2Name)) >= 0:
        return True
    elif (company2Name.find(company1Name)) >= 0:
        return True
    else:
        return False
        
##Combine all data into a single source where it is determined whether company uses Azure/AWS and where there is not
##a direct match, give a level of certainty
def checkForCompanyMatchInMasterList(companyListToCompare,top30CompanyNameRevenueDataFrame,providerFields):
    exactMatch=False
    isAbbreviated=False
    for companyToCheck in companyListToCompare:
        for index, row in top30CompanyNameRevenueDataFrame.iterrows():
            exactMatch,matchRatio = checkDirectCompanyMatch(companyToCheck,row['Name'])
            isAbbreviated = checkForAbbreviation(companyToCheck,row['Name'])
            if (exactMatch or isAbbreviated):
                #flag an absolute match
                top30CompanyNameRevenueDataFrame.loc[index,providerFields[0]] = True 
                #flag a possible match, with a rating
                top30CompanyNameRevenueDataFrame.loc[index,providerFields[1]] = round(matchRatio,3)
    
    return top30CompanyNameRevenueDataFrame

#Function to display dataframe content cleanly
def displayMaskedDataFrame(dataFrame,columnNames):
    for columnName in columnNames:
        mask = dataFrame[columnName] == 0
        dataFrame.loc[mask, columnName] = '-'
    print(dataFrame)

##Data Sources and relevant field/tags to extract from scraped html data
top30CompanyByRevenueURL = 'https://en.wikipedia.org/wiki/List_of_largest_companies_by_revenue'

AWSCustomerlinkToScrape='https://aws.amazon.com/solutions/case-studies/all/'
AWSHtmlTagFilter = './/h2/a[contains(@href,"//aws.amazon.com/solutions/case-studies")]//text()'
azureCustomerLinkToScrape='https://www.quora.com/What-are-publicly-known-biggest-customers-of-the-Microsoft-Azure-Platform'
azureHtmlTagFilter='//div[@class="AnswerWiki"]//text()'

print('Reading top revenue company data')
htmlList = pd.read_html(top30CompanyByRevenueURL)
top30CompanyNameRevenueDataFrame = generateTopCompaniesDataFrame(htmlList)

##Terms to clean out the scraped AWS/Azure data
AWSPhraseList = ['AWS Case Study: ','Case Study']
azurePhraseList = ['find more at ','Customer and Partner Success Stories for Microsoft Azure']

##Scrape links and clean data
print('Scraping AWS customers data source')
AWSTree = generateHTMLTree(AWSCustomerlinkToScrape)
AWSCompanies = extractCompanyNames(AWSTree,AWSHtmlTagFilter)
cleanedAWSCompanyList = cleanList(AWSCompanies,AWSPhraseList)

print('Scraping Azure customer data source')
azureTree = generateHTMLTree(azureCustomerLinkToScrape)
azureCompanyNames = extractCompanyNames(azureTree,azureHtmlTagFilter)
cleanedAzureCompanyList = cleanList(azureCompanyNames,azurePhraseList)

##Compare scraped data with data in top company dataframe and update relevant fields
#Fields to update in matching step
print("Matching top revenue customers with Azure/AWS customers")
AWSFields = ['UsesAWS','AWSMatchRatio']
AzureFields = ['UsesAzure','AzureMatchRatio']
checkForCompanyMatchInMasterList(cleanedAWSCompanyList,top30CompanyNameRevenueDataFrame,AWSFields)
checkForCompanyMatchInMasterList(cleanedAzureCompanyList,top30CompanyNameRevenueDataFrame,AzureFields)
displayMaskedDataFrame(top30CompanyNameRevenueDataFrame[:].copy(),['AWSMatchRatio','AzureMatchRatio'])

#save data to excel for analysis
writer = pd.ExcelWriter('IaasTopRevenueCustomersList.xlsx',index=False)
top30CompanyNameRevenueDataFrame.to_excel(writer,'Sheet1')
writer.save()

