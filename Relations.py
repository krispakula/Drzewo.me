#!/usr/bin/python
# -*- coding: iso-8859-2 -*-


import MySQLdb as mdb
import os, sys
import os.path
import datetime
from datetime import date


import time
import re


SCRIPT = os.path.basename(sys.argv[0])
MYSQL_DATABASE_NAME='nukedemo'
MYSQL_USER='kpakula'
MYSQL_PASSWORD='rmld29psf3697'
TABLE  = 'nuke_genealogy'
EMAILS_TO_SEND_TABLE = 'emails_to_send'

MYSQL_USER='root'
MYSQL_PASSWORD='rmld29'
TRANSLATIONS = 'translations'
THEMES_TABLE_NAME = 'themes'
SQL_LIMIT = 0

PATH_TO_PICTURES = 'image/drzewo'
PATH_TO_TREE=""

# Locations of images on the server
IMAGES = "images"

GENERATIONS_LIMIT = 6

IMAGE_CHILD_PICTURE_SIZE = 24  
IMAGE_GRANDCHILD_PICTURE_SIZE = 30 
IMAGE_PICTURE_SIZE = 16 

#SUPER_USERS = [614101095, 839397534, 682508999]

VALID_LANGUAGES = {"PL":"Polish", "EN":"English", "SP":"Spanish"}
DEFAULT_LANGUAGE = 'PL'
IMAGE_LOCATION = "image/"

GROUNUP_AGE_IN_DAYS = 5800

# Encoding example .  
#text = "3697"
#>>> m = hashlib.md5()
#>>> m.update(text.encode('UTF-8'))
#>>> print(m.hexdigest())

_a = u"\xB1"
_c = u"\xE6"
_e = u"\xEA"
_l = u"\xB3"
_n = u"\xF1"
_o = u"\xF3"
_s = u"\xB6"
_z = u"\xBF"
_z = u"\xBC"

_A = u"\xA1"
_C = u"\xC6"
_E = u"\xCA"
_L = u"\xA3"
_N = u"\xD1"
_O = u"\xD3"
_S = u"\xA6"
_Z = u"\xAF"
_Z = u"\xAC"


#   from constants import *

import logging 


#now we will Create and configure logger 
logging.basicConfig(filename="relations.log", 
					format='%(asctime)s %(message)s') 

#Let us Create an object 
logger=logging.getLogger() 

#Now we are going to Set the threshold of logger to DEBUG 
logger.setLevel(logging.DEBUG) 

logger.info("INFO: Drzewo.me is run") 







import collections
 
class Dict(collections.MutableMapping):
    """A dictionary that applies an arbitrary key-altering
       function before accessing the keys"""

    def __init__(self, *args, **kwargs):
        self.store = dict()
        self.update(dict(*args, **kwargs))  # use the free update to set keys

    def __getitem__(self, key):
        return self.store[self.__keytransform__(key)]

    def __setitem__(self, key, value):
        self.store[self.__keytransform__(key)] = value

    def __delitem__(self, key):
        del self.store[self.__keytransform__(key)]

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)

    def __keytransform__(self, key):
        return key

    def value(self, key):
        if self.store.has_key(key):
            return self.store[key]
        return ''

    def mama(self):
        if self.store.has_key('mere'):
            return self.store['mere']
        return ''
        
    def papa(self):
        if self.store.has_key('pere'):
            return self.store['pere']
        return ''
        
    def conj(self):
        if self.store.has_key('conjoint'):
            return self.store['conjoint']
        return ''
        
    def g(self):
        if self.store.has_key('genre'):
            return self.store['genre'] > 0
        return False
    
    def dob(self):
        if self.store.has_key('naissance'):
            return self.store['naissance'] 
        return ''
    
    def dod(self):
        if self.store.has_key('deces'):
            return self.store['deces'] 
        return ''
     
  
        
    def get_links(self, uid):
        # Return all infor for uid in the form of dictionary
        sql = "SELECT * from %s WHERE uid='%s';"%(TABLE, uid)
        row = self.sql_execute(sql)
        try:
            row_data = row[0]
            return [row_data[12], row_data[13], row_data[14]]
        except:
            logger.error("ERROR: Execution of SQL failed %s"%sql)
            return [0,0,0]

    def gpap(self): # dziadek ojczysty
        return self.get_links(self.papa())[0]
        
    def gpam(self): # dziadek maciezysty
        return self.get_links(self.mama())[0]
        
    def gmap(self): # babcia ojczysta
        return self.get_links(self.papa())[1]
        
    def gmam(self): # babcia maciezysta
        return self.get_links(self.mama())[1]
        
    def maml(self):  # tesciowa
        return self.get_links(self.conj())[1]
        
    def papl(self):  # test 
        return self.get_links(self.conj())[0]
   

    
