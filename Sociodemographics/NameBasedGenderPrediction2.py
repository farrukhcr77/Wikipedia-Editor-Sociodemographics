#This program tokenizes the words in raw text taken from editor profile and assigns parts of speach to each word
#Then it creates a list of proper nouns
#Then it compares the detected proper nouns with the list of categorized names and displays the gender of editor.

import nltk
from pymongo import MongoClient
import pandas as pd
import numpy as np
from nltk import pos_tag

#class for author
class Author:
    def __init__(self):
        self.name = ""
        self.gender = ""
    def setname(self, name):
        self.name = name
    def setgender(self, gender):
        self.gender = gender

#declaration of list of authors
authors = []

#reading file of categorized names and creating a string list using numpy
data = pd.read_csv("C:/Users/Farrukh/name.csv", header=None, encoding="utf8")
myarray = np.array(data)
np.transpose(myarray)

#creating each row in authors list using author class
for row in myarray:
    author = Author()
    author.setname(row[0])
    author.setgender(row[1])
    authors.append(author)


# connect with mongo client
client = MongoClient('127.0.0.1', 27017)
client2 = MongoClient('127.0.0.1', 27017)

##objects for dealing mongodb clients
db1 = client.editordb

#for collections in mongoDB
collection1 = db1.editors


#cursor for searching inside the collection. Limit is used to get the record of first 20 editors in the list but to check it on whole db just remove limit.
cursor1 = collection1.find().limit(20)


#for loop for accessing data inside the cursor
for doc1 in cursor1:

            print('-------------------------------------------------------------')
            print(doc1['_id'])
            print('\n')
            print(doc1['id'])
            print('\n')

            #creating a list to store the list of pronouns
            propernouns = []

            #tokenizing raw text into words
            sent_text = nltk.word_tokenize(doc1['raw_content'])

            #tagging each word with its part of speech and creating a list of words along with part of speech
            tagged = [pos_tag(sent_text)]

            #As it creates a list inside list so 2 for loops are used to acces the content inside the list "tagged"
            for row1 in tagged:
                for row2 in row1:

                    #if word is tagged as proper noun
                    if row2[1]=='NNP':

                        #adding rows to list of propernoun
                        propernouns.append(row2)

            #since it creates an integer array so using numpy for string array
            propernouns2 = np.array(propernouns)

            #taking transpose because numpy inverts the list
            np.transpose(propernouns2)
            print (propernouns2)

            #comparing the list of propernoun with the list of authors
            for row5 in propernouns2:
                    for row4 in authors:
                        if row5[0].lower() == row4.name.lower():
                            print("Author Name: " + row4.name)
                            if row4.gender == "M":
                                print("Author is Male")
                            elif row4.gender == "F":
                                print("Author is Female")
                            elif row4.gender == "?M":
                                print("Author name mostly used for male")
                            elif row4.gender == "?F":
                                print("Author name mostly used for female")
                            elif row4.gender == "?":
                                print("unknown")
            #emptying the list for the next editor
            propernouns[:]=[]
            print('--------------------------------------------------------------')

print("end")