import requests, bs4, pandas as pd
import csv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import numpy as np

cid = 'aa0b0677b0a94e46ad76cf3ceb6875b0' #spotipy keys
secret = 'de8b878ba401409abbe23c5645a6a1da' 

client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)

sp = spotipy.Spotify(client_credentials_manager = client_credentials_manager)

def gettop40chartsongs(url): #function to webscrape from top 40 songs site
    allsongs = []
    print('Getting Page %s ' %url) #tracking which page it's on
    req = requests.get(url)
    req.raise_for_status()

    if req.status_code != 200:
        return None
    
    soup = bs4.BeautifulSoup(req.text, "lxml")

    sdate = soup.find_all("p", class_="article-date") #the scrapening commences
    date = sdate[0].text.split('-')[0]
    title = soup.find_all("div", class_="title")
    position = soup.find_all("span", class_="position")
    spotifylink = soup.find_all("a", class_="spotify")
    
    spotify = []

    for a in spotifylink: 
        spotify.append(a["href"])

    linkful_park = []

    for i in range (1,len(position)+1): #only include songs that have spotify links
        x = soup.find("tr", class_="actions-view actions-view-listen actions-view-listen-" + str(i))

        if x == None:
            continue
        else:
            y = x.find("a") 
            if len(y) == 1: #the first link in the tag exists
                if y.text == "spotify": #the first link is a spotify link
                    linkful_park.append(i)
    
    spotifyallweeks = []
    blankchecker = 0

    #make a list where each song with a spotify link is placed in the index equal to the position 
    #ranking of the song-1 and has its corresponding spotify link as its value
    #else the value is 0
    for i in range(1,len(linkful_park)+1): 
        if i == 1:
            if linkful_park[i-1] != 1: #edge case of 1st song and song(s) between 1st and the next song that has a link having no link
                    blankdiff = linkful_park[i-1] - 1
                    for u in range(blankdiff):
                        
                        spotifyallweeks.append(0)

                    spotifyallweeks.append(spotify[i-1])
                    blankchecker = 1
            elif linkful_park[i-1] == 1:
                spotifyallweeks.append(spotify[i-1])
        elif linkful_park[-i] == linkful_park[0]: #edge case of last song having no link
            if linkful_park[i-1] != len(position): 
                if linkful_park[i-1] != i+blankchecker: #edge edge case of song(s) between last song and the song previous that had a link having no link(s)
                    blankdiff = linkful_park[i-1]-linkful_park[i-2] -1
                    for g in range(blankdiff):
                    
                        spotifyallweeks.append(0)
                    spotifyallweeks.append(spotify[i-1])

                    enddiff = len(position) - linkful_park[i-1]
                    
                    for l in range (enddiff):
                        spotifyallweeks.append(0)
                elif linkful_park[i-1] == i+blankchecker:
                    spotifyallweeks.append(spotify[i-1])

                    enddiff = len(position) - linkful_park[i-1]
                    
                    for l in range (enddiff):
                        spotifyallweeks.append(0)

            elif linkful_park[i-1] == len(position): 
                blankdiff = linkful_park[i-1]-linkful_park[i-2] -1
                for g in range(blankdiff):
                    spotifyallweeks.append(0)
                spotifyallweeks.append(spotify[i-1])
        elif linkful_park[i-1] != i+blankchecker: #check if current index of song+1 in position ranking doesn't have a link
            blankdiff = linkful_park[i-1]-linkful_park[i-2] -1
            blankchecker = blankchecker+blankdiff
            for j in range(blankdiff):
                spotifyallweeks.append(0)
            spotifyallweeks.append(spotify[i-1])
        elif linkful_park[i-1] == i+blankchecker: 
            spotifyallweeks.append(spotify[i-1])
    for i in linkful_park: #move all the data for a song into a list and then into another list with each song's data stored as a list for each index
        Topfortyweeklysongs = []
        Topfortyweeklysongs.append(date.strip('\r').strip('\n').strip(' '))
        Topfortyweeklysongs.append(i)
        Topfortyweeklysongs.append(title[i-1].text.strip('\r').strip('\n').strip(' '))
        Topfortyweeklysongs.append(spotifyallweeks[i-1].strip('\r').strip('\n').strip(' '))
        allsongs.append(Topfortyweeklysongs)

    print(allsongs)

    prevlink = soup.find("a", class_="prev chart-date-directions") #change the link to the previous page/week
    if prevlink["href"] == "/charts/uk-top-40-singles-chart/20000227/750140":
        return None
    link = prevlink["href"]
    link = "http://www.officialcharts.com/" + link

    with open("output4.csv", 'a', newline='') as resultFile: #move the list to a csv file format with each song as a row
        wr = csv.writer(resultFile)
        wr.writerows(allsongs)
        resultFile.close()
    
    allsongs = []
    gettop40chartsongs(link)

gettop40chartsongs() #starting function

songs = pd.read_csv("output4.csv") #import the csv file with the data to clean it a bit and add time length

uniqsongs = songs.drop_duplicates(subset=['title']) #only unique songs need be considered

uniqurl = uniqsongs['spotifylink']

uniqurllist = uniqurl.tolist()

time = []

print(len(uniqurllist))

indexlist = []

for i in range(len(uniqurllist)): #access song time length info through spotipy library

    songtime = (sp.audio_features(uniqurllist[i])[0]["duration_ms"])
    time.append(songtime)
    indexlist.append(i)
    print(i)

uniqsongsdf = uniqsongs.assign(Time = time) #make a new dataframe with an added column for the song time length

uniqsongsdf.insert(0,"newindex", indexlist) #make a new index to refer to in case its needed

uniqsongsdf.to_csv('output5.csv') #final csv output







