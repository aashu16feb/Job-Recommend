from flask import Flask , render_template , url_for , redirect , abort , request
from pymongo import MongoClient
import pymongo
import operator
import spacy
import bson
import json

connection_string = "mongodb://localhost:27017"
client = MongoClient(connection_string)
db = client['jobs']
db1=client['jobPortal']
mydb2 = db1['jobs']
mydb1=db1['jobapplicantinfos']

app = Flask(__name__)

#EXTRACT SKILLS FROM THE GIVEN TEXT
    
def extract_information_from_user(text):
    key=[]
    value=[]
    nlp = spacy.load("./output/model-last/")

    doc = nlp(text)

    for ent in doc.ents:
        key.append(ent.label_)
        value.append(ent.text)
    
    Dict = {key[i]: value[i] for i in range(len(key))}
    
    SKILLS= Dict["SKILLS"].split(",")

    Dict.update(SKILLS=SKILLS)

    text = Dict["SKILLS"]
    print("ABCD",text)
    txt=[]
    for ele in text:
        i=ele.strip(' ')
        #str(ele).replace(' ','')
        #print(i)
        txt.append(i)
    print("Hello",txt)
    return retirve_info_from_db(txt)

#RETRIVE RELATED JOBS BASED ON JACCARD COEFFICIENT 
def retirve_info_from_db(user_list):

    len_user_list = len(user_list)
    n = mydb2.find( { 'skillsets': { '$in': user_list}} ,{'_id':0}) #COLLECTING JOBS BASED ON MATCHING SKILLS
    
    jobs = []
    joblist=[]
    for i in n:

        job_skills = i['skillsets']
        print("Jobs",job_skills)
        match = len([k for k , val in enumerate(job_skills) if val in user_list])
        
        total_len = len(job_skills) + len_user_list 
        i['rank'] = match/total_len #RANKING COEFFICIENT
        jobs.append(i)
    jobs.sort(key=operator.itemgetter('rank') , reverse=True) #SORTING JOBS BASED ON THE RANK SCORE
    for i in jobs:
        joblist.append(i['title'])
    print(joblist)

    return json.dumps({"result":joblist})

"""#SORT THE JOBS RANK WISE AND DISPLAY
def show_info(jobs , job_skills , job_len):

    return render_template('show_job.html' , jobs=jobs , job_skills=job_skills , job_len=job_len)"""

@app.route('/recommend', methods=['POST'])
def my_form_post():
    data= request.get_json()
    userid=data['id']
    myskills=mydb1.find({'userId': bson.ObjectId(oid=str(userid))},{'_id':0})
    
    ski=""
    for data in myskills:
        ski=" ,".join(data['skills'])
        
    print(ski)
    return(extract_information_from_user(ski))    


if __name__ == "__main__":
    
    #CONNECTING WITH MONGO DB
    connection_string = "mongodb://localhost:27017"
    client = MongoClient(connection_string)

    db = client['jobs']
    db1=client['jobPortal']
    mydb = db1['jobs']
    mydb1=db1['jobapplicantinfos']
    #STARTING THE APPLICATION
    app.run(host="0.0.0.0" ,port=5000, debug = True)