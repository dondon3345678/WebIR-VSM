# WebIR-VSM
My search engine implemented by Vector Space Model and Rocchio Feedback. This implementation achived 0.74349 MAP value on the given corpus.

## Preprocess
* file-list : Each line is a file path to every document.
* vocab.all : First line is the encoding format of this file, followed by terms in this collection. Index of each term is its *row number - 1*

```
utf-8
apple
bannan
cat
``` 
* inverted-file : vocab\_id and file\_id referred from *vocab.all* and *file-list*. vocab\_id\_1 vocab\_id\_2 denotes an unigram when vocab\_id\_2==-1 or a bigram when vocab\_id\_2!=-1. If there are N files containing vocab\_id\_1 vocab\_id\_2, there will be the number N next to vocab\_id\_2, followed by **N lines** that display the counts of this term in each file.

## IO
Input file is a ```query.xml``` in the following format.

```
<number> : The topic number.<title>: The topic title.<question>: A short description about the query topic.<narrative>: Even more verbose descriptions about the topic.<concepts>: A set of keywords that can be used in retrieval about the topic
```

Output file is a ```result.csv```, every line is query\_id,retrieved\_docs, like 

```
011,doc1,doc3,doc5
```

## Execution
```shell
execute.sh [-r] -i query-file -o output-file -m model-fir -d corpus-path

-r
	If specified, turn on relevance feedback.
-i
	query file follows the format above
-o
   output rank list
-m 
   a directory contains vocab.all,inverted-file,file-list
-d
	absolute path to the corpus directory
```