## Simple python crawler to extract some informations on fold.it 

Actually only work on users with profiles:  

```
python foldit_extractProfiles.py
```

Will give it in a file something like:
```JSON
[{
    "url": "",
    "name": "",
    "location": "",
    "homepage": "",
    "hobbies": "",
    "desc" :"",
    "linksDesc": "",
    "rank" :"",
    "startedFolding": "",
    "group": "",
    "groupURL": ""
}]
```
Probably lot of thing to optimize or extend...  
Work with BeautifulSoup, requets, lxml, json, pprint.