
## "AI" (rename to "Wikipedia Answers")
Given a list of questions, googles the first Wikipedia article found for each and then returns the first 5 paragraphs of that article, then stores the results in a JSON file.

For gathering data for AI final project.
### `wiki.py`
Main (and simplest) file.

Usage: `usage: python wiki.py dataset_name range_1 range_2`

Where
* `dataset_name` is the name of the dataset used (a list of questions)
* `range_1` and `range_2` are the range of the indexes of the questions.

Inside the file, the `Question` class refers to just one question. Initializing it via `Question("your question")` immediately fetches the 5 paragraphs, which can then be accessed by the `.paragraphs` attribute.
Querying results of each question is also stored to a `log.txt` file.

### `wikisearch.py` and `wikisearch_careful.py`
These files don't use the `Question` class, run a multi-threaded version (using `Pool`), and uses the `wikipedia` API.

### `new_wiki.py`
This file uses the `wikipediaapi` module as well as the `Question` class.
