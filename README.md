# Movie Search Engine

This project was made for Information Retrieval course.


## Part 1: Crawler

Built with [Scrapy](http://scrapy.org/).
The cralwer contains a spider to crawl and retrieve movies information from [Torec](http://torec.net)

The initial website the crawler starts from is the movies listing first page - http://www.torec.net/movies_subs.asp?p=1
Then it opens multithreads to retrieve each movie in this page (aprx 12 movies), once its finished the crawler paginating to the next page

The output of the crawler is list of documents named with the movie id.
Each document contains its movie description
While exporting  data, theres an index file contains all other data reffered to the spicfic movie.

e.g - movies 1,2:
files will be: 1, 2, index.csv
where 1,2 will hold the movie description
and index.csv will hold all other information such as Rating, Movie name, Actors, Release date and etc.

## Part 2: Files proccessing and Counting

This part will process each movie's description and will create a frenquency file to hold each movie's description words TF-IDF
Relevant files:   createFrequency.py

In the first stage: the DBIndexer initialise all files to process,

in step_1() function it first count the term's frequency for each word in each movie description

then in step_2() function it calculates the IDF and finished with a structur that holds words and thier TF-IDF


## Part 3: Evaluating, Search, Return

This part contains 2 options, search with **Cosine Similarity** and **BM25**

The user provide a query to search and the system will support this query in both CosineSimilarity and BM25 functions
Each movie in the result file will hold its meta data such as: serialNum, url, name_eng, length, year, imdb_score, download, RANK
 
While Rank is the evaluation for the **Cosine Similarity** or **BM25**

## Part 4: Tagging

TODO

## Part 5: Conclusions

As part of the course, we should estimate our search by planning a test to examine our Precision-Recall score
In order to do so: we will need to plan how should I calculate the Precision-Recall

The DB contains 8508 documents
Therefore, our maximum retrieved doc can be up to 8508 results.
we will search for a speicific genre - 'SCI-FI' while assuming:

1. we have 8508 documents
2. search conducted with 5000 documents
3. 1500 were relevant

Therefore:
```
X = Relevant documents retrieved =>  1500
Y = Relevant documents not retrieved => 8508 - 1500 = 7008
Z = Irrelevant documents retrieved => 5000 - 1500 = 3500
```
Equation ==>
```
Recall = (X / (X + Y)) * 100 => 1500/8508 * 100 = 17.63%
Precision = (X / (X + Z)) * 100 => 1500/5000 * 100 = 30%
```