class Relation:
    def __init__(self):
        self.con = mdb.connect('localhost',MYSQL_USER,MYSQL_PASSWORD,MYSQL_DATABASE_NAME)
        self.cur = self.con.cursor()
        self.column_names = []
        self.get_column_names()
        self.owner_uid = ''
        self.svg = ''
        self.match_string = ''
        self.descendants_counter =0
        self.all_db = {}
        self.current_date = datetime.date.today()
        self.rate = 0 
    
        # Open connection to MySQL       
    def get_login_dict(self, login_uid):     
        sql = "SELECT * from %s WHERE uid='%s';"%(TABLE, login_uid)
        logger.info("INFO: Trying to execute SQL: %s"%sql)
        row = self.sql_execute(sql)
        logger.debug("DEBUG:SQL returned %s"%row)
        self.login_dict = self.convert_sqlrow_to_dict(row[0])    
        
    def get_new_uid(self):
        return int(time.time())       
        
    def label_cleanup(self, label):
        before = label
        
        after = before.lstrip()
        if before != after:
            logger.error("ERROR: Label [%s] contains leading spaces in language %s"%(before, self.prefered_language))
            before = after

        after = before.rstrip()
        if before != after:
            logger.error("ERROR: Label [%s] contains trailing spaces in language %s"%(before, self.prefered_language))
            before = after

        after = re.sub(' +', ' ', before)
        if before != after:
            logger.error("ERROR: Label [%s] contains double spaces in language %s"%(before, self.prefered_language))
            before = after



        after = re.sub("'", "", before)
        if before != after:
            logger.error("ERROR: Label [%s] contains invalid sign ' in language %s"%(before, self.prefered_language))
            before = after 
            
        return after    
        
             
    def sql_execute(self, sql):
        logger.info("INFO: Attempting to execute SQL: %s"%(sql))
        try:
            self.cur.execute(sql)
            row = self.cur.fetchall()   
        except mdb.Error, e:
            logger.error("ERROR: Execution of SQL failed: %s"%sql)
            if self.con:
                self.con.rollback()
            logger.error("ERROR %s: %s"%(e.args[0],e.args[1]))
            logger.error("ERROR: Failed to execute SQL: %s"%(sql))
            return ""
            
        return row
 
    def sql_execute_and_commit(self, sql):
        
        logger.info("INFO: Attempting to execute and commit SQL: %s"%(sql))
        try:
            self.cur.execute(sql)
            self.con.commit()
            
        except mdb.Error, e:
            logger.error("ERROR: Execution of SQL failed: %s"%sql)
            if self.con:
                self.con.rollback()

            logger.error("ERROR %s: %s" % (e.args[0],e.args[1]))
            logger.error("ERROR: Failed to execute end commit SQL: %s"%(sql))
            return ""
            
        return 
    
    def get_dict(self, uid):
        
        # logger.info("INFO: searching in DB for %s"%uid)
        
        # return self.all_db[uid]
        # Return all infor for uid in the form of dictionary
        
        if uid == 0: 
            logger.error("ERROR: UID is number 0")
            return 
        if uid == '0': 
            logger.error("ERROR: UID is string '0'")
            return
        if uid < 0 : 
            logger.error("ERROR: UID is number '%s'"%uid)
            return 
        

        sql = "SELECT * from %s WHERE uid='%s';"%(TABLE, uid)
        try:    
            row = self.sql_execute(sql)
            row_data = row[0]
            return self.convert_sqlrow_to_dict(row[0])
        except:
            logger.error("ERROR: UID not found in DB during execution of get_dict: %s"%sql)
            return 



    def get_message(self, imie, ID, key): 
        email_msg = "\r\n".join([
         "",
         "%s"%(imie),
         " Welcome to the family Tree.",
         "",
         " https://drzewo.me/tr/drzewo.py?action=login\\&ampuid=%s\\ampkey=%s"%(ID,key),
         " Your identifier: %s"%(ID),
         " Your key: %s"%(key),
         "",
         ])
        return email_msg

    def get_key(self, uid):
        return hashlib.md5(str(uid)).hexdigest()[:6] 


    
    def get_person_age_in_days(self, idict):
        
        current_date = self.current_date
        dob_date = idict.dob()
        
        if type(dob_date) == type(""):
            # Do this if dob is TEXT not DATE
            p = re.compile(r"(\d\d\d\d)-(\d\d)-(\d\d)")
            a = p.search(dob_date)  
            if a is None: 
                logger.error("ERROR: Date [%s] is not in correct format for UID %s"%(dob_date, idict.value('uid'))) 
                return "", ""
            else:     
                try: 
                    dob_in_date_type = datetime.date( int(a.group(1)), int(a.group(2)), int(a.group(3)))
                    current_date = self.current_date
                    age_in_days = current_date - dob_in_date_type
                    
                    bday = datetime.date(current_date.year, int(a.group(2)), int(a.group(3)))
                    day_of_year = datetime.date(current_date.year, 1, 1) 
                    days_since_bday = current_date - bday                     
                    
                    return  age_in_days.days, days_since_bday.days
                except:  
                    logger.error("ERROR: DOB date %s not converted to DATE type for UID %s"%(dob_date,idict.value('uid'))) 
                    return "", ""
                
        if type(dob_date) == type(current_date): 
            # Assuming DATE format in database  
            age_in_days = current_date - dob_date
            
            bday = datetime.date(2023, dob_date.month, dob_date.today().day)
            day_of_year = datetime.date(2023, 1, 1) 
            days_since_bday = bday - day_of_year     
            
            
            
            return  age_in_days.days, days_since_bday
        
        logger.error("ERROR: Unknown type of date %s in database for UID %s"%(dob_date, idict.value('uid'))) 
        
        return "", ""



    def am_i_superuser(self):
        superuser = self.login_dict.value('SUPERUSER')
        if superuser == "1":
            return True
        else:
            return False
        return False

    def calculate_date( date, years):
        year = str(int(date[:4]) + years)
        return "%s%s"%(year, data[4:])

    def get_list_of_siblings(self, Person):
        # Return all infor for uid in the form of dictionary
        pere = Person.papa()
        mere = Person.mama()
        slf = Person.value('uid')
        sql = "SELECT `uid` from %s WHERE pere='%s' AND mere='%s' ;"%(TABLE, pere, mere)
        row = self.sql_execute(sql)
        try:
            row_data = []
            for i in row:
                if i[0] != slf:
                    row_data.append(i[0]) 
            return row_data
        except:
            return []      

    def recursive_siblings_descendants_check(self, counter, who_is_checked, against_who, Person1, Person2, rate):
        self.rate = rate 
        rate = rate * 2
            
        counter = counter -1 
        if counter <0:
            return
        
        logger.info("INFO: WAS HERE 1 %s %s"%(who_is_checked, against_who))        
        if self.match_string != "":
            return
        
        if Person1.papa() <= 0: return 
        if Person2.papa() <= 0: return 
        if Person1.mama() <= 0: return 
        if Person2.mama() <= 0: return 
        
        list_of_siblings = self.get_list_of_siblings(Person1)
        logger.info("INFO: LIST OF SIBLINGS %s"%str(list_of_siblings)) 
        
        for sibling in list_of_siblings:
            logger.info("INFO: WAS HERE 3 %s %s %s"%(sibling, who_is_checked, against_who)) 
                      
            Sibling = self.get_dict(sibling)
            if Sibling.g()  :
                whos = "your %s brother is"%who_is_checked
            else: 
                whos = "your %s sister is"%who_is_checked
                
            if Person2.g() :
                against = "hi"
            else:
                against = "her"
            self.recursive_check(counter, whos, against, Person2, Sibling, rate)
            if self.match_string != "":
                return self.match_string
            
        against_father = "%s %s"%(against_who, "fathers")
        whos_papa = "fathers %s"%(who_is_checked)       
        Person_papa = self.get_dict(Person1.papa())
        self.recursive_siblings_descendants_check( counter, whos_papa, against_father, Person_papa, Person2,  rate)  
        if self.match_string != "": return self.match_string
        
        
        against_mother = "%s %s"%(against_who, "mothers")        
        whos_mama = "mothers %s"%(who_is_checked)
        Person_mama = self.get_dict(Person1.mama())        
        self.recursive_siblings_descendants_check( counter, whos_mama, against_mother, Person_mama, Person2, rate)  
        if self.match_string != "": return self.match_string
        
        return 
            
    
    def recursive_sibling_check(self, counter, who_is_checked, against_who, Person1, Person2, rate):
        y = rate
        self.rate = rate 
        rate = rate * 2
            
        counter = counter -1 
        if counter <0:
            return
        
        if self.match_string != "":
            return
        
        if Person1.papa() <= 0: return 
        if Person2.papa() <= 0: return 
        if Person1.mama() <= 0: return 
        if Person2.mama() <= 0: return 
        
        
        if Person1.value('pere') == Person2.value('pere') and Person1.value('mere') == Person2.value('mere'): 
            if Person2.g():
                self.match_string = "your %s %s brother"%(who_is_checked, against_who)
            else:
                self.match_string = "your %s %s sister"%(who_is_checked, against_who)
            return self.match_string
        else: 
            # Continue checking
            against_father = "%s %s"%(against_who, "fathers")
                
            whos_papa = "%s"%(who_is_checked)
            
            if Person1.papa() > 0:
                Person_papa = self.get_dict(Person1.papa())
                self.recursive_sibling_check(counter, whos_papa, against_father, Person_papa, Person2, rate)
            
            if self.match_string != "": return self.match_string   
            
            if self.match_string == '': 
                whos_mama = "%s"%(who_is_checked)
                # Continue checking
                against_mother = "%s %s"%(against_who, "mothers")

                if Person1.mama() > 0:     
                    Person_mama = self.get_dict(Person1.mama())                                 
                    self.recursive_sibling_check(counter, whos_mama, against_mother, Person_mama, Person2, rate)
                    
                if self.match_string != "": return self.match_string          
        return 
    
    
    def recursive_check(self, counter, who_is_checked, against_who, Person1, Person2, rate):
        self.rate = rate
        rate = rate * 2
        
        counter = counter -1 
        if counter <0:
            return
        
        if self.match_string != "":
            return
        
        try: 
            p1 = Person1.value('uid')
            p2 = Person2.value('uid')
        except:
            return 
        
        
        if Person1.value('uid') == Person2.value('uid'): 
            self.match_string = "%s %s"%(who_is_checked, against_who)
            return
        else: 
            # Continue checking
            if against_who == "you yourself": 
                against_father = "your %s"%("father")
            else:  
                against_father = "%ss %s"%(against_who, "father")
                
            whos_papa = "%s"%(who_is_checked)
            
            if Person1.papa() > 0:
                Person_papa = self.get_dict(Person1.papa())
                self.recursive_check(counter, whos_papa, against_father, Person_papa, Person2, rate)
            
            if self.match_string != "": return   
            
            if self.match_string == '': 
                whos_mama = "%s"%(who_is_checked)
                # Continue checking
                if against_who == "you yourself": 
                    against_mother = "your %s"%("mother")
                else:    
                    against_mother = "%ss %s"%(against_who, "mother")

                if Person1.mama() > 0:     
                    Person_mama = self.get_dict(Person1.mama())                                 
                    self.recursive_check(counter, whos_mama, against_mother, Person_mama, Person2, rate)
                    
                if self.match_string != "": return           
        return 
      
    
    def get_relationship(self, from_person, to_person):
        
        idict = self.get_dict(to_person)
        Person = idict
        
        Me = self.get_dict(from_person)
        logger.info("INFO: Looking at person: %s %s %s"%(idict['uid'], idict['prenom'], idict['nom']))
        self.login_dict = Me
        
        logger.info("INFO: Looking by person: %s %s %s"%(Me['uid'], Me['prenom'], Me['nom']))
        
        # Finding all acesstors  
        who = ""
        against = "you yourself" 
        self.recursive_check(6, who, against, Me, Person, 1 )
        if self.match_string != '':
            return self.match_string 
        
        
        # Finding children and all descendants 
        if Person.g():
            prenom = "hi"  # It is hi on purpose / do not correct 
        else:
            prenom = "her"      
        # Checking if I am in the person Ancesstors  
        # Finding if person is my descendant  
        who = ""
        against = "you are %s"%prenom            
        self.recursive_check(6, who, against, Person, Me, 1)
        if self.match_string != '':
            return self.match_string       
        

        # Finding all full sisters and brothers, aunts and uncles 
        # And Aunts, Uncles and generations UP
        against= ""
        who = ""
        self.recursive_sibling_check(6, who, against, Me, Person, 2)        
        if self.match_string != '':
            return self.match_string         
        
        
        # Finding nieces nepnews and cousins
        against= ""
        who = ""        
        self.recursive_siblings_descendants_check(12, who, against, Me, Person, 1)
        if self.match_string != '':
            return self.match_string  
        
        # Finding if person is in my wifes ancestors all ancestors   
        if Me.conj() > 0:
            My_spouse = self.get_dict(Me.conj())
            who = "your"
            if Me.g():
                against = "wife"
            else:
                against = "husband"
            self.recursive_check(6, who, against, My_spouse, Person, 0)
            if self.match_string != '':
                return self.match_string 
                
            
        # Finding if person is my spouses full sibling or aunt, uncle ets.     
        if Me.conj() > 0:
            My_spouse = self.get_dict(Me.conj())
            who = ""
            if Me.g():
                against = "wifes"
            else:
                against = "husbands"
            self.recursive_sibling_check(5, who, against, My_spouse, Person, 0)
            if self.match_string != '':
                return self.match_string    
  
          
        # finding if my fathers is on persons Ancesstors 
        who = ""
        # Find siblings by father 
        p = "father"
        against = "your %ss is %s"%(p, prenom)  
        if Me.papa() > 0: 
            Papa = self.get_dict(Me.papa())
            self.recursive_check(8, who, against, Person, Papa, 2)
            if self.match_string != '':
                return self.match_string   
            
            # Finding half uncles and aunts 
            against = "your %ss father is %s"%(p, prenom)  
            if Papa.papa() > 0: 
                self.recursive_check(8, who, against, Person, self.get_dict(Papa.papa()), 4)
                if self.match_string != '':
                    return self.match_string 
                
            # Finding half uncles and aunts                 
            against = "your %ss mother is %s"%(p, prenom)   
            if Papa.mama() > 0: 
                self.recursive_check(8, who, against, Person, self.get_dict(Papa.mama()), 4)
                if self.match_string != '':
                    return self.match_string                  
                
        # Find half siblings by mother     
        p = "mother"
        against = "your %ss is %s"%(p, prenom)  
        if Me.mama() > 0: 
            Mama = self.get_dict(Me.mama())
            self.recursive_check(5, who, against, Person, Mama, 2)
            if self.match_string != '':
                return self.match_string    
            
            # Finding half uncles and aunts 
            against = "your %ss father is %s"%(p, prenom) 
            if Mama.papa() > 0: 
                self.recursive_check(5, who, against, Person, self.get_dict(Mama.papa()), 4)
                if self.match_string != '':
                    return self.match_string 
            # Finding uncles and aunts 
            against = "your %ss mother is %s"%(p, prenom)  
            if Mama.mama() > 0: 
                self.recursive_check(5, who, against, Person, self.get_dict(Mama.mama()), 4)
                if self.match_string != '':
                    return self.match_string    
    
        # Finding if person is on the list of spouse half ancesstors 
        if Me.conj() > 0:
            My_spouse = self.get_dict(Me.conj())
            who = "your"
            if Me.g():
                against = "wife"
            else:
                against = "husband"
            self.recursive_check(8, who, against, My_spouse, Person, 0)
            if self.match_string != '':
                return self.match_string 
             
        
        # Finding if person spouse is on the list of my Ancessors      
        if Person.conj() > 0:
            Spouse = self.get_dict(Person.conj())
            who = ""
            if Person.g():
                against = " your"
                who = " husband of"
            else:
                against = " your"
                who = " wife of"
            self.recursive_check(8, who, against, Me, Spouse, 0)
            if self.match_string != '':
                return self.match_string    
            
        # Finding wifes and husband of direct Descendants       
        if Person.conj() > 0:
            Spouse = self.get_dict(Person.conj())
            who = ""
            if Spouse.g():
                against = " husband"
                who = "i am her "
            else:
                against = " wife"
                who = "i am his "
            self.recursive_check(8, who, against, Spouse, Me, 0)
            if self.match_string != '':
                return self.match_string                
            
        #===============================================================    
        
        # Here start not blood related tests  
        
        me = Me.value("uid")
        person = Person.value('uid')
        My_spouse = self.get_dict(Me.conj())        
        
        if Person.papa() >0 :
            person_papa = Person.papa()
            Person_papa = self.get_dict(person_papa)
  
        if Person.mama() >0 : 
            person_mama = Person.mama()
            Person_mama = self.get_dict(person_mama)        
  
        person_spouse = Person.conj()
        
        twoja = "" # self.c_lang("This is your feminine")  
        twoj = "" # self.c_lang("This is your masculine")  
        

        self.msg = ""
        
        if True:  # try
            # Macocha test      
            Me = self.login_dict
            if Me.papa() > 0:        
                My_papa = self.get_dict(Me.papa())
                if My_papa.conj() > 0:
                    if  person == My_papa.conj():
                        text =  "step mother"                                                            
                        self.msg="%s%s"%( twoja, text)
                        return self.msg          

            # Ojczym test 
            if Me.mama() > 0: 
                My_mama=self.get_dict(Me.mama())
                if My_mama.conj() > 0:
                    if  person == My_mama.conj():
                        text =  "step father"                                                                 
                        self.msg = "%s%s"%(twoj, text)
                        return self.msg       
                      

                    
            #===============================================
            # Rodzeństwo nie krewne
                                       
            my_mama = Me.mama()
            my_papa = Me.papa()
            person_mama = Person.mama()
            person_papa = Person.papa()
            
                   
            my_spouse = Me.conj()  
            # szwagier test
            if my_spouse > 0 :
                My_spouse = self.get_dict(my_spouse)  
                my_spouse_papa = My_spouse.papa()
                my_spouse_mama = My_spouse.mama()
                
                if  person_papa == my_spouse_papa or person_mama == my_spouse_mama:
                    if My_spouse.g(): 
                        if Person.g(): 
                            text = "brother in law your husbands brother"                  
                            self.msg = "%s%s"%(twoj, text)
                            return self.msg
                        else:
                            text =  "sister in law your husbands sister"                  
                            self.msg = "%s%s"%(twoja, text)
                            return self.msg
                    else:
                        if Person.g(): 
                            text =  "brother in law your wifes brother"                 
                            self.msg = "%s%s"%(twoj, text)
                            return self.msg                        
                        else:
                            text =  "sister in law your wifes sister"                  
                            self.msg = "%s%s"%(twoja, text)
                            return self.msg

            person_papa = Person.papa()
            person_mama = Person.mama()
                    
            # ziec i synowa test 
            if person_spouse >0: 
                Spouse = self.get_dict(person_spouse)
                if  me in [ Spouse.papa(), Spouse.mama()]:
                    if Person.g(): 
                        text =  "son in law your daughters husband"                       
                        self.msg = "%s%s"%(twoj, text)
                        return self.msg
                    else:
                        text =  "daughter in law your sons wife"                 
                        self.msg = "%s%s"%(twoja, text)
                        return self.msg
              

            # szwagier od siotry lub brata
            
            # szwagier od siostry test 
            if Person.conj() >0: 
                Spouse = self.get_dict(Person.conj())
                if  my_papa ==Spouse.papa() or my_mama == Spouse.mama():
                    if Person.g() : 
                        text =  "brother in law your sisters husband "                      
                        self.msg = "%s%s"%(twoj, text)
                    else:
                        text =  "sister in law your brothers wife"                    
                        self.msg = "%s%s"%(twoja, text)
                    return self.msg

