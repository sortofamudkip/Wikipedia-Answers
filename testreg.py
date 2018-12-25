import json, re

with open("curatedtrec/questions.json", "r") as f:
	meow = json.load(f)
	regex_str = meow[20]["answers"]
	print(regex_str)

for test in ["Japan", "Korea", "JJ", "___", "dd"]:
	if re.search(regex_str, test):
		print("match: {} vs {}".format(regex_str, test))
	else:
		print("no match: {} vs {}".format(regex_str, test))