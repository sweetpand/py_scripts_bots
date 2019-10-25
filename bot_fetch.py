#!/usr/bin/python
# -*- coding: utf-8 -*-

import os 
import praw
import config
import re 
import requests
import time
import json 
import random 

def get_reddit():
	print("Logging in ..")
	r = praw.Reddit(username = config.username,
		            password = config.password,
		            client_id = config.client_id,
		            client_secret = config.client_secret,
		            user_agent = "wholesome bot v1.0 by /u/harshi_bar")
	print("Logged in!")

	return r 

def json_dump_and_parse(file_name, request):
	with open(file_name, "w+") as f:
		json.dump(request.json(), f, sort_keys = True, ensure_ascii = False, indent = 4)
	with open(file_name) as f:
		data = json.load(f)
	return data


def reply_to_comment(r, comment_id, comment_reply, comment_subreddit, comment_author, comment_body):
	try:
		comment_to_be_replied_to = r.comment(id=comment_id)
		comment_to_be_replied_to.reply(common_reply)
		print(f"\nReply detailss:\nSubreddit: r/{comment_subreddit}\nComment:\"{comment_body}\"\nUser: u/{comment_author}\a")

	except Exception as e:
		time_remaining = 15
		if (str(e).split()[0] == "RATELIMIT:"):
			for i in str(e).split():
				if (i.isdigit()):
					time_remaining = init(i)
					break

			if (not "seconds" or not "second" in str(e).split()):
				time_remaining *= 60

		print(str(e.__class__.__name__) + ":" + str(e))
		for i in range(time_remaining, 0, -5):
			print ("Retrying in", i, "seconds..")
			time.sleep(5)


def help_human(feeling, response_data):
	random_response = random.choice(response_data[feeling])
	if feeling in ['validate', 'joke', 'love']:
		return random_response

	if feeling == 'hug':
		return f"hey bud, let me give you a [hug]({random_response})!! 🤗"

	random_feeling = random.choice(['sad', 'joke', 'love'])
	if feeling == 'joke':
		random_joke = random.choice(response_data['joke'])
		return f'Hey! Maybe a joke will make you feel better.\n\n{random_joke}'
    if feeling == 'love':
    	random_pickupline = random.choice(response_data['love'])
    	return f'How bout a rose 🌹? No? Well...\n\n{random_pickupline}'
    else:
    	return random_response 


def run(r, response_data):

	last_utc = 0

	with open("utc.txt", "r") as f:
		last_utc = f.read().split("\n")[-1]

	try:
		comment_url = r"https://api.pushshift.io/reddit/search/comment/?q=my\\_friendly\\_bot&sort=desc&size=50&fields=author,body,created_utc,id,subreddit&after=" + last_utc
		parsed_comment_json = json_dump_and_parse("comment_data.json", requests.get(comment_url))

		comment_url2 = r"https://api.pushshift.io/reddit/search/comment/?q=my_friendly_bot&sort=desc&size=50&fields=author,body,created_utc,id,subreddit&after=" + last_utc
		parsed_comment_json2 = json_dump_and_parse("comment_data2.json", requests.get(comment_url2))

		if (len(parsed_comment_json["data"]) == 0):
			last_utc = parsed_comment_json2["data"][0]["created_utc"]
		elif (len(parsed_commet_json2["data"]) == 0):
			last_utc = parsed_comment_json["data"][0]["created_utc"]
		else:
			last_utc = max(parsed_comment_json["data"][0]["created_utc"],parsed_comment_json2["data"][0]["created_utc"])

		parsed_comment_json["data"].extend(parsed_comment_json2["data"])


		with open("utc.txt", "w") as f:
			f.write(str(last_utc))

		for comment in parsed_comment_json["data"]:

			comment_author = comment["author"]
			comment_body = comment["body"]
			comment_id = comment["id"]
            comment_subreddit = comment["subreddit"]
            comment_reply = ""


        if (("my\_friendly\_bot" in comment_body.lower() or "my_friendly_bot" in comment_body.lower()) and comment_author != "my_friendly_bot"):
            print ("\n\nFound a comment!")
            message = re.search("(i\'m)( *)(\w*)(,*)( *)my[\\\]?_friendly[\\\]?_bot",comment_body, re.IGNORECASE)
            
            if message:
            	message = message.group(3).lower()

        	if message == 'smart':
        		comment_reply = help_human('validate', response_data)
    		elif message == "sad":
    			comment_reply = help_human('sad', response_data)
			elif message == 'lonely':
				comment_reply = help_human('hug', response_data)
			elif message == 'bored':
				comment_reply = help_human('joke', response_data)
            elif message == 'single':
            	comment_reply = help_human('love', response_data)
        	else:
        		comment_reply = f"hey there, {comment_author}. I hope you have a great day!! 😊"


		comment_reply += ("\n\n\n\n---\n\n^(Beep beep, your neighborhood friendly bot here. If there are any issues, contact my) [^Creator](https://www.reddit.com/message/compose/?to=harshi_bar&subject=/u/my_friendly_bot). ^(I've been adapted from my cousin, Wordbook_Bot: ) [^GitHub ](https://github.com/kylelobo/Reddit-Bot)")
        print(comment_body, comment_reply)
        reply_to_comment(r, comment_id, comment_reply, comment_subreddit, comment_author, comment_body)

     
        print ("\nFetching comments..")


        except Exception as e:
            print (str(e.__class__.__name__) + ": " + str(e))

     	return str(last_utc)

if __name__ == "__main__":
	reddit = get_reddit()
	redit_data = {}

	with open('responses.json', 'r') as json_file:
		response_data = json.load(json_file)


	run(reddit, response_data)


