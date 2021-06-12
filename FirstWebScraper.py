import bs4 as bs
import urllib.request
import re
import pandas as pd
import numpy as np


#The IMDB list used to generate this data set is called "The Top 2000 Male Action Stars," and can be found at https://www.imdb.com/list/ls059545729/
#The list includes actors that primarily star in action movies, consists of 17 pages, and encompasses nearly 100 years of cinema.
#Before delving into the mechanics of the script it is important for one to first examine how the list and its constituent pages are set up, as well as the structure of the URLs of the actors' pages
#***In particular, the links provided in this list lead to a partial bio of each actor. To get the actual data we want, we must access their full bio page. We can achieve this
#   using a piece of the partial bio URL, and apriori knowledge of the structure of the full bio URL***
#This script extracts the data by:
#   1. beginning with the first page, creating a soup object to represent the elements of the given page
#   2. using the soup object, scrape the partial bio URL for each actor
#   3. creating a list of the actual, full bio URLs constructed from the partial bio URLs
#   4. iterate through the list of full bio URLs lifting the data we want

#create an index i to facilitate looping through the 17 pages of actors
i = 1
#create a list to hold partial bio URLs
actors = []
#create a variable for current page of actors and set it to the first page
actors_page = urllib.request.urlopen("https://www.imdb.com/list/ls059545729/")
#create the base url that subsequent pages will use (both pages of the list and each individual actor's full bio page)
fragment1 = "https://www.imdb.com"
#this is no typo; I named it fragment 3 because it is appended to the end of the final, full actor bio URL
fragment3 = "/bio?ref_=nm_ov_bio_sm"
while i < 18:
    print(i)
    #create beautiful soup object with current page of actors
    soup = bs.BeautifulSoup(actors_page, features="html.parser")
    #add html elements containing links to actors' partial bios to the list
    actors = actors + soup.body.findAll("h3")
    #we now have all of the elements containing our actors' links for this page; now we must get the link to the next page of actors
    #make a list of all URLs on the page
    anchors = soup.findAll("a")
    if(i == 17):
        i = i + 1
        continue
    #find the url for the next page
    next_page_anchor = re.findall("class=\"flat-button lister-page-next next-page\" href=.*", str(anchors))
    #split string containing the url to extract it
    broken_anchor = re.split("\"", next_page_anchor[0], 0, 0)
    #create target url using the base fragment with part we just extracted
    next_url = fragment1 + broken_anchor[3]
    actors_page = urllib.request.urlopen(next_url)
    i = i + 1

#We now possess a list of tags containing links to each actor's partial bio page. we could traverse the partial bio pages to access the full bio page for each actor, but it will actually save
#   much more time and resources to construct the URLs ourselves

#regex the list of actors' partial bio anchor elements
partial_bio_urls = re.findall("/name/nm[\\d]{7}", str(actors))
#append the above fragments with "http://imdb.com" and "bio?ref_=nm_ov_bio_sm" to obtain URL for full bio
complete_full_bio_urls = []
for x in partial_bio_urls:
    complete_full_bio_urls.append(fragment1 + x + fragment3)

heights = []
i = 1
for x in complete_full_bio_urls:
    feet = inches = '0'
    #load html code from a url
    page = urllib.request.urlopen(x)
    #makes a soup object with the html page as parameter
    soup = bs.BeautifulSoup(page, features="html.parser")
    #findAll() returns a list of all <td> tags
    tdata = soup.body.findAll("td")
    #using regex to find the height entry/cell/ findall() of regex library also returns a list
    height_entry = re.findall("\n[0-9]'\s[0-9]?[0-9]?", str(tdata))
    #checks if list is non-empty and makes a string variable for height if so
    if height_entry:
        data_string = height_entry[0]
    else:
        continue

    data_string = data_string.strip("\n")

    feet = data_string[0]

    if len(data_string) > 3:
        inches = data_string[3]
    if len(data_string) > 4:
        inches = inches + data_string[4]
    height = [feet, inches]
    heights.append(height)
    print(str(i) + ": " + str(height))

    i = i + 1

heights_in_inches = []
for x in heights:
        heights_in_inches.append(int(x[0]) * 12 + int(x[1]))

df = pd.DataFrame(heights_in_inches)
df.to_csv("heights.csv", index=False)

print(df.describe())