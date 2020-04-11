import requests
from bs4 import BeautifulSoup
import os, json

base_url = "http://api.genius.com"
headers = {'Authorization': 'Bearer GENIUS_API_BEARER_STRING'}

artist_names = ["Fleet Foxes"]

def artist_id_from_song_api_path(song_api_path, artist_name):
  song_url =  base_url + song_api_path
  response = requests.get(song_url, headers=headers)
  json = response.json()
  artist = json["response"]["song"]["primary_artist"]
  if artist["name"] == artist_name:
    return artist["api_path"]
  else:
    return None

def songs_from_artist_api_path(artist_api_path):
  api_paths = []
  artist_url = base_url + artist_api_path + "/songs"
  data = {"per_page": 50}
  while True:
    response = requests.get(artist_url, data=data, headers=headers)
    json = response.json()
    songs = json["response"]["songs"]
    for song in songs:
      api_paths.append(song["api_path"])
    if len(songs) < 50:
      break #no more songs for artist
    else:
      if "page" in data:
        data["page"] = data["page"] + 1
      else:
        data["page"] = 1
  return list(set(api_paths))

def info_from_song_api_path(song_api_path):
  song_url =  base_url + song_api_path
  response = requests.get(song_url, headers=headers)
  json = response.json()
  return json

def lyrics_from_song_web_path(song_web_path):
  #gotta go regular scraping... come on Genius
  page_url = "http://genius.com" + song_web_path
  page = requests.get(page_url)
  html = BeautifulSoup(page.text, "html.parser")
  [h.extract() for h in html('script')]
  lyrics = html.find("lyrics").get_text()
  return clean_lyrics(lyrics)

def song_ids_already_scraped(artist_folder_path, force=False):
  #check for ids already scraped so we don't redo
  if force:
    return []
  song_ids = []
  files = os.listdir(artist_folder_path)
  for file_name in files:
    dot_split = file_name.split('.')
    #sometimes the file is empty, we don't want to include if that's the case
    if dot_split[1] == 'txt':
      try:
        song_id = dot_split[0].split("_")[-1]
        if os.path.getsize(artist_folder_path + '/' + file_name) != 0:
          song_ids.append(song_id)
      except:
        pass
  return song_ids

def clean_lyrics(lyrics):
  lyrics = lyrics.replace(u"\u2019", "'") #right quotation mark
  lyrics = lyrics.replace(u"\u2018", "'") #left quotation mark
  lyrics = lyrics.replace(u"\u02bc", "'") #a with dots on top
  lyrics = lyrics.replace(u"\xe9", "e") #e with an accent
  lyrics = lyrics.replace(u"\xe8", "e") #e with an backwards accent
  lyrics = lyrics.replace(u"\xe0", "a") #a with an accent
  lyrics = lyrics.replace(u"\u2026", "...") #ellipsis apparently
  lyrics = lyrics.replace(u"\u2012", "-") #hyphen or dash
  lyrics = lyrics.replace(u"\u2013", "-") #other type of hyphen or dash
  lyrics = lyrics.replace(u"\u2014", "-") #other type of hyphen or dash
  lyrics = lyrics.replace(u"\u201c", '"') #left double quote
  lyrics = lyrics.replace(u"\u201d", '"') #right double quote
  lyrics = lyrics.replace(u"\u200b", ' ') #zero width space ?
  lyrics = lyrics.replace(u"\x92", "'") #different quote
  lyrics = lyrics.replace(u"\x91", "'") #still different quote
  lyrics = lyrics.replace(u"\xf1", "n") #n with tilde!
  lyrics = lyrics.replace(u"\xed", "i") #i with accent
  lyrics = lyrics.replace(u"\xe1", "a") #a with accent
  lyrics = lyrics.replace(u"\xea", "e") #e with circumflex
  lyrics = lyrics.replace(u"\xf3", "o") #o with accent
  lyrics = lyrics.replace(u"\xb4", "") #just an accent, so remove
  lyrics = lyrics.replace(u"\xeb", "e") #e with dots on top
  lyrics = lyrics.replace(u"\xe4", "a") #a with dots on top
  lyrics = lyrics.replace(u"\xe7", "c") #c with squigly bottom
  return lyrics

if __name__ == "__main__":
  for artist_name in artist_names:
    #setting up path to artist's directories
    artist_folder_path = "artists/%s" % artist_name
    artist_lyrics_path = "%s/lyrics" % artist_folder_path
    artist_info_path = "%s/info" % artist_folder_path
    if not os.path.exists(artist_folder_path):
      os.makedirs(artist_folder_path)
    if not os.path.exists(artist_lyrics_path):
      os.makedirs(artist_lyrics_path)
    if not os.path.exists(artist_info_path):
      os.makedirs(artist_info_path)

    #only using lyrics since they're saved second
    prev_song_ids = song_ids_already_scraped(artist_lyrics_path)

    #find the artist!
    search_url = base_url + "/search"
    data = {'q': artist_name}
    response = requests.get(search_url, data=data, headers=headers)
    artist_info = response.json()
    for hit in artist_info["response"]["hits"]:
      song_api_path = hit["result"]["api_path"]
      artist_api_path = artist_id_from_song_api_path(song_api_path, artist_name)
      if artist_api_path: #done searching if we found the guy
        break

    if not artist_api_path:
      print "Could not find %s" % artist_name

    #find the song api ids for the artist
    song_api_paths = songs_from_artist_api_path(artist_api_path)

    #print out how many songs we have left
    print len(song_api_paths) - len(prev_song_ids)

    for song_api_path in song_api_paths:
      api_id = song_api_path.split('/')[2]
      if api_id in prev_song_ids:
        continue #don't redo
      full_song_info = info_from_song_api_path(song_api_path)
      song_title = full_song_info["response"]["song"]["title"]
      song_title_path = song_title.replace('/', '_')#.replace(' ', '_').lower()
      song_web_path = full_song_info["response"]["song"]["path"]

      lyrics = lyrics_from_song_web_path(song_web_path)

      lyric_path = "%s/lyrics/%s.txt" % (artist_folder_path, song_title_path)
      info_path = "%s/info/%s.txt" % (artist_folder_path, song_title_path)
      #import pdb;pdb.set_trace()

      #for record keeping purposes
      #print (artist_folder_path, song_title_path, api_id)
      print lyric_path

      with open(info_path, "w") as lfile:
        lfile.write(json.dumps(full_song_info))
      with open(lyric_path, "w") as ifile:
        try:
          ifile.write(lyrics)
        except UnicodeEncodeError as error:
          print error
