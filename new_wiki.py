import wikipediaapi as w
from bs4 import BeautifulSoup
from pprint import pprint
from multiprocessing import Pool
import json, re
from requests import get, RequestException
from urllib.parse import unquote

class Question:
	def __init__(self, question: str):
		self.question = question
		link = self.get_wiki_link(question)
		if link:
			self.wiki_link = unquote(unquote(link)) # remove encodings. Twice. Thanks google
			self.paragraphs = self.get_paragraphs(self.wiki_link)
			self.is_valid = True
		else:
			self.is_valid = False
			self.wiki_link = ""
			self.paragraphs = []

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
	        print('Error during requests to {0} : {1}'.format(url, str(e)))
	        return None

		
	def get_wiki_link(self, question: str):
		"""
			Searches Google for the question and returns the Wikipedia link.
		"""	
		google_format = "+".join(question.split())
		search_link = "https://www.google.com/search?q=" + google_format
		result = self.simple_get(search_link)
		soup = BeautifulSoup(result, 'html.parser')
		links = soup.find_all(href=re.compile("en.wikipedia.org/wiki"))
		if (len(links) == 0): # cannot find wiki link, just get the first link
			print("warning: cannot find wiki link for question: {}".format(question))
			try:
				ugly_link = soup.find_all(class_ = "r")[0].a.attrs["href"]
			except Exception as e:
				print("\tSkipping this question!")
				return None
			# print("\tLink of find found: {}".format(ugly_link))
		else:
			ugly_link = links[0].attrs["href"] # always assume it's the first one; get just the link
		match = re.match(r"/url\?q=(.*?)&", ugly_link) # extract wikipedia link from the mess
		return match.group(1)

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

def get_q_a_map(dirname: str) -> list:
	with open("{}/questions.json".format(dirname), "r") as f:
		q_a_list = json.load(f)
	return q_a_list

def get_a_paragraph(entry):
	try:
		print("trying question: |{}|".format(entry["question"]))
		Q = Question(entry["question"])
		if Q.is_valid:
			return {"question": entry["question"], "answers": entry["answers"], "paragraphs" : Q.paragraphs}
		else: 
			return {}
	except Exception as e:
		print("Problem found!! Skipping this question.")
		print("\tproblem: |{}|".format(e))
		return {}	

def run_job(qlist, thread=12):
	pool = Pool(thread)
	results = pool.map(get_a_paragraph, qlist)
	pool.close(); pool.join()
	return results

if __name__ == "__main__":
	# webq_alist = get_q_a_map("wikimovies")
	webq_alist = get_q_a_map("wikimovies")[194:]
	# print(webq_alist); exit(0)
	big_list = run_job(webq_alist, 4)

	with open("mapping_wikimovies_2.json", "w") as f:
		json.dump(big_list, f, indent=4)

	# from time import sleep
	# sleep(20) 

	# webq_alist = get_q_a_map("curatedtrec")
	# # print(webq_alist); exit(0)
	# big_list = run_job(webq_alist, 4)

	# with open("mapping_curatedtrec.json", "w") as f:
	# 	json.dump(big_list, f, indent=4)

	# print("done!")