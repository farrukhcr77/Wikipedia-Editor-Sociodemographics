# wikipedia editor sociodemographics

Basic Requirements - **Python 3.5+**

Individual part requirements listed in respective directories

The folder **"Crawler for grabbing data"** has 2 folders "crawler" and "interpreter" that are used to crawl data from wikipedia english pages and store data in mongo db

The folder **"Grabbed Data from Wikipedia"** contains the bson and json files of the data grabbed from wikipedia.
In order to use the collections in mongoDb download the files from the link in txt file in folder "Grabbed Data from Wikipedia"
and perform a mongo restore.
It is necessary to download and perform a mongo restore as all the 3 methods mentioned below process data from the collections in the mongodb.

The folder **"Sociodemographics"** contains 3 major files each for different method

**1st method == > Direct Method**
file **directmethod.py**
  " this method uses a simple technique by first fetching data from the mongoDB database and compares the raw text with the bag of key         words such as gender, name , age locaton etc. that indicate a demographic character of editor."

file **directMeethodwithComparisonofWikipages.py**
  " does exactly the same thing as directmethod.py but also tells which page the editor has editted.
 Note: this method uses nltk and pymongo


**2nd Method ===> Name Based gender prediction method**
  file NameBasedGenderPrediction2.py
  " it fetches data from editor collection. for raw text provided by each editor it tokenizes each word and assigns parts of speech to the text. from the created list of words along with parts of speech it filters the list for proper nouns and then it compares the list of authors created from file name.csv. if proper noun matches the name in the list of author then the name and gener of the author is  displayed."
  "Note : remember to give the correct path for the name.csv file"
  Note: it uses nltk, numpy, pandas and pymogo
  

**3rd Method ===> Text Based Gender Prediction**
  file TextBasedgenderPrediction.py
  " Uses a library **Genderizer** (https://github.com/muatik/genderizer). this library is developed in python 2.0 since I am using Python 3.0 so i converted the library to python 3.0 and is included in folder **"lib"** inside the folder "sociodemographic". this library first creates a model from a trained data and files associated are in folder "data". It uses Naive bayes classifier to classify the gender on the basis of text so the library of naive bayes classifier is provided in folder **"lib"**. this file was also in python 2.0 therefore i converted it to 3.0 and provided it here."
Note:it uses pymongo and genderizer
