from bs4 import BeautifulSoup
from pprint import pprint
import json, re
from requests import get, RequestException
from urllib.parse import unquote
from time import sleep
from random import uniform
from sys import argv

master_link = []

logfile = open("log.txt", "w")

if len(argv) != 4:
	print("usage: py wiki.py [dataset_name] [range_1] [range_2]")
	exit(0)

dataset_name = argv[1]
range_1 = int(argv[2])
range_2 = int(argv[3])


JSON_FILENAME = "mapping_{}_{}_{}.json".format(dataset_name, range_1, range_2)
JSON_TEMP_FILENAME = "temp_{}".format(JSON_FILENAME)
tempfile = open(JSON_TEMP_FILENAME, "w")

def logprint(s: str):
	print(s)
	logfile.write(s + "\n")

class Question:
	def __init__(self, question: str):
		self.question = question
		self.no_response = 0
		link = self.get_wiki_link(question)
		if link:
			self.wiki_link = unquote(unquote(link)) # remove encodings. Twice. Thanks google
			self.paragraphs = self.get_paragraphs(self.wiki_link)
			self.is_valid = True
		else:
			self.is_valid = False

	# These two functions are just for obtaining the HTML files.
	def is_good_response(self, resp):
	    content_type = resp.headers['Content-Type'].lower()
	    return (resp.status_code == 200 
	            and content_type is not None 
	            and content_type.find('html') > -1)

	def simple_get(self, url):
	    try:
	        with (get(url, stream=True)) as resp:
	        	return resp.content if self.is_good_response(resp) else None
	    except RequestException as e:
	        logprint('Error during requests to {0} : {1}'.format(url, str(e)))
	        return None

		
	def get_wiki_link(self, question: str):
		"""
			Searches Google for the question and returns the Wikipedia link.
		"""	
		google_format = "+".join(question.split())
		search_link = "https://www.google.com/search?q=" + google_format
		result = self.simple_get(search_link)
		if result is None:
			logprint("result is none!")
			self.no_response += 1
			if self.no_response >= 7:
				logprint("fatal error: ip probably blocked. Exiting.")
				dump_to_json(JSON_FILENAME)
				exit(0)
			else:
				return None
		soup = BeautifulSoup(result, 'html.parser')
		# links = soup.find_all(href=re.compile("en.wikipedia.org/wiki"))
		# if (len(links) == 0): # cannot find wiki link, just get the first link
		# 	logprint("warning: cannot find wiki link for question: {}".format(question))
		# 	try:
		# 		ugly_link = soup.find_all(class_ = "r")[0].a.attrs["href"]
		# 	except Exception as e:
		# 		logprint("\tSkipping this question!")
		# 		return None
		# 	# logprint("\tLink of find found: {}".format(ugly_link))
		# else:
		# 	ugly_link = links[0].attrs["href"] # always assume it's the first one; get just the link

		"""
		for wikimovies: just get the first link
		"""
		try:
			match = soup.find_all(class_ = "r")
			for m in match: # keep going through each match until a relevant one is found
				link = m.a.attrs["href"]
				regex_format = "\\+".join(question.split())
				if re.search(regex_format, link): 
					# logprint("matched!")
					continue # try another one if this is a bad link
				else: 
					match = re.match(r"/url\?q=(.*?)&", link) # extract wikipedia link from the mess
					return match.group(1)
		except (AttributeError, TypeError) as e:
			logprint("error:", e)
			logprint("-------")
			match = soup.find_all(class_ = "r"); pprint("match: |{}|".format(match))
			match_0 = match[0]; pprint("match[0]: |{}|".format(match_0))
			link = match_0.a; pprint("link: |{}|".format(link))
			pprint("vars(link):", vars(link))
			pprint("attrs: ", link.attrs)
			logprint("-------")
			return None
	def get_paragraphs(self, link: str):
		# enter wikipedia link, get first 5 paragraphs.
		if link == None: return None
		contents = self.simple_get(link)
		if contents == None:
			return None
		soup = BeautifulSoup(contents, 'html.parser')
		paragraphs = soup.find_all("p", limit=200) # gets 20 paragraphs (the <p> tag; not really good for finding actual paragraphs)
		count = 0; plist = [] # stop at 5
		for p in paragraphs:
			stripped_p = p.get_text().strip()
			if stripped_p == "": continue
			if count >= 5: break
			count += 1
			plist.append(stripped_p)
		return plist


def get_questions(dirname: str) -> list:
	with open("{}/questions.txt".format(dirname), "r") as f:
		qlist = f.read().split("\n")
	return qlist

def get_q_a_map(dirname: str):
	with open("{}/questions.json".format(dirname), "r") as f:
		q_a_list = json.load(f)
	return q_a_list

def dump_to_json(fname: str):
	with open(fname, "w") as f:
		json.dump(master_link, f, indent=4)

# webqlist = get_questions("webquestions")
webq_alist = get_q_a_map(dataset_name)[range_1:range_2+1]  # 195:
# pprint(webq_alist); exit(0)


for i, entry in enumerate(webq_alist):
	q_i = i + range_1
	try:
		Q = Question(entry["question"])
		if Q.is_valid:
			dic = {"question": entry["question"], "answers": entry["answers"], "paragraphs" : Q.paragraphs}
			master_link.append(dic)
			json.dump(dic, tempfile)
			logprint("question {}: success".format(i))
		else: logprint("question {}: failure".format(i))
	except Exception as e:
		logprint("question {}: Problem found: |{}|\n\tSkipping this question.".format(i, e))
	sleep(uniform(0.3,1.5)) # google doesn't like scraping :(


dump_to_json(JSON_FILENAME)

# Q = Question("what is Natural Language Processing")
# for p in Q.paragraphs:
# 	logprint(p)


