#This program first check which editor has edited which page and then takes the raw text from author profile as input and tells the gender of the editor
#For detecting gender through text genderizer library is used
#Genderizer library is originally developed in python 2 the one used in this program is converted to python3.0 for use in this project
#genderizer library can be found on following link (https://github.com/muatik/genderizer)
#The only function of text based is used in this program
from pymongo import MongoClient

#Using library genderizer
from genderizer.genderizer import Genderizer




# connect with mongo client
client = MongoClient('127.0.0.1', 27017)
client2 = MongoClient('127.0.0.1', 27017)

##objects for dealing mongodb clients
db1 = client.editordb
db2 = client2.pages_editorsdb

#for collections in mongoDB
collection1 = db1.editors
collection2 = db2.pages_editors

#cursor for searching inside the collection. Limit is used to get the record of first 20 editors in the list but to check it on whole db just remove limit.
cursor2 = collection2.find().limit(22)
cursor1 = collection1.find().limit(22)

#loop for searching pages
for doc2 in cursor2:

    #loop for searching editors
    for doc1 in cursor1:

        #this conditions detects that editor has editted which page
        if (doc1['_id']) in (doc2['editors_list']):
            print('-------------------------------------------------------------')
            print('Page Title = '+doc2['page_title'])
            print('\n')
            print(doc1['id'])
            print('\n')
            text = doc1['raw_content'].ljust(120)[:120].strip()
            print("gender by text")

            #Raw text given as an input to the function in genderizer library
            print(Genderizer.detect(text=text))
            print('\n')
        else:
            break

print("end")