import bs4 as bs
import urllib.request
import re
import pandas as pd


#The IMDB list used to generate this data set is called "The Top 2000 Male Action Stars," and can be found at https://www.imdb.com/list/ls059545729/
#The list includes actors that primarily star in action movies, consists of 17 pages, and encompasses nearly 100 years of cinema.
#Before delving into the mechanics of the script it is important for one to first examine how the list and its constituent pages are set up, as well as the structure of the URLs of the actors' pages
#***In particular, the links provided in this list lead to a partial bio of each actor. To get the actual data we want, we must further traverse to their full bio page. We can easily access the
#   full bio page using apriori knowledge of the structure of the full bio URL and information from their partial bio url***
#This script extracts the data by:
#   1. beginning with the first page, creating a soup object to represent the elements of the given page
#   2. using the soup object, make a list containing the urls to the actors' partial bio pages
#   3. creating a list of the actual, full bio URLs from the partial bio URLs

def getHeight():
    #load html code from a url
    page = urllib.request.urlopen("https://www.imdb.com/name/nm0000078/bio?ref_=nm_ov_bio_sm")
    #makes a soup object with the html page as parameter
    soup = bs.BeautifulSoup(page)
    #findAll() returns a list of all <td> tags
    tdata = soup.body.findAll("td")
    #using regex to find the height entry/cell/ findall() of regex library also returns a list
    height_entry = re.findall("\n[0-9]'\s[0-9]", str(tdata))
    #converts the list containing height into a string so taht we may parse it
    data_string = height_entry[0]

    feet = data_string[1]
    inches = data_string[4]
    height = [feet, inches]
    return height


#create an index i to facilitate looping through the 17 pages of actor bio links
i = 1
#create a list to hold links to actors
actors = []
#create a variable for current page of actors and set it to the first page
actors_page = urllib.request.urlopen("https://www.imdb.com/list/ls059545729/")
#create the base url that subsequent pages will use
fragment1 = "https://www.imdb.com"
while i < 18:
    print(i)
    #create beautiful soup object with current page of actors
    soup = bs.BeautifulSoup(actors_page, features="html.parser")
    #add html elements containing links to actors' bios to the list
    actors = actors + soup.body.findAll("h3")
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

#we now possess a list of tags containing links to each actor's bio page. however, these links only
#lead to a partial bio. fortunately each has a link to the full bio nested inside

#we now want to extract the urls to the actors' full pages from each partial bio page
#regex the list of actor's partial bios anchor elements
partial_bio_urls = re.findall("/name/nm[\\d]{7}", str(actors))
#append the above fragments with "http://imdb.com" to obtain full URL
complete_partial_bio_urls = []
for x in partial_bio_urls:
    complete_partial_bio_urls.append(fragment1 + x)

#great, now we can access the partial bios
#let's do this and grab the full bio URls
current_partial_bio = ""
full_bio_links = []
for x in complete_partial_bio_urls:
    current_partial_bio_page = urllib.request.urlopen(x)
    soup = bs.BeautifulSoup(current_partial_bio_page, features="html.parser")
    anchors = soup.findAll("a")
    full_bio_url = re.findall("/name/nm[\\d]{7}/bio.*, str(anchors))
    full_bio_links.append(full_bio_url)
print(full_bio_links)



#<a href="/name/nm0001526/bio?ref_=nm_ov_bio_sm">See full bio</a>
#