#========================================================================                
                
            if Person.conj() >0: 
                Spouse = self.get_dict(Person.conj())
                if Me.conj() > 0:
                    My_spouse = self.get_dict(Me.conj())
                    if Spouse.papa() == My_spouse.papa() or Spouse.mama() == My_spouse.mama():
                        if Me.g():
                            if Person.g() : 
                                text =  "brother in law husband of your wifes sister"                      
                                self.msg = "%s%s"%(twoj, text)
                            else:
                                text =  "sister in law wife of you wifes brother"                  
                                self.msg = "%s%s"%(twoja, text)
                        else: 
                            if Person.g() : 
                                text =  "brother in law husband of your husbands sister"                    
                                self.msg = "%s%s"%(twoj, text)
                            else:
                                text =  "sister in law wife of your husbands brother"                  
                                self.msg = "%s%s"%(twoja, text)    
                            return self.msg                

            # Siostra lub brat przyrodni test              
            if Person.mama()  > 0 and Me.papa() >0:   
                My_papa = self.get_dict(Me.papa())
                if  Person.mama() == My_papa.conj():
                    if Person.g() : 
                        text =  "step brother son of your fathers wife"                     
                        self.msg = "%s%s"%(twoj, text)
                    else:
                        text =  "step sister daughter of your fathers wife"              
                        self.msg = "%s%s"%(twoja, text)                        
                    return self.msg
            if Person.papa()  > 0 and Me.mama() >0:   
                My_mama = self.get_dict(Me.mama())
                if  Person.papa() == My_mama.conj():
                    if Person.g() : 
                        text =  "step brother son of of your mothers husband"                   
                        self.msg = "%s%s"%(twoj, text)
                    else:
                        text =  "step sister daughter of your mothers husband"                    
                        self.msg = "%s%s"%(twoja, text)                        
                    return self.msg
                  
            if Person.papa() > 0:
                if Me.conj() == person_papa:
                    if Person.g(): 
                        text =  "step son you are her step mother"                    
                        self.msg = "%s%s"%(twoj, text)
                        return self.msg
                    else:
                        text =  "step daughter you are her step mother"                  
                        self.msg = "%s%s"%(twoja, text)
                        return self.msg
                        person_papa = Person.papa()   
                        
            if Person.mama() > 0:
                if Me.conj() == person_mama :
                    if Person.g(): 
                        text =  "step son you are his step father"                      
                        self.msg = "%s%s"%(twoj, text)
                        return self.msg
                    else:
                        text =  "step daughter you are her step father"                     
                        self.msg = "%s%s"%(twoja, text)
                        return self.msg
                        person_papa = Person.papa()                           
            
        # except:
        #    pass            

        return self.msg


  

    def convert_sqlrow_to_dict(self, row):
        i = 0
        values = row
        d = Dict()
        for c in self.column_names:
            v = row[i]
            if (v is None  ) : v = ""
            if (v == 'None') : v = ""
            d[c] = v
            i += 1 
        return d

        
        
    
  

    def check_if_date_string_is_valid(self, date, person): 
        # date should be in format 0000-00-00 and be valid date otherwise it is simple text 
        
        correctDate = False
        if date == "": 
            correctDate = True
            return correctDate
        
        p = re.compile(r"(\d\d\d\d)-(\d\d)-(\d\d)")
        a = p.search(date)  
        if a is None: 
            correctDate = False
        else:     
            try:
                newDate = datetime.datetime( int(a.group(1)), int(a.group(2)), int(a.group(3)))
                correctDate = True
            except ValueError:
                logger.error("ERROR: the string [%s] is not correct for date at UID %s"%(date, person.value['uid']))
                correctDate = False
        return correctDate
        
    def is_it_myself(self, idict):
        if idict['uid'] == self.login_dict['uid']: 
            return True
        return False
    


    def format_as_table(self, x):
        t = []
        for i in x:
            t.append(i[0])

    def format_as_table(self, x):
        t = []
        for i in x:
            t.append(i[0])
        return t
       

    def get_column_names(self):
        # Przeczytaj atrybuty tabeli 'nuke_genealogy' 
        columns = self.sql_execute('DESCRIBE %s'%TABLE)

        column_names=[]
        for i in columns:
            column_names.append(i[0])
        self.column_names = column_names
 
        columns = self.sql_execute('DESCRIBE %s'%TRANSLATIONS)
                                            
        column_names=[]
        for i in columns:
            column_names.append(i[0])
        self.translations_column_names = column_names
        
        


if '__main__' == __name__:
    if True:   # NEW
        
        r = Relation()
        result = r.get_relationship(259092175, 326411579)
        print result 

    else:
        pass 
                                             
