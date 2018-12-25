import wikipedia
import json, re
from sys import argv
from multiprocessing import Pool
from pprint import pprint


if len(argv) != 4:
	print("usage: py wikisearch.py [dataset_name] [range_1] [range_2]")
	exit(0)

dataset_name = argv[1]
range_1 = int(argv[2])
range_2 = int(argv[3])

JSON_FILENAME = "mapping_{}_{}_{}.json".format(dataset_name, range_1, range_2)
JSON_TEMP_FILENAME = "temp_{}".format(JSON_FILENAME)
tempfile = open(JSON_TEMP_FILENAME, "w")
logfile = open("log_{}.txt".format(argv[0]), "w")


## THIS IS THE POLICY 
def get_five_paragraphs(contents: list, answers: list): # a list of pages to search
	content_list = [content.split("\n") for content in contents] # split pages by lines
	filtered_list = [list(filter(lambda x: x != "" and "=" not in x, content)) for content in content_list] # remove invalid lines
	return_list = []
	for page in filtered_list:
		for paragraph in page:
			if any([re.search(ans, paragraph) for ans in answers]):
				return_list.append(paragraph)
				if (len(return_list) >= 5): break
	return return_list

def get_paragraphs(question: str, answers: list):
	search_results = wikipedia.search(question, results=10)
	if (search_results is None): print("couldn't find results!"); return None
	page_list = [wikipedia.WikipediaPage(title=target) for target in search_results]
	content_list = [page.content for page in page_list]
	return get_five_paragraphs(content_list, answers)
## ^^ END OF POLICY

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
		paragraphs = get_paragraphs(entry["question"], entry["answers"])
		if paragraphs:
			dic = {"question": entry["question"], "answers": entry["answers"], "paragraphs" : paragraphs}
			json.dump(dic, tempfile, indent=4)
			if (len(paragraphs) == 5):
				logprint("question |{}...|: success".format(entry["question"][0:20]))
			else:
				logprint("question |{}...|: success (missing some paragraphs)".format(entry["question"][0:20]))
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
	big_list = run_job(the_list, 16)
	final_list = list(filter(lambda x: x != {}, big_list))
	dump_to_json(final_list, JSON_FILENAME)
	print("final tally: {}/{}".format(len(final_list), len(the_list)))
	print("Job successful!")