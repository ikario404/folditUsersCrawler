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
    # session = requests.Session()
    # session.mount("http://", requests.adapters.HTTPAdapter(max_retries=1))
    # headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'}
    # connect_timeout = 0.0001
    response = requests.get(url, timeout=None)
    # time.sleep(2)
    errorList = []
    errorFile = 'errorDB.json'
    if response.status_code == 200:
        return response.text
    else:
        print('error on :', response.status_code)
        errorList.append(url)
        json_save(errorFile, errorList)
        return 

# JSON saving
def json_save(filename, data):
    with open(filename, 'a') as data_file:
        # output.update(data)
        json.dump(data, data_file)
        # json.dump(data, data_file, indent=4)

## First Crawl
def extract_links(html):
    # print(bcolors.WARNING + bcolors.BOLD + 'GO extraction data from : '+ bcolors.FAIL + artist_name + bcolors.ENDC)
    soup = BeautifulSoup(html, 'lxml')
    listLink = soup.find_all('div', {'class' : 'body'})
    all_link = {}
    
    for x in listLink:
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

        print (bcolors.WARNING + author_name + bcolors.ENDC)
        listeA = {}
        listeA['name'] = author_name
        listeA['url'] = author_url
        print(author_url)
        listeA['rank'] = author_rank
        listeA['desc'] = author_desc
        all_link.update(listeA)
        
        # Goto extract user inf
        data = host + author_url
        print(data)
        json_save(all_link)

    next_page = soup.find('a', {'title' : 'Go to next page'}).get('href')
    next_page_URL = host + next_page
    print(next_page_URL)

    while (next_page is not None):
        try:
            # Download until...
            next_download = download(next_page_URL)
            soup = BeautifulSoup(next_download, 'lxml')
            next_page = soup.find('a', {'title' : 'Go to next page'}).get('href')
            next_page_URL = host + next_page
            listLink = soup.find_all('div', {'class' : 'body'})

            # reprise de la boucle
            for x in listLink:
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

                # add as data
                print (bcolors.WARNING + author_name + bcolors.ENDC)
                listeA = {}
                listeA['name'] = author_name
                listeA['url'] = author_url
                listeA['rank'] = author_rank
                listeA['desc'] = author_desc
                all_link.update(listeA)
                
                # Goto extract user inf
                data = host + author_url
                print(data)
                json_save(all_link)
                
        except AttributeError:
            print('Fin de boucle !')
            break

    return all_link

## Second Crawl
def extract_users_info(html, dataObj):
    soup = BeautifulSoup(html, 'lxml')
    userInfoHTML = soup.find_all('div', {'class' : 'node'}) 
    userInfoStructured = {}
    listeB = {}
    print(dataObj['desc'])
    try:
        for x in userInfoHTML:
            profile = x.find('table', {'class' : 'drupal-info'})
            # Here start tha game
            location = profile.find('th', text='Location:')
            if location:
                location = location.find_next('td').getText()
                listeB['location'] = location
            startedFolding = profile.find('th', text='Started Folding:')
            if startedFolding:
                startedFolding = startedFolding.find_next('td').getText()
                listeB['startedFolding'] = startedFolding
            links = profile.find('th', text='About me:').find_next('td').find_all('a', href=True)
            if links:
                # links = links.find_next('td').find_all('a', href=True)
                linksData = []
                for l in links:
                    link = l.get('href') 
                    linksData.append(link)
                listeB['aboutMe'] = linksData
            hobbies = profile.find('th', text='Hobbies:')
            if hobbies:
                hobbies = hobbies.find_next('td').getText()
                listeB['hobbies'] = hobbies
            group = profile.find('th', text='Group:')
            if group:
                group = group.find_next('td').getText()
                listeB['group'] = group
            dataObj.update(listeB)
    except Exception as e:
        print('Fin de boucle : ', e.message)
        return
    return dataObj

if __name__ == '__main__':
    host = 'https://fold.it'
    userList = 'result.json'
    lastFile = 'dataComplete.json'
    dataF = json.load(open(userList))

    for userData in dataF:
        # print(host + userData['url'])
        userURL = host + userData['url']
        # userData['rank'] = userData['rank'].translate(str.maketrans("\n\t\r", " "))
        # userDesc['desc'] = userData['desc'].translate(str.maketrans("\n\t\r", " "))
        dataDownload = download(userURL)
        if dataDownload:
            dataComplete = extract_users_info(dataDownload, userData)
            pprint.pprint(dataComplete)
            json_save(lastFile, dataComplete)
        else:
            json_save(lastFile, userData)