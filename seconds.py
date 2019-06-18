import wikipedia
import json
from sys import argv
from time import sleep
from multiprocessing import Pool
from pprint import pprint

"""
The idea is:
 for each question:
 	search wikipedia
 	get 5 paragraphs
 	pack into json

"""

logfile = open("log_new.txt", "w")

if len(argv) != 4:
	print("usage: py wikisearch.py [dataset_name] [range_1] [range_2]")
	exit(0)

dataset_name = argv[1]
range_1 = int(argv[2])
range_2 = int(argv[3])

JSON_FILENAME = "mapping_{}_{}_{}.json".format(dataset_name, range_1, range_2)
JSON_TEMP_FILENAME = "temp_{}".format(JSON_FILENAME)
tempfile = open(JSON_TEMP_FILENAME, "w")

		


## THIS IS THE POLICY 
def get_five_paragraphs(contents: str):
	content_list = contents.split("\n")
	filtered_list = list(filter(lambda x: x != "" and "=" not in x, content_list))
	
	return filtered_list[0:5]

def get_paragraphs(question: str):
	search_results = wikipedia.search(question)
	if (search_results is None): print("couldn't find results!"); return None
	target = search_results[0]
	page = wikipedia.WikipediaPage(title=target)
	contents = page.content
	return get_five_paragraphs(contents)

def get_q_a_map(dirname: str):
	with open("{}/questions.json".format(dirname), "r") as f:
		q_a_list = json.load(f)
	return list(q_a_list)

def run_job(qlist, thread=4):
	pool = Pool(thread)
	results = pool.map(get_a_paragraph, qlist)
	pool.close(); pool.join()
	return results

def get_a_paragraph(entry):
	try:
		paragraphs = get_paragraphs(entry["question"])
		if paragraphs is not None:
			dic = {"question": entry["question"], "answers": entry["answers"], "paragraphs" : paragraphs}
			json.dump(dic, tempfile, indent=4)
			logprint("question |{}...|: success".format(entry["question"][0:20]))
			return dic
		else: 
			logprint("question |{}...|: failed".format(entry["question"][0:20]))
			return {}
	except Exception as e:
		logprint("question |{}...|: problem found, skipping question".format(entry["question"][0:20]))
		print("\tproblem: |{}|".format(e))
		return {}	

def logprint(s: str):
	print(s)
	logfile.write(s + "\n")


def dump_to_json(data: list, fname: str):
	with open(fname, "w") as f:
		json.dump(data, f, indent=8)

if __name__ == "__main__":
	webq_alist = get_q_a_map(dataset_name)
	the_list = webq_alist[range_1:min(range_2+1, len(webq_alist))] 
	big_list = run_job(the_list, 12)
	dump_to_json(big_list, JSON_FILENAME)
