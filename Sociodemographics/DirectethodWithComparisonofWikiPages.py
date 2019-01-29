#This file searches for the keywords reated to demographical features and display the sentences containing those words.

import nltk
from pymongo import MongoClient


# connect with mongo client
client = MongoClient('127.0.0.1', 27017)
client2 = MongoClient('127.0.0.1', 27017)

#objects for dealing mongodb clients
db1 = client.editordb
db2 = client2.pages_editorsdb

#for collections in mongoDB
collection1 = db1.editors
collection2 = db2.pages_editors

#Words searched in each sentence to extract demographical information
searchtext = "this user"
searchtext2 = "This user"
searchtext3 = "This User"
birthtext1 = "Birthday"
birthtext2 = "Birth day"
birthtext3 = "birthday"
birthtext4 = "birth Day"
born = "born"
born2 = "Born"
country = "Country"
country2 = "country"
lives = "lives"
lives2 = "live"
lives3 = "location"
lives4 = "Location"
cloc1 = "current location"
cloc2 = "Current Location"
cloc3 = "Current location"
cloc4 = "current Location"
gendr1 = "male"
gendr2 = "Male"
gendr3 = "Female"
gendr4 = "female"
edu1 = "education"
edu2 = "Education"
edu3 = "Bachelor"
edu4 = "bachelor"
edu5 = "B.Sc"
edu6 = "M.Sc"
edu7 = "Diploma"
edu8 = "diploma"
edu9 = "Master"
edu10 = "master"

#cursor for searching inside the collections of mongoDB
#limit is set to search only first 100 editors in the editor DB if you want to run it for all just remove the limit fuction

cursor2 = collection2.find().limit(100)
cursor1 = collection1.find().limit(100)
for doc2 in cursor2:


    #loop for searching inside the editor DB
    for doc1 in cursor1:
            if (doc1['_id']) in (doc2['editors_list']):
                print('-------------------------------------------------------------')
                print(doc2['page_title'])

                print(doc1['id'])
                print('\n')
                print (doc1['raw_content'])
                print ('\n')

        #tokenizing the raw text into sentences
                sent_text = nltk.sent_tokenize(doc1['raw_content'])

        #Searching for keywords in each sentence
                for sentence in sent_text:
                    if ((searchtext in sentence) or (searchtext2 in sentence) or (searchtext3 in sentence) ):
                        print(sentence)

                for birth in sent_text:
                    if ((birthtext1 in birth) or (birthtext2 in birth) or (birthtext3 in birth) or (birthtext4 in birth) or (born in birth) or (born2 in birth) or (country in birth) or (country2 in birth)):
                        print(birth)

                for cntry in sent_text:
                    if ( (country in cntry) or (country2 in cntry)):
                        print(cntry)


                for live in sent_text:
                    if ( (lives in live) or (lives2 in live) or (lives3 in live) or (lives4 in live) or (cloc1 in live) or (cloc2 in live) or (cloc3 in live) or (cloc4 in live)):
                        print(live)

                for gendr in sent_text:
                    if ((gendr1 in sent_text) or (gendr2 in sent_text) or (gendr3 in sent_text)or (gendr4 in sent_text)):
                        print(gendr)


                for edu in sent_text:
                    if ((edu1 in sent_text) or (edu2 in sent_text) or (edu3 in sent_text) or (edu4 in sent_text) or (edu5 in sent_text) or (edu6 in sent_text) or (edu7 in sent_text) or (edu8 in sent_text) or (edu9 in sent_text) or (edu10 in sent_text)):
                        print(edu)





            else:
                break

print("end")