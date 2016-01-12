#!/usr/lib/python2.7
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import requests
import urllib.parse
import csv
import lxml
import string
import sys
import json
import time 
import pprint
# Helpfull color
class bcolors:
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

## Downloader
def download(url):
    print(bcolors.WARNING + bcolors.BOLD + 'GO download on : ' + bcolors.FAIL + url + bcolors.ENDC)
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'}
    response = requests.get(url, headers=headers)
    errorList = []
    errorFile = 'errorDB.json'
    if response.status_code == 200:
        return response.text
    else:
        print('error on :', response.status_code)
        errURL = errorList.append(url)
        return errURL

## JSON saving
def json_save(filename, data):
    with open(filename, 'a') as data_file:
        json.dump(data, data_file, indent=1)

## Recurent target profiles
def dataTarget(html_body, extracted_info):
    for x in html_body:
        author_url = x.find('div', {'class' : 'name'}).find('a').get('href')
        author_name = x.find('div', {'class' : 'name'}).find('a').getText()
        author_rank = x.find('div', {'class' : 'actions'}).getText()
        author_desc = x.find('div', {'class' : 'description'}).getText()
        author_desc_url = x.find('div', {'class' : 'description'}).find_all('a')
        author_desc_url_map = []
        if author_desc_url:
            for x in author_desc_url:
                author_desc_url_listed = x.get('href')
                author_desc_url_map.append(author_desc_url_listed)
        # add into db
        print (bcolors.WARNING + author_name + bcolors.ENDC)
        listeA = {}
        listeA['name'] = author_name
        listeA['url'] = author_url
        listeA['rank'] = author_rank
        listeA['desc'] = author_desc
        extracted_info.update(listeA)                
        # Goto extract user inf
        data = host + author_url
        ## Uncomment if wanna add on loop data save
        # json_save(extracted_info)

## First Crawl
def extract_links(html):
    # print(bcolors.WARNING + bcolors.BOLD + 'GO extraction data from : '+ bcolors.FAIL + artist_name + bcolors.ENDC)
    soup = BeautifulSoup(html, 'lxml')
    html_body = soup.find_all('div', {'class' : 'body'})
    extracted_info = {}
    # surely not the most efficiency...
    dataTarget(html_body, extracted_info)
    # Get NextPage then download until none
    next_page = soup.find('a', {'title' : 'Go to next page'}).get('href')
    next_page_URL = host + next_page
    print(next_page_URL)
    while (next_page is not None):
        try:
            next_download = download(next_page_URL)
            soup = BeautifulSoup(next_download, 'lxml')
            next_page = soup.find('a', {'title' : 'Go to next page'}).get('href')
            next_page_URL = host + next_page
            html_body = soup.find_all('div', {'class' : 'body'})
            # reprise des data
            dataTarget(html_body, extracted_info)        
        except Exception as e:
            print('Erreur sur : ', e)
            return
    return extracted_info

## Second Crawl
def extract_users_info(html, dataObj):
    soup = BeautifulSoup(html, 'lxml')
    userInfoHTML = soup.find_all('div', {'class' : 'node'}) 
    userInfoStructured = {}
    listeB = {}
    try:
        for x in userInfoHTML:
            profile = x.find('table', {'class' : 'drupal-info'})
            hobbies = profile.find('th', text='Hobbies:')
            if hobbies:
                hobbies = hobbies.find_next('td').getText()
                listeB['hobbies'] = hobbies.strip('\r\n\t')
            group = profile.find('th', text='Group:')
            if group:
                groupURL = group.find_next('td').find('a').get('href')
                listeB['groupURL'] = groupURL
            dataObj['rank'] = dataObj['rank'].strip('\n\t')
            dataObj.update(listeB)
    except Exception as e:
        print('Erreur sur : ', e)
        return    
    return dataObj

if __name__ == '__main__':
    host = 'https://fold.it'
    indexUsers = '/portal/players/profs'
    dbBase = 'db/' 
    ## Uncomment if previous data else init 
    # userList = db + 'dataCompleteWithHomepage.json'
    # dataF = json.load(open(userList))
    getIndex = download(host + indexUsers)
    dataF = extract_links(getIndex)
    lastFile = db + 'dataLast.json'
    # Boucle par url d'utilisateur trouvé
    for userData in dataF:
        # Download, extract info and then save (or sort of...)
        userURL = host + userData['url']
        dataDownload = download(userURL)
        if dataDownload:
            dataComplete = extract_users_info(dataDownload, userData)
            if dataComplete:
                pprint.pprint(dataComplete)
                json_save(lastFile, dataComplete)
        else:
            json_save(lastFile, userData)
