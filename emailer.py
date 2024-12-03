#!/usr/bin/python
# -*- coding: iso-8859-2 -*-


#=======================================================================================================
# HISTORY:   |  CHANGE:
# Date:      |
# 28-Sep-2023|  Wersja Orginalna 
#            !  


'''
PURPOSE:
'''
import MySQLdb as mdb
import os, sys
import os.path
import datetime
from datetime import date



fromaddr = 'admin@drzewo.me'
toaddrs  = 'kris.pakula@gmail.com'


import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.application import MIMEApplication

import time
import re
# Import modules for CGI handling 

import HTMLgen
import HTMLGen
import hashlib


SCRIPT = os.path.basename(sys.argv[0])
SCRIPT = "https://drzewo.me/tr/dr.py"
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

PATH_TO_PICTURES = 'https:/drzewo.me/tr/image/drzewo'
PATH_TO_TREE=""

# Locations of images on the server
IMAGES = "https://drzewo.me/tr/images"

GENERATIONS_LIMIT = 6

IMAGE_CHILD_PICTURE_SIZE = 24  
IMAGE_GRANDCHILD_PICTURE_SIZE = 30 
IMAGE_PICTURE_SIZE = 16 

#SUPER_USERS = [614101095, 839397534, 682508999]

VALID_LANGUAGES = {"PL":"Polish", "EN":"English", "SP":"Spanish"}
DEFAULT_LANGUAGE = 'PL'

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

import logging 


#now we will Create and configure logger 
logging.basicConfig(filename="emailer.log", format='%(asctime)s %(message)s') 

##Let us Create an object 
logger=logging.getLogger() 

#Now we are going to Set the threshold of logger to DEBUG 
logger.setLevel(logging.DEBUG) 


hidden=             ['id', 'uid', 'pere','mere','genre','conjoint','bapt','bapt_plac','epouse','deces_plac','picture_id','facebook_id','owner_uid','change_time','SUPERUSER','theme' ]
hidden_for_editing= ['id', 'uid', 'pere','mere','genre','conjoint','bapt','bapt_plac','epouse','owner_uid','change_time','facebook_id','picture_id', 'SUPERUSER', 'theme', 'pref_lang']
hidden_for_editing_by_myself= ['id', 'uid', 'pere','mere','genre','conjoint','bapt','bapt_plac','epouse','owner_uid','change_time','facebook_id','picture_id', 'SUPERUSER']
hidden_for_editing_by_super=  ['id', 'uid','genre','bapt','bapt_plac','epouse','owner_uid','change_time','facebook_id','picture_id']
 


dates_items = ['bapt', 'naissance', 'deces'] #Pola w bazie danych ktore sa datami

RADIUS = 3
COLOR = 'yellow'
STEM = 0.0

import Relations
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
   

class Theme(collections.MutableMapping): 
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
    
class Server:
    def __init__(self, server_id):
        self.id = server_id
        self.log = ''
        self.password = ''
        
    def login(self, login, password):
        self.log = login
        self.password = password
        self.prin("LOGGED TO SERVER AS: %s %s"%(self.log, self.password))
        
    def sendmail(self, sender, recipient , text):
        self.prin("EMAIL SEND FROM %s"%sender)
        self.prin("EMAIL   SEND TO %s"%recipient)
        self.prin("ABOUT %s"%text)
        self.prin("ON SERVER %s LOGGED AS %s %s"%(self.id, self.log, self.password))
    
    def quit(self): 
        self.prin("SERVER %s QUITED"%self.id )
        
    def prin(self, text):
         pass
#        print text

    
    
class Emailer:
    def __init__(self, login_uid, pref_lang):
        self.con = mdb.connect('localhost',MYSQL_USER,MYSQL_PASSWORD,MYSQL_DATABASE_NAME)
        self.cur = self.con.cursor()
        self.column_names = []
        self.translations_column_names = []
        self.get_column_names()
        self.login_dict = self.get_login_dict(login_uid)
        self.idict = Dict()
        self.owner_uid = ''
        self.prefered_language = pref_lang
        self.match_string = ''
        self.descendants_counter =0
        self.all_db = {}
        self.current_date = datetime.date.today()
        self.themes = {}
        self.theme = Theme()
        self.rate = 0 
        self.server = "" # smtplib.SMTP_SSL('smtp.titan.email:465')

    
    
    def run_emails(self):
        
        username = 'admin@drzewo.me'
        password = 'Rmld@3697'

        # Flip here for test mode 
        self.server = smtplib.SMTP_SSL('smtp.titan.email:465')
        # self.server = Server('smtp.titan.email:465')
        
        
        self.server.login(username, password)
        
        logging.basicConfig(filename="emailer.log", format='%(asctime)s %(message)s')         
    
        # print "Running run_email"
        sql = "SELECT * FROM %s WHERE `date_send`='' ORDER BY `id` ASC LIMIT 1;"%(EMAILS_TO_SEND_TABLE)
        
        # print sql
        row = self.sql_execute(sql)
        
        for person in row:
            k = person
            # self.login_dict.value('uid'), idict.value('uid')
            email_id = k[0]
            email = k[1]
            from_person = k[2]
            to_person = k[3]
            
            self.run_one_email(email, from_person, to_person, email_id)
            # print "Running inside the loop  %s"%(str(person))
        
        self.server.quit()
        
        
        
    def run_one_email(self, email, sender, recipient, email_id):   
        
        Sender = self.get_dict(sender)
        Recipient = self.get_dict(recipient)
        self.login_dict = Recipient
        
        self.set_theme()
        self.set_prefered_language()
        
        text = self.get_email_text(Sender, Recipient, email_id)

        msg = MIMEMultipart()

        first_name = Sender['prenom']
        last_name = Sender['nom']

        msg['Subject'] = 'Zaproszenie do Drzewa od %s %s'%(self.kogo(Sender),last_name)
        msg['From'] = "admin@drzewo.me"
        msg['To'] = email

        part1 = MIMEText(text, 'html') 

        msg.attach(part1)
        
        self.server.sendmail("admin@drzewo.me", email, msg.as_string())
        # print "Running one email:%s sender:%s recipient:%s email id:%s"%(email, sender, recipient, email_id)

        date_send = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')

        sql = "UPDATE `%s` SET `date_send`='%s'  WHERE `id`='%s' ;"%(EMAILS_TO_SEND_TABLE, date_send, email_id )
        # print sql
        
        
        # Comment statement below to prevent marking in database the email was sent
        # This way emailer.py keeps resending it 
        self.sql_execute_and_commit(sql)
        
        time.sleep(1)

   
    def get_email_text(self, Sender, Recipient, emailid):
        
        text = self.main(Sender, Recipient, emailid) 
        
        return text                 
    
        # Open connection to MySQL       
    def get_login_dict(self, login_uid):     
        sql = "SELECT * from %s WHERE uid='%s';"%(TABLE, login_uid)
        logger.info("INFO: Trying to execute SQL: %s"%sql)
        row = self.sql_execute(sql)
        logger.debug("DEBUG:SQL returned %s"%row)
        self.login_dict = self.convert_sqlrow_to_dict(row[0])    

    def c_lang(self, label):  
        
        label= re.sub(' +', ' ', label) # remove double spaces
        label= re.sub("'", "", label)   # remove double spaces
        label = label.lstrip()
        label = label.rstrip()
        
        
        PREF_LANG = self.prefered_language
            
        sql = 'SELECT * FROM translations WHERE lang = "%s" AND label = "%s" ;'%(PREF_LANG, label)
        row = self.sql_execute(sql)
        
        l = ()
        if type(row) != type(l):
            return "no translation in %s {%s}"%(self.login_dict['pref_lang'], label)

        if len(row) == 0:
            return "no list translation in %s {%s}"%(self.login_dict['pref_lang'], label)
        
        if len(row) > 1:
            logger.error("ERROR: MORE THAT ONE TRANSLATION %s"%str(row))
            logger.error("ERROR: Translation not found for [%s] in language:%s"%(label, self.prefered_language)) 
            return "multiple translations in %s {%s}"%(self.login_dict['pref_lang'], label)
        
        row = row[0]
        return row[2]    
        
    def c_lang_the_oldway(self, label) :   
        
        d = self.get_dict_from_translations(label)
        
        if type(d) == type({}): 
            return d['translation']
        else: 
            logger.error("ERROR: Translation not found for [%s] in language:%s"%(label, self.prefered_language))
            if d != "":  
                return "no translation in %s {%s}"%(self.login_dict['pref_lang'], label)
            else:
                logger.error("ERROR: Defaulted to translation [%s]"%(label))
                return "[%s]"%label
      
    
        
    def get_new_uid(self):
        return int(time.time())
    
    def set_prefered_language(self):
        self.prefered_language = self.login_dict['pref_lang']
        
        
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
            
    def set_theme(self): 

        # print "THEME SELECTED BY RECIPIENT %s"%self.login_dict['theme']

        sql = 'DESCRIBE %s'%THEMES_TABLE_NAME
        column_names = self.sql_execute(sql)
        
        logger.info("INFO: Column names %s "%(str(column_names)))
        
        sql = 'SELECT * FROM themes WHERE id = "%s" ;'%(self.login_dict['theme'])
        theme_row = self.sql_execute(sql)[0]
                     
        logger.info("INFO: Theme row %s "%(str(theme_row)))             
 
        i = 0  
        d = {} 
        for column_name in column_names:
            d[column_name[0]] = theme_row[i]           
            i += 1                                                                         
        self.theme = Theme(d)                                                
    
    def set_themes(self):         
        
        sql = 'SELECT `id`,`name` FROM themes ;'
        
        themes_row = self.sql_execute(sql)
        logger.info("INFO: Themes rows %s "%(str(themes_row)))             
 
        d = {}
        for theme in themes_row:
            logger.info("INFO: Theme row %s "%(str(themes_row)))                  
            d[theme[0]] = theme[1]                                                                                 
        self.themes = d   
        
             
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

   
    
    def show_table(self, rows, order ):
        # not used     
        dmain = HTMLgen.Div(id = 'main')
        ddemo = HTMLgen.Div(id = 'demo')
    
        h = []
        # sortable by SQL statement 
        table = HTMLgen.Table(border=0, cell_spacing=0, heading=h, width=None, body=[])
    
        tb = HTMLGen.Table(border=0, cell_spacing=0, heading=None, width=None, body=[])
        tr = []
    
        dmain.append(ddemo)
        ddemo.append(table)
    
        return dmain
    
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
             
    def get_tabela_grandparents(self, text, idict, uid):
        
        dedit = HTMLgen.Div(id = 'parents')
        table = HTMLgen.TableLite(border=0, cell_spacing=1, width=None, body=[])
        tr = HTMLgen.TR()
        pere_dict = self.get_dict(int(idict.value('pere')))
        if not pere_dict is None:
            url = "%s?action=show&uid=%s"%(SCRIPT, idict['pere'])           
            td = HTMLgen.TD()
            #PL td.append(self.one_person('Dziadek %sy'%text, url, pere_dict))

            text1 = self.c_lang("%s %s"%(text,"grandfather"))
            td.append(self.one_person(' %s '%(text1), url, pere_dict))
            tr.append(td)
        else: # Dadaj puste pole 
            td = HTMLgen.TD('')
            tr.append(td)
            td = HTMLgen.TD('')
            tr.append(td)
        
        mere_dict = self.get_dict(int(idict.value('mere')))
        if not mere_dict is None:
            url = "%s?action=show&uid=%s"%(SCRIPT, idict.value('mere'))
            td = HTMLgen.TD()
            #PL td.append(self.one_person('Babcia %sa'%text, url, mere_dict))
            text1 = self.c_lang("%s %s"%(text, "grandmother"))
            td.append(self.one_person(' %s '%(text1), url, mere_dict))
            tr.append(td)
        else: # Dadaj puste pole
            td = HTMLgen.TD('')
            tr.append(td)
            td = HTMLgen.TD('')
            tr.append(td)

        table.append(tr)
    
        dedit.append(table)
        return dedit 

    def one_person(self, text, url, dict):
        table = HTMLgen.TableLite(border=0, cell_spacing=2, width=None, body=[])
        tr = HTMLgen.TR()
        href = HTMLgen.Href( url, " %s %s"%(dict.value('prenom'),dict.value('nom')))
        td = HTMLgen.TD()
        td.append('%s :'%text)
        td.append(HTMLgen.BR())
        td.append(href)
        tr.append(td)
        image_width = 3*IMAGE_PICTURE_SIZE
        
        # image = HTMLgen.Image('%s'%( self.get_picture(dict)), width="%s"%(3*IMAGE_PICTURE_SIZE), height="%s"%(4*IMAGE_PICTURE_SIZE))
        image = HTMLgen.Image('%s'%( self.get_picture(dict)), width="", height="%s"%(4*IMAGE_PICTURE_SIZE))
        href = HTMLgen.Href( url, image)
        td = HTMLgen.TD()
        td.append(href)
        tr.append(td)  
        table.append(tr)
        return table      
        
            
    def get_tabela_rodzice(self, idict, uid):
    
        dedit = HTMLgen.Div(id = 'parents')
        table = HTMLgen.TableLite(border=0, cell_spacing=1, width=None, body=[])
        tr = HTMLgen.TR()
        pere_dict = self.get_dict(int(idict.value('pere')))
        tr_grandparents= HTMLgen.TR()
        if not pere_dict is None:
            td_grandparents= HTMLgen.TD()
            
            text = "paternal"
            td_grandparents.append(self.get_tabela_grandparents(text, pere_dict,  uid))
            
            tr_grandparents.append(td_grandparents)  
            
            td = HTMLgen.TD()          
            td.append(tr_grandparents)
            tr.append(td)

            url = "%s?action=show&uid=%s"%(SCRIPT, idict['pere'])
            td = HTMLgen.TD()
            #PL text = "Ojciec" 
            text = self.c_lang(  "Father")
            td.append(self.one_person(' %s '%text, url, pere_dict))
            tr.append(td)
    
        else: # Dadaj tate
            if True or self.check_permission_to_edit(idict):
                url = "%s?action=add_parent&genre=1&uid=%s"%(SCRIPT,uid)
                
                text1 = self.c_lang("Add")
                text2 = self.c_lang("Father genitive")
                href = HTMLgen.Href( url, " %s %s %s"%(text1, self.kogo(idict), text2))
                div = HTMLgen.Div( id ="add_parent_key")
                td = HTMLgen.TD()
                div.append(href)
                td.append(div)
                tr.append(td)
                url = "%s?action=link_papa&genre=1&nom=%s&uid=%s&dob=%s"%(SCRIPT, idict.value('nom'),uid,idict.value('naissance'))
                text1 = self.c_lang("Link")
                text2 = self.c_lang("Father genitive") 
                href = HTMLgen.Href( url, " %s %s %s"%(text1, self.kogo(idict), text2))
                div = HTMLgen.Div( id ="add_parent_key")
                td = HTMLgen.TD()
                div.append(href)
                td.append(div)
                tr.append(td)
        
        mere_dict = self.get_dict(int(idict.value('mere')))
        if not mere_dict is None:
            # tr_grandparents= HTMLgen.TR()
            td_grandparents= HTMLgen.TD()
            
            text = "maternal"
            td_grandparents.append(self.get_tabela_grandparents(text, mere_dict,  uid))            
            tr_grandparents.append(td_grandparents)  
 
            
            url = "%s?action=show&uid=%s"%(SCRIPT, idict.value('mere'))
            td = HTMLgen.TD()
            
            #PL text = "Matka"
            text = self.c_lang( "Mother")
            td.append(self.one_person(text, url, mere_dict))            
            tr.append(td)
        else: # Dadaj mame
            if self.check_permission_to_edit(idict):
                url = "%s?action=add_parent&genre=0&uid=%s"%(SCRIPT,uid)
                #PL href = HTMLgen.Href( url, "Dodaj Matke %s "%(self.kogo(idict)))
                
                text1 = self.c_lang("Add")
                text2 = self.c_lang("Mother genitive")
                href = HTMLgen.Href( url,  " %s %s %s"%(text1, self.kogo(idict),text2))
                div = HTMLgen.Div( id ="add_parent_key")
                td = HTMLgen.TD()
                div.append(href)
                td.append(div)
                tr.append(td)

                url = "%s?action=link_mama&genre=0&nom=%s&uid=%s&dob=%s"%(SCRIPT, idict.value('nom'),uid,idict.value('naissance'))
                #PL href = HTMLgen.Href( url, "Dolacz Matke %s "%(self.kogo(idict)))
                text1 = self.c_lang("Link")
                text2 = self.c_lang("Mother genitive")
                href = HTMLgen.Href( url, " %s %s %s"%(text1, self.kogo(idict), text2))  
                div = HTMLgen.Div( id ="add_parent_key")
                td = HTMLgen.TD()
                div.append(href)
                td.append(div)
                tr.append(td)
        
        table.append(tr)
            
        dedit.append(table)
        return dedit
    
    def get_tabela_children(self, idict, uid, picture_scale, recursive_counter ):
    
        birthday_soon_image = ""
        birthday_today_image = ""
        # Wyszukaj grand children 
        sql = "SELECT * from %s WHERE pere='%s' OR mere='%s' ORDER BY  `naissance` ASC ;"%(TABLE, uid, uid) 
        gr_children = self.sql_execute(sql)
        
        #return empty when no children found 
        if len(gr_children) == 0: 
            return ""
        
        counter = recursive_counter - 1
        if counter < 0: 
            return ""
        
        if counter % 2 == 0:  
            children_div = HTMLgen.Div(id = 'children_odd')
        else:
            children_div = HTMLgen.Div(id = 'children')
        
        scale = picture_scale * 0.8  
        width = int(3*scale)
        height =int(4*scale)
 
        
        td1 = HTMLgen.TD()      
        # td1.append(uid) 
        td = HTMLgen.TD()
        tr = HTMLgen.TR()  
        tb = HTMLgen.TableLite(border=0, cell_spacing=1, width=None, body=[])
        for child in gr_children:
            self.descendants_counter += 1
            child_uid = child[1]
            child_name ="%s "%(child[3])  # imie 
            url = "%s?action=show&uid=%s"%(SCRIPT,child_uid)
            href1 = HTMLgen.Href( url, child_name)
            
            child_uid = child[1]
            child_name =" %s"%(child[4]) #nazwisko
            url = "%s?action=show&uid=%s"%(SCRIPT,child_uid)
            href2 = HTMLgen.Href( url, child_name)

            child_dict = self.get_dict(child_uid)
            # image = HTMLgen.Image('%s'%( self.get_picture(child_dict)), width="%s"%width, height="%s"%height)
            image = HTMLgen.Image('%s'%( self.get_picture(child_dict)), width="", height="%s"%height)
            href_image = HTMLgen.Href( url, image)

            tr = HTMLgen.TR()
            td_text = HTMLgen.TD()
            td_image = HTMLgen.TD()
            td = HTMLgen.TD()

            
            td_text.append(href1)
            td_text.append(HTMLgen.BR())
            td_text.append(href2)    

            
            div = HTMLgen.Div(id = 'dates')
            
            # PLACE BIRTHDAY TAG 
            dob = child_dict.dob()
            if dob != "": 
                div.append(dob)
                div.append(HTMLgen.BR())
            
            # PLACE AGE TAG   
            dod = child_dict.dod()
            if dod == "":
                age, days_since_bday  = self.get_person_age_in_days(child_dict) 
                if age == "":
                    pass
                else:
                    age = int(age) / 365
                
                # div.append(" (%s)[%s] "%(age, days_since_bday))  # Show days to Birthday
                div.append(" (%s) "%(age))  
                
                if days_since_bday > -10 and days_since_bday < 3: 
                    birthday_soon_image = HTMLgen.Image('%s/%s%s'%(IMAGES, self.theme['directory'], "BIRTHDAY_SOON.png"), width="", height="%s"%height)
                else: 
                    birthday_soon_image = ""
                
                if days_since_bday == 0 : 
                    birthday_today_image = HTMLgen.Image('%s/%s%s'%(IMAGES, self.theme['directory'], "BIRTHDAY_TODAY.png"), width="", height="%s"%height)
                else: 
                    birthday_today_image = ""                
                
            else:    
                dod = child_dict.dod()
                div.append(dod) 
                
            td_text.append(div)

            
            td_image.append(href_image)
            td_image.append(birthday_soon_image)
            td_image.append(birthday_today_image)

            tr.append(td_text)
            tr.append(td_image)              
            td = self.get_tabela_children(child, child_uid, scale, counter)  # recursive 
            tr.append(td)
            tb.append(tr)
        
        children_div(tb)        
        td1.append(children_div)

        return(td1)    
            

    def kogo(self, idict):
        
        first_name = idict.value('prenom')
        
        if self.prefered_language == "EN":
            return " %s's "%first_name
        
        elif self.prefered_language == "PL": 
            if idict.g(): 
                if first_name[-2:] == ['eł'] :   # if first_name Paweł   
                    return "%ła"%(first_name[:-2])   # return Pawła

                if first_name[-2:] == ['er'] :   # if first_name Aleksander   
                    return "%sra"%(first_name[:-2])   # return Aleksandra                
                
                if first_name[-2:] in ['ek']:   # if first_name in ['Jacek','Wojtek','Zbyszek','Przemek']:  
                    return "%ska"%(first_name[:-2])   # return Jacka Wojtka Zbyszka Przemka
                
                if first_name[-1:] in ['y']:   # if first_name in ['Jerzy','Wincenty','Konstanty',itp]: 
                    return "%sego"%(first_name[:-1]) #Jerzego, Wincentego, Konstantego , Cezarego 

                # Hipolita , Adama, Izydora, Romana, Piotra, Przemysława, Jakuba, Oskara             
                return "%sa"%(first_name)
            
            else: 
                
                if first_name[-2:] in ['na', 'fa', 'pa', 'ra', 'ta', 'wa', 'za']:  #  Krystyna, Bożena , Anna, Paulina, Honorata, Zuza, Stanisława, 
                    return "%sy"%(first_name[:-1])  #  Krystyny , Bożeny  , Anny , Pauliny 
                        
                return "%si"%(first_name[:-1]) # Alicji , Dominiki, Agnieszki , Jadwigi , Zofii, Maria, Marii
            
        return first_name   


    def get_connect_child(self, uid, idict):
        if idict.g():
            url = "%s?action=link_child&uid=%s&nom=%s"%(SCRIPT, uid, idict.value('nom'))
        else:
            spouse_dict = self.get_dict(int(idict.value('conjoint')))
            if spouse_dict is None or spouse_dict['nom'] is None:
                url = "%s?action=link_child&uid=%s&nom=%s"%(SCRIPT, uid, idict.value('nom'))
            else:
                url = "%s?action=link_child&uid=%s&nom=%s"%(SCRIPT, uid, spouse_dict['nom'])
        text = self.c_lang( "Link Descendant"  )      
        href = HTMLgen.Href( url, " %s "%text)
        td = HTMLgen.TD()
        td.append(href)
        tr = HTMLgen.TR()
        tr.append(td)
        return tr
        #^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    

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

    def get_tabela_spouse(self, idict, uid):
        dedit = HTMLgen.Div(id = 'spouse')
        table = HTMLgen.TableLite(border=0, cell_spacing=1, width=None, body=[])
        if int(idict.value('conjoint')) >0:
            spouse_dict = self.get_dict(int(idict['conjoint']))
            url = "%s?action=show&uid=%s"%(SCRIPT, idict['conjoint'])
    
            if not idict.g():
                text ="M\xb1\xbf"
                text = self.c_lang("Husband") 
                href = HTMLgen.Href( url, "%s: %s %s"%(text, spouse_dict['prenom'], spouse_dict['nom']))
            else:
                text = "\xafona"
                text = self.c_lang( "Wife")
                href = HTMLgen.Href( url, "%s: %s %s"%(text, spouse_dict['prenom'], spouse_dict['nom']))
    
            tr = HTMLgen.TR()
            td = HTMLgen.TD()
            td.append(href)
            tr.append(td)


            # image = HTMLgen.Image('%s'%( self.get_picture(spouse_dict)), width="%s"%(3*IMAGE_PICTURE_SIZE), height="%s"%(4*IMAGE_PICTURE_SIZE))
            image = HTMLgen.Image('%s'%( self.get_picture(spouse_dict)), width="", height="%s"%(4*IMAGE_PICTURE_SIZE))
            href = HTMLgen.Href( url, image)
            td = HTMLgen.TD()
            td.append(href)
            tr.append(td)

            table.append(tr)
        else: # Dadaj spouse
            genre = 1
            text = self.c_lang( "husband genitive")
            spouse = text
            if idict.g(): 
                genre =0
                text = self.c_lang( "wife genitive")
                #PL text = "\xbfone"
                spouse = text
        
            # To show edit link" only when person is more than 
            (age, dummy) = self.get_person_age_in_days(idict)
            if self.check_permission_to_edit(idict) and age > 5800:
                
                url = "%s?action=add_spouse&uid=%s&genre=%s"%(SCRIPT, uid, genre)
                text = self.c_lang( "Add")
                href = HTMLgen.Href( url, "%s %s %s "%(text, spouse, self.kogo(idict)))
                tr = HTMLgen.TR()
                td = HTMLgen.TD()
                div = HTMLgen.Div( id = "add_spouse_key") 
                div.append(href)
                td.append(div)
                tr.append(td)

                url = "%s?action=link_spouse&uid=%s&genre=%s"%(SCRIPT, uid, genre)
                text = self.c_lang( "Link")
                href = HTMLgen.Href( url, "%s %s %s "%(text, spouse, self.kogo(idict)))
                td = HTMLgen.TD()
                div = HTMLgen.Div( id = "add_spouse_key") 
                div.append(href)
                td.append(div)
                tr.append(td)
                table.append(tr)
    
        dedit.append(table)
        return dedit

    def show_pictures(self, idict ):

        import os
        text = ''
        id = idict.value('id')
        listdir = os.listdir(PATH_TO_PICTURES)
        listdir.sort()
        pictures_container = HTMLgen.Div(id = 'pictures_container')
        for fname in listdir:
           
            if not os.path.isfile(os.path.join(PATH_TO_PICTURES,fname)): continue
            if not (fname.endswith('.JPG') or fname.endswith('.jpg')) : continue
            if not (fname.startswith('%s_'%id)) and not(fname.startswith('%s.'%id)): continue
            if fname.startswith('.') : continue
            path = '%s/%s'%(PATH_TO_PICTURES, fname)
            image = HTMLgen.Image('%s'%(path), width="", height="200")
            url ='%s/%s'%(PATH_TO_PICTURES, fname)
            href = HTMLgen.Href(url, image, target="new")
            pictures_container.append(href)
        return pictures_container

    
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
        
    
    def get_picture(self, idict):
      
        picture_path_from_my_sql = ''
        if idict is not None:
            picture_path_from_mysql = "%s/%s"%(PATH_TO_PICTURES, str(idict.value('picture_id')))
            picture_path = picture_path_from_mysql          
            if os.path.isfile(picture_path):
                return picture_path 
                   
            picture_path = "%s/%s.jpg"%(PATH_TO_PICTURES, idict.value('id'))            
            if os.path.isfile(picture_path):                 
                return picture_path
        if idict.g(): 
            picture_path = "%s/%s%s"%(IMAGES, self.theme['directory'], self.theme['img_male'] )    # smiley.gif 
        else:
            picture_path = "%s/%s%s"%(IMAGES, self.theme['directory'], self.theme['img_female'] )   
            
        person_age, days_since_bday = self.get_person_age_in_days(idict)
                                      
        if person_age <  self.theme['age_of_child']:  #  AGE_OF_GROWNUP :    # 3650 is 11 years
            if idict.g(): 
                picture_path = "%s/%s%s"%(IMAGES, self.theme['directory'], self.theme['img_boy'])  # smiley.gif 
            else:
                picture_path = "%s/%s%s"%(IMAGES, self.theme['directory'], self.theme['img_girl'])   
                
        if person_age < self.theme['age_of_infant']: # AGE_OF_CHILD:   # in days
            picture_path = "%s/%s%s"%(IMAGES, self.theme['directory'], self.theme['img_infant'] ) 
            
        return picture_path
    
    def get_picture_upload_form(self, idict):
        # Formularz do wysyłania zdjęć pojawi się tylko wtedy gdy masz pozwolenie na edycję
        # form to upload pictures 
        td_picture_form = HTMLgen.TD(border="0")
        form = HTMLgen.Form( enctype="multipart/form-data", cgi="%s"%SCRIPT)
        form.append( HTMLgen.BR())
        form.append( HTMLgen.Input( type='file', name="file"))
        form.append( HTMLgen.Input( type='hidden', name="file_name", value="%s"%(idict.value('id'))))
        form.append( HTMLgen.Input( type='hidden', name="uid", value="%s"%(idict.value('uid'))))
        form.append( HTMLgen.Input( type='hidden', name="prefix", value="YES"))
        form.append( HTMLgen.Input( type='hidden', name="profile_picture", value="YES"))

        dd_upload_picture = HTMLgen.Div(id = 'upload')
        text = self.c_lang("change profile picture")      
        td_picture_form.append(text)
        dd_upload_picture.append(form)
        td_picture_form.append(dd_upload_picture)
        
        div = HTMLgen.Div()
        div.append(self.c_lang("Instructions"))
        
                                       
        td_picture_form.append(div)            


        any_picture_form = HTMLgen.Form( enctype="multipart/form-data", cgi="%s"%SCRIPT)
        any_picture_form.append( HTMLgen.BR())
        any_picture_form.append( HTMLgen.Input( type='file', name="file"))
        any_picture_form.append( HTMLgen.Input( type='hidden', name="file_name", value="%s"%(idict.value('id'))))
        any_picture_form.append( HTMLgen.Input( type='hidden', name="uid", value="%s"%(idict.value('uid'))))
        any_picture_form.append( HTMLgen.Input( type='hidden', name="prefix", value="YES"))
        any_picture_form.append( HTMLgen.Input( type='hidden', name="profile_picture", value="NO"))

        dd_upload_any_picture = HTMLgen.Div(id = 'upload')

        td_picture_form.append(HTMLgen.BR())
        
        text = self.c_lang("upload any picture")
        td_picture_form.append(text)
        
        dd_upload_any_picture.append(any_picture_form)
        td_picture_form.append(dd_upload_any_picture)
        
        return (td_picture_form)

    def show_item(self, uid, owner_uid):
    
        dedit = HTMLgen.Div(id = 'show')
        dedit_item = HTMLgen.Div(id = 'item')
        
        
        dedit_picture = HTMLgen.Div(id = 'picture_item')
        table_big = HTMLgen.TableLite(border=0, cell_spacing=1, heading=self.column_names[1:], width=None, body=[])        
        table = HTMLgen.TableLite(border=0, cell_spacing=1, heading=self.column_names[1:], width=None, body=[])
        table_with_picture = HTMLgen.TableLite(border=0, cell_spacing=1, heading=self.column_names[1:], width=None, body=[])
    
        idict = Dict()
        
        sql = "SELECT * FROM %s WHERE uid ='%s'"%(TABLE, uid)
        row = self.sql_execute(sql)
        
        self.dict = self.convert_sqlrow_to_dict(row[0])
        
        i = 0
        values = row[0][0:]
        for c in self.column_names[0:]:
            v = values[i]
            if (v is None) or (v == 'None') : v = ""
            idict[c] =  v
            i += 1 
            if c in hidden or idict.value(c) == '':
                pass
            else:
                tr = HTMLgen.TR()
                td = HTMLgen.TD( align="right" )
                text = self.c_lang(c)
                td.append("%s :"%(text))
                tr.append(td)
                # Szerokosc pola danych 300, kolor szary
                td = HTMLgen.TD(bgcolor="#FFFFFF" , width="200")
                line_to_show = "%s"%v
                if c in ['nom','prenom']: 
                    lshow = HTMLgen.Div( id = "fontsize")
                    lshow.append(line_to_show) 
                    line_to_show=lshow
                if c == 'notes': 
                    line_to_show = HTMLgen.Textarea( rows=2, cols=40, text=v)
                 
                if c == 'phone': 
                    line_to_show = ""
                    if idict.value('phone') != "":   
                        phone_number = idict.value('phone')
                        url = "tel:%s"%phone_number
                        image_path = "%s/%sb_phone.png"%(IMAGES, self.theme['directory'] )
                        # icon = HTMLgen.Image(class='icon', src= image, width="30", height="30")
                        icon = HTMLgen.Image( image_path, width="30", height="30", alt="Make A Phone Call :")
                        href = HTMLgen.Href(url, icon, target="new")
                        td.append(href)
                        href = HTMLgen.Href(url, phone_number, target="new")
                        line_to_show = href
                
                if c == 'email': 
                    line_to_show = ""
                    if idict.value('email') != "":
                        to_addr = idict.value('email')
                        if to_addr.find('@') > 0 :
                            full_name = "%s %s"%(idict.value('prenom'), idict.value('nom'))
                            msg = "Hello %s"%full_name                     
                            mail = HTMLGen.MailTo( address="%s"%(to_addr), subject=msg, body=msg, text="%s"%(to_addr))
                            line_to_show = mail
                        else: 
                            line_to_show = to_addr        
                    
                if c == 'facebook': 
                    line_to_show = ""
                    if idict.value('facebook') != "":    
                        url = "http://www.facebook.com/%s"%(idict.value('facebook'))
                        image = "%s/%sfacebook.png"%(IMAGES, self.theme['directory'] )
                        icon = HTMLgen.Image( image, width="30", height="30", alt="Open Facebook")
                        href = HTMLgen.Href(url, icon, target="popup", onClick="window.open('%s','name','width=900,height=600')"%url)
                        line_to_show = href
                    
                if c == 'geo_location': 
                    string = idict.value('geo_location')
                    # ?q=loc:32.9091722,-117.203475
                    # https://www.google.com/maps?q=loc:32.9091722,-117.203475
                    # geolocation string manipulation goes here 
                    
                    url = "http://www.google.com/maps?q=loc:%s"%(string)
                    image = "%s/%sb_globe.png"%(IMAGES, self.theme['directory'] )
                    icon = HTMLgen.Image( image, width="30", height="30", alt="Open Location in Google")
                    href = HTMLgen.Href(url, icon, target="popup", onClick="window.open('%s','name','width=900,height=600')"%url)
                    line_to_show = href    

                td.append(line_to_show)
                tr.append(td)
                table.append(tr)
    
        # Tu dodaje się stopien pokrewieństwa / relation
        r = Relations.Relation()
        relation = r.get_relationship(self.login_dict.value('uid'), idict.value('uid'))    
        ## . relation = "%s"%idict['uid'] # '.keys()
        relation = self.label_cleanup(relation)    
        
        if relation <> '':   
            relation_translated = " %s "%(self.c_lang(relation))
            dd_relation = HTMLgen.Div(id = 'relation')
            
            dd_relation.append(relation_translated)
            
            if self.rate > 0:  # Showing rate of relationship
                dd_rate = HTMLgen.Div(id = 'rate')
                relative = self.c_lang('relative')
                if not idict.value('genre') :  
                    relative = self.c_lang('relativa')
                        
                dd_rate.append("1/%s %s"%(self.rate, relative ))
                dd_relation.append(dd_rate)
                logger.info ("INFO: Found relation: [%s] translated to >%s< for %s"%(relation, relation_translated, idict.value('uid')))
            

            #  dd_relation.append("{%s}"%relation)  # Relation not translated
            
            # DEBUG 
            # dd_relation.append(self.theme['age_of_child']) 
            
            # font = HTMLgen.Font(size="20")
            td = HTMLgen.TD( align="left", colspan="3", bgcolor="#88FF88" )
            tr = HTMLgen.TR()
            td.append(dd_relation)
            
            tr.append(td)
            table_with_picture.append(tr)
            
        # Tu dadaje sie zdjecie
        # image = HTMLgen.Image('%s'%(self.get_picture(idict)), width="150", height="200")
        image = HTMLgen.Image('%s'%(self.get_picture(idict)), width="", height="200")
        # Zmień kolor ramki jeżeli osoba ma wpisaną datę śmierci 
        if idict.value('deces') == '':
            frame_color = "#FFFFFF"
        else:
            frame_color = "#9A9A9A"

        url = "%s?action=show_pictures&uid=%s"%(SCRIPT,idict.value('uid'))
        icon = image 
        href1 = HTMLgen.Href(url, icon, target="new")

        # dedit_picture.append(image)
        dedit_picture.append(href1)

        td_picture = HTMLgen.TD( align="center", bgcolor="%s"%frame_color, width="180", height="240")
        td_picture_form = HTMLgen.TD(border="0")
        td_picture.append(dedit_picture)
    
        tr = HTMLgen.TR()
        td = HTMLgen.TD(bgcolor="#EEEEEE")
        td.append(table)
        tr.append(td)
        tr.append(td_picture)
        
        if self.check_permission_to_edit(idict):       
            # Show pictures upload only when you have permission to edit
            td_picture_form = self.get_picture_upload_form(idict)
            
        tr.append(td_picture_form)
        
        table_with_picture.append(tr)
        #KP dedit_item.append(table_with_picture)
    
      
        table_footer = HTMLgen.TableLite(border=0, cell_spacing=1, heading=self.column_names[1:], width=None, body=[])
        
        # Link to create invitations 
        tr = HTMLgen.TR()
        td = HTMLgen.TD( align="left" )
        if idict.value('deces') == "":
            name = "%s %s"%(idict.value('prenom'), idict.value('nom'))
            email = idict.value('email') 
            if "@" in email: 
                if True:
                    text = ""
                    sql = "SELECT * FROM %s WHERE `sender_uid`=%s AND `recipient_uid`=%s ORDER BY `id` DESC LIMIT 1;"%(EMAILS_TO_SEND_TABLE, self.login_dict.value('uid'), idict.value('uid'))
                    
                    row = self.sql_execute(sql)
                    if len(row) >0:
                        row = row[0]
                        date = row[4]
                        if date != "": 
                            text = self.c_lang("invitation was prepared on")
                            text = "%s %s"%(text, date)
                            li = HTMLGen.LI()
                            li.append(text)
                            td.append(li) 

                        date = row[5]
                        if date != "": 
                            text = self.c_lang("invitation was sent on")
                            text = "%s %s"%(text, date) 
                            li = HTMLGen.LI()
                            li.append(text)
                            td.append(li)                           

                        date = row[6]
                        if date != "": 
                            text = self.c_lang("invitation was accepted on")
                            text = "%s %s"%(text, date)  
                            li = HTMLGen.LI()
                            li.append(text)
                            td.append(li)                                
                    
                    if text == "":
                        url = "%s?action=invite&uid=%s"%(SCRIPT, idict.value('uid'))
                        text = "%s %s %s"%(self.c_lang("click here to send invite to"), self.kogo(idict), self.c_lang("by email"))
                        href = HTMLgen.Href( url, text)
                        
                        li = HTMLGen.LI()
                        li.append(href)
                        td.append(li) 
                        # td.append(href)    
                        td.append(HTMLgen.BR())
                        
                    tr.append(td)
                    table_footer.append(tr)
                # except:
                else: 
                    text = self.c_lang("can not send invitation")
                    li = HTMLGen.LI()
                    li.append(text)
                    td.append(li)
                    tr.append(td)
                    table_footer.append(tr)
            else: 
                text1 = self.c_lang("give email address to")
                text2 = self.c_lang("to be able send him invitation")
                text = "%s %s %s"%(text1, name, text2)
                li = HTMLGen.LI()
                li.append(text)
                td.append(li)
                tr.append(td)
                table_footer.append(tr)
        else:    
            li = HTMLGen.LI()
            li.append(self.c_lang("this person is not receiving emails"))
            td.append(li)
            tr.append(td)
            table_footer.append(tr)
            
        
        
        tr = HTMLgen.TR()
        if idict.value('owner_uid') >0 :
            try:
                td = HTMLgen.TD( align="left" )
                owner_dict= self.get_dict( idict['owner_uid'])
                url = "%s?action=show&uid=%s"%(SCRIPT, owner_dict.value('uid'))
                name = "%s %s"%(owner_dict.value('prenom'), owner_dict.value('nom'))
                href = HTMLgen.Href( url, name)
                
                text = self.c_lang("this record is owned by")
                li = HTMLGen.LI()
                li.append(" %s "%text)
                li.append(href )
                
                td.append(li)
                tr.append(td)
                table_footer.append(tr)
            except:
                # You are here because your owner does not exist
                pass
            
        tr = HTMLgen.TR()
        td = HTMLgen.TD( align="left" )
        
        #PL td.append("wpis ostatnio zmieniony : %s"%(idict.value('change_time')))
        text = self.c_lang("this record was last updated on")  
        li = HTMLGen.LI()
        li.append("%s : %s"%(text, idict.value('change_time')))
        td.append(li)
        
        tr.append(td)
        table_footer.append(tr)
        
        if not self.owner_uid is None:  # To show edit link"
            if self.check_permission_to_edit(idict):
                url = "%s?action=edit&uid=%s&owner_uid=%s"%(SCRIPT,uid, self.owner_uid)
                text = self.c_lang( "Editing is allowed")
                
                msg = " %s : %s"%(text, self.msg)
                href = HTMLgen.Href(url, msg, target="popup", onClick="window.open('%s','name','width=900,height=600')"%url)
                tr = HTMLgen.TR()
                td = HTMLgen.TD( align="left" )
                td.append(href)
                tr.append(td)
                table_footer.append(tr)
                to_addr = idict.value('email')
#                if  self.am_i_superuser() :
#                    uid = str(idict.value('uid'))
#                    key = self.get_key(uid)
#                    #PL msg = 'Identyfikator: %s Klucz: %s  '%(uid, key) 
#                    text = self.c_lang( "Identifier"   )       
#                    text1 = self.c_lang("Key")
#                    msg = '%s: %s %s: %s  '%(text, uid, text1, key) 
#                    tr = HTMLgen.TR()
#                    td = HTMLgen.TD( align="left" )
#                    td.append(msg)
#                    tr.append(td)
#                    table_footer.append(tr)
#                    
#                    if  to_addr.find('@') > 0 :
#                        dedit_item.append(HTMLgen.BR())
#                        imie = "%s %s"%(idict.value('prenom'), idict.value('nom'))
#                        ID = idict.value('uid')
#                        key = self.get_key(ID)
#                        msg = self.get_message(imie, ID, self.get_key(ID))
#                        
#                        text = self.c_lang( "Invitation to the Tree")
#                        text2 = self.c_lang("send email to")
#                        mail = HTMLGen.MailTo( address="%s"%(to_addr), subject=text, body=msg, text="%s %s"%(text2, imie))
#                        tr = HTMLgen.TR()
#                        td = HTMLgen.TD( align="left" )
#                        td.append(mail)
#                        tr.append(td)
#                        table_footer.append(tr)
#                        
#                    url = "%s?action=login&uid=%s&key=%s"%(SCRIPT, uid, key)
#                                              
#                    text = "Zmiana loginu"
#                    text = self.c_lang( "Change the login")
#                    li = HTMLGen.LI()
#                                              
#                    href = HTMLgen.Href( url, text)
#                    li.append(href)
#                    
#                    tr = HTMLgen.TR()
#                    td = HTMLgen.TD( align="left" )
#                    td.append(li)
#                    tr.append(td)
#                    table_footer.append(tr)
            else:
                tr = HTMLgen.TR()
                td = HTMLgen.TD( align="left" )
                
                #PL text = "Edycja nie jest dozwolona:"                              
                text = self.c_lang( "Edition is not allowed here"  )                          
                td.append(text) 
                tr.append(td)
                table_footer.append(tr)
                # dedit_item.append("%s<>%s"%( idict.value('owner_uid'), self.owner_uid))
        else:
            # dedit_item.append("%s<>%s"%( idict.value('owner_uid'), self.owner_uid))
            tr = HTMLgen.TR()
            td = HTMLgen.TD( align="left" )
            #PL text = "Edycja nie jest dozwolona:"                              
            text = self.c_lang( "Edition is not allowed here")                              
            td.append(text) 
            tr.append(td)
            table_footer.append(tr)
                
        tr = HTMLgen.TR()        
        td = HTMLgen.TD( align="left", colspan="3" )
        
        
#        button = HTMLGen.Button(type="button", Class="collapsible")
#        button.append(self.c_lang("details"))
#        td.append(button)
#        div_collapsible = HTMLgen.Div( id = 'content' , style="display: none" ) # Make collapsible initially collapsed
#        div_collapsible.append(table_footer)
#        td.append(div_collapsible)
        
        
        # td.append(table_footer)
        tr.append(td)
        
        td = HTMLgen.TD( align="left" , colspan="2" )
         
        table_with_picture.append(tr)
                
        dedit_item.append(table_with_picture)  
                                 
    
        tabela_rodzice = self.get_tabela_rodzice(idict, uid)
        dedit.append(tabela_rodzice)
    
        tabela_spouse = self.get_tabela_spouse(idict, uid)
        dedit.append(tabela_spouse)
        
        dedit.append(dedit_item)
        
        self.descendants_counter =0 
               
        return dedit

    def get_add_chilren_table(self, uid, idict):
        table =""
        (age, dummy) = self.get_person_age_in_days(idict)
        if self.check_permission_to_edit(idict) and age > 5800:
            
            table = HTMLgen.TableLite(border=0, cell_spacing=1, width=None, body=[])
            url = "%s?action=add_child&uid=%s&genre=0"%(SCRIPT, uid)
            #PL href = HTMLgen.Href( url, "dodaj c\xf3rke %s (+)"%(self.kogo(idict)))
            text1 = self.c_lang("Add")
            text2 = self.c_lang("daughter genitive")
            href = HTMLgen.Href( url, " %s %s %s"%(text1, self.kogo(idict), text2))
            tr = HTMLgen.TR()
            td = HTMLgen.TD()
            div = HTMLgen.Div(id="add_child_key")
            div.append(href)
            td.append(div)
            tr.append(td)
            table.append(tr) 
            tr = HTMLgen.TR()
            url = "%s?action=add_child&uid=%s&genre=1"%(SCRIPT, uid)
            # href = HTMLgen.Href( url, "dodaj syna %s (+)"%(self.kogo(idict)))
            text1 = self.c_lang("Add")
            text2 = self.c_lang("son genitive")
            href = HTMLgen.Href( url, " %s %s %s"%(text1, self.kogo(idict), text2))
            td = HTMLgen.TD()
            div = HTMLgen.Div(id="add_child_key")
            div.append(href)
            td.append(div)
            tr.append(td)
            table.append(tr)
  
            # LINKING CHILD IS ANABLE ONLY FOR SUPER USERS 
#            if self.am_i_superuser():
#                tr = self.get_connect_child(uid, idict)
#                table.append(tr) 
        return table        
    
    
#    def am_i_superuser(self):
#        return False
#        superuser = self.login_dict.value('SUPERUSER')
#        if superuser == "1":
#            return True
#        else:
#            return False
#        return False

    def calculate_date( date, years):
        year = str(int(date[:4]) + years)
        return "%s%s"%(year, data[4:])





    def check_permission_to_edit(self, person):
        return False 
        self.msg = ''
        me = self.login_dict
        if  person.value('uid') == me.value('uid'):
            text = self.c_lang( "This is You" )
            self.msg += "%s "%(text)
            return True

        if  person.value('uid') == me.papa():
            text = self.c_lang( "This is your Father"  )
            self.msg += "%s "%(text)
            return True

        if  person.value('uid') == me.mama():
            text = self.c_lang( "This is your Mother"  )                                 
            self.msg += "%s "%(text)
            return True

        if  person.value('uid') == me.conj():
            text = self.c_lang( "This is your husband or wife")                                                                  
            self.msg += "%s "%(text)
            return True

        if  person.papa() == me.value('uid'):
            text = self.c_lang( "You are logged as father of this person"  )                                 
            self.msg += "%s. "%(text)
            return True

        if  person.mama() == me.value('uid'):
            text = self.c_lang( "You are logged as mother of this person" )                                  
            self.msg += "%s "%(text)
            return True

        if  person.value('owner_uid') == me.value('uid'):
            text = self.c_lang( "You are the owner of this record" )                                  
            self.msg += "%s. "%(text)
            return True

        if  person.value('owner_uid') == self.owner_uid:
            text = self.c_lang( "You presented correct id" )                                  
            self.msg += " %s %s %s"%(text, person.value('owner_uid'), self.owner_uid)
            return True

#        if  self.am_i_superuser():
#            text = self.c_lang( "as SUPERUSER"  )                                 
#            self.msg += "%s "%(text)
#            return True

        return False

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

        
        
    
    def show_list(self, rows):
      
        table = HTMLgen.TableLite(border=0, cell_spacing=1, width=None, body=[])

        for row in rows:
            reaction = 'show'

            person = self.convert_sqlrow_to_dict(row)
            url = "?action=%s&uid=%s"%('show', person.value('uid'))
            
            tr = HTMLgen.TR( )
            td = HTMLgen.TD( align="right" )
            s = "%s %s"%(person['prenom'], person['nom'])
            href = HTMLgen.Href( url, s)
            td.append(href)
            date = "%s"%(person['naissance'])
            ddate = HTMLgen.Div(id = 'date')
            ddate.append(date)
            td.append(ddate)
            tr.append(td)
            
            td = HTMLgen.TD( align="right" )
            image = HTMLgen.Image('%s'%( self.get_picture(person)), width="30", height="40")
            href = HTMLgen.Href( url, image)
            td.append(href)
            tr.append(td)

            td = HTMLgen.TD( align="right" )
            changer = self.get_dict(person.value('owner_uid'))
            
            td = HTMLgen.TD( align="right" )
            if changer is not None:
                text = self.c_lang( "modified by")
                s = "%s %s %s %s"%(text, changer.value('prenom'), changer.value('nom'), person.value('change_time'))
            else:
                text = self.c_lang( "modified by Anonimous Anonim")
                s = "%s %s"%(text, person.value('change_time'))
            href = HTMLgen.Href( url, s)
            
            td.append(href)
            tr.append(td)
            
            table.append(tr)

        dresults = HTMLgen.Div(id = 'results')
        dresults.append(table)
        dedit = HTMLgen.Div(id = 'edit')
        dedit.append(dresults)
        return dedit

    def show_search_results(self, rows, action, genre, uid, prenom, nom , dob):
      
        table = HTMLgen.TableLite(border=0, cell_spacing=1, width=None, body=[])
        tr = HTMLgen.TR( )
        td = HTMLgen.TD( align="left" )
        #PL text = "imi\xea"        
        text = self.c_lang( "first name")

        td.append(text)
        tr.append(td)
        td = HTMLgen.TD( align="left" )
    
        #PL text = "nazwisko"
        text = self.c_lang( "last name")

        td.append(text)
        
        tr.append(td)
        table.append(tr)
        tr = HTMLgen.TR( )
        td = HTMLgen.TD( align="left" )
        prenom = HTMLgen.Input( type='text', name="prenom", value="%s"%prenom , size="10")
        td.append(prenom)
        tr.append(td)
        td = HTMLgen.TD( align="left" )
        nom    = HTMLgen.Input( type='text', name="nom",    value="%s"%nom ,    size="10")
        td.append(nom)
        tr.append(td)

        genre_tag      = HTMLgen.Input( type='hidden', name="genre",    value="%s"%(genre))
        uid_tag        = HTMLgen.Input( type='hidden', name="uid",    value="%s"%(uid))
        dob_tag        = HTMLgen.Input( type='hidden', name="dob",    value="%s"%(dob))
        action_input   = HTMLgen.Input( type='hidden', name="action", value="%s"%(action))
        
        text = self.c_lang( "search")
        form = HTMLgen.Form( cgi="%s"%SCRIPT, submit=HTMLgen.Input(type='submit',value=text))
        form.append(table)

        form.append(prenom)
        form.append(nom)
        form.append(uid_tag)
        form.append(genre_tag)
        form.append(dob_tag)
        form.append(action_input)

        dsearch = HTMLgen.Div(id = 'search')
        dsearch.append(form)

        table = HTMLgen.TableLite(border=0, cell_spacing=1, width=None, body=[])

        for row in rows:
            if action in ['link_mama','link_papa','link_child','link_spouse']:
                   reaction ="r%s"%action
            else:          
                   reaction = action

            person = self.convert_sqlrow_to_dict(row)
            url = "?action=%s&uid=%s&who=%s&genre=%s"%(reaction, uid, person['uid'],genre)
            
            tr = HTMLgen.TR( )
            td = HTMLgen.TD( align="right" )
            s = "%s %s"%(person['prenom'], person['nom'])
            href = HTMLgen.Href( url, s)
            td.append(href)
            date = "%s"%(person['naissance'])
            ddate = HTMLgen.Div(id = 'date')
            ddate.append(date)
            td.append(ddate)
            tr.append(td)
            
            td = HTMLgen.TD( align="right" )
            image = HTMLgen.Image('%s'%( self.get_picture(person)), width="30", height="40")
            href = HTMLgen.Href( url, image)
            td.append(href)
            tr.append(td)
            
            table.append(tr)

        dresults = HTMLgen.Div(id = 'results')
        dresults.append(table)
        dedit = HTMLgen.Div(id = 'edit')
        dedit.append(dsearch)
        dedit.append(dresults)
        return dedit

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
    
    def get_edit_form(self, idict, uid):
        table = HTMLgen.TableLite(border=0, cell_spacing=1, width=None, body=[])
        present_time_string = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
        
        hidden_items_list = hidden_for_editing 
        if self.is_it_myself(idict):
            hidden_items_list = hidden_for_editing_by_myself
        
#        if self.am_i_superuser(): 
#            hidden_items_list = hidden_for_editing_by_super      
        
        for c in self.column_names[0:]:
            if c in hidden_items_list:
                input = HTMLgen.Input( type='hidden', name="%s"%c, value="%s"%idict.value(c))
                if c == 'owner_uid':
                    if idict.value(c) == '':
                        # Mozesz zostac włascicielem wpisu tylko jezeli wpis nie ma zadnego wlasciciela
                        input = HTMLgen.Input( type='hidden', name="%s"%c, value="%s"%self.login_dict.value('uid'))
                    else:
                        # Jezeli własciciel juz jest musi pozostać taki jaki jest 
                        input = HTMLgen.Input( type='hidden', name="%s"%c, value="%s"%idict.value(c))
                if c == 'change_time':
                    input = HTMLgen.Input( type='hidden', name="%s"%c, value="%s"%present_time_string)
                table.append(input)
            else:
                tr = HTMLgen.TR( )
                td = HTMLgen.TD( align="right" )
                text = self.c_lang(c)
                s = "%s :"%(text)

                input = HTMLgen.Input( type='text', name="%s"%c, value="%s"%idict.value(c) , size="60")
                if c == 'notes':
                    input = HTMLgen.Textarea(name="%s"%c, rows=2, cols=60, text="%s"%idict.value(c))
                if c in ['naissance', 'deces'] and self.check_if_date_string_is_valid(idict.value(c), idict) : 
                    input = HTMLgen.Input( type='date', name="%s"%c, value="%s"%idict.value(c) , size="60")

                if c == 'change_time':
                    input = HTMLgen.Input( type='text', name="%s"%c, value="%s"%present_time_string)
                    
                if c == 'pref_lang':
                    #TODO create here proper selector with valid languages
                    # VALID_LANGUAGES = {"PL":"Polish", "EN":"English", "SP":"Spanish"}
                    language_code = idict.value(c)
                    if not language_code in VALID_LANGUAGES.keys():
                        language_code = DEFAULT_LANGUAGE
                        
                    data = []    
                    for key in VALID_LANGUAGES.keys():
                        data.append((self.c_lang(VALID_LANGUAGES[key]), key))  
                    input = HTMLgen.Select( name="%s"%c, data=data, selected="%s"%language_code, multiple=False, size="4")   

                if c == 'theme':
                    logger.debug("DEBUG: theme value from db %s"%idict.value(c))
                    if idict.value(c) == "": 
                        theme_code = 0 
                    else:    
                        theme_code = int(idict.value(c))
                    logger.debug("DEBUG: theme code %s"%theme_code)
                    logger.debug("DEBUG: themes.keys() %s"%str(self.themes.keys()))

                    if not theme_code in self.themes.keys():
                        theme_code = 0 
                        
                    data = []    
                    for key in self.themes.keys():
                        data.append((self.themes[key], "%s"%key))  
                    
                    input = HTMLgen.Select( name="%s"%c, data=data, selected="%s"%theme_code, multiple=False, size="%s"%(len(self.themes.keys())))   
                    


                td.append(s)
                tr.append(td)
                td = HTMLgen.TD()
        

                td.append(input)
                tr.append(td)
                table.append(tr)
                
        text = self.c_lang( "Save")
        form = HTMLgen.Form( cgi="%s"%SCRIPT, submit=HTMLgen.Input(type='submit',value=text))
        form.append(table)
        form.append(HTMLgen.BR())
        return form
    
    def get_translation_add_edit_form(self, dict):
        table = HTMLgen.TableLite(border=0, cell_spacing=1, width=None, body=[])
        present_time_string = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
        td = HTMLgen.TD( align="right")
        tr = HTMLgen.TR( )
        
        # DEBUG FOR TRANSLATIONS 
        # td.append(self.translator)
        
        # if dict['lang'] == '': 
        #    self.login_dict.value('pref_lang')
        
        for c in dict.keys():   
            if c in ['translation']:   
                input = HTMLgen.Input( type='text', name="%s"%c, value="%s"%dict[c] , size="60")
                td.append(input)
            elif c in ['Date']:
                input = HTMLgen.Input( type='hidden', name="%s"%c, value="%s"%present_time_string) 
                td.append(input)
            else:    
                input = HTMLgen.Input( type='hidden', name="%s"%c, value="%s"%dict[c]) 
                td.append(input)

        tr.append(td)
        table.append(tr)
                
        text = self.c_lang( "Save")
        form = HTMLgen.Form( cgi="%s"%SCRIPT, submit=HTMLgen.Input(type='submit',value=text))
        form.append(table)
        form.append(HTMLgen.Input( type='hidden', name="action", value="save_translation"))
        form.append(HTMLgen.BR())
        return form
    
    
    
    def edit_item(self, row, uid):
        idict = self.convert_sqlrow_to_dict(row[0])
        form = self.get_edit_form(idict, uid)
        form.append(HTMLgen.Input( type='hidden', name="action", value="save"))
        return self.get_rest_of_edit_form(form, idict)


    def get_rest_of_edit_form(self, form, idict):
        dedit_picture = HTMLgen.Div(id = 'picture_item')
        table_with_picture = HTMLgen.TableLite(border=0, cell_spacing=1, width=None, body=[])
    
        # Tu dadaje sie zdjecie
        # image = HTMLgen.Image('%s'%( self.get_picture(idict)), width="150", height="200")
        image = HTMLgen.Image('%s'%( self.get_picture(idict)), width="", height="200")
        frame_color = "#FFFFFF"
        dedit_picture.append(image)
        td_picture = HTMLgen.TD( align="center", bgcolor="%s"%frame_color, width="180", height="240")
        td_picture.append(dedit_picture)
    
        td=HTMLgen.TD(bgcolor = "#EEEEEE")
        td.append(form)
        tr=HTMLgen.TR()
        tr.append(td)
        tr.append(td_picture)
        table_with_picture.append(tr)
    
        # dedit.append(table)
        dedit = HTMLgen.Div(id = 'edit')
        dedit.append(table_with_picture)
        return dedit
    
    def add_parent(self, idict, uid):
        
        form = self.get_edit_form(idict, uid)

        form.append(HTMLgen.Input( type='hidden', name="child_uid", value="%s"%(uid)))
        form.append(HTMLgen.Input( type='hidden', name="action", value="save_parent"))
    
        return self.get_rest_of_edit_form(form, idict)

    def add_spouse(self, idict, uid):
        form = self.get_edit_form(idict, uid)

        form.append(HTMLgen.Input( type='hidden', name="spouse_uid", value="%s"%(uid)))
        form.append(HTMLgen.Input( type='hidden', name="action", value="save_spouse"))
    
        return self.get_rest_of_edit_form(form, idict)

    def add_child(self, idict, uid):
        form = self.get_edit_form(idict, uid)

        form.append(HTMLgen.Input( type='hidden', name="parent_uid", value="%s"%(uid)))
        form.append(HTMLgen.Input( type='hidden', name="action", value="save_child"))
    
        return self.get_rest_of_edit_form(form, idict)


    def format_as_table(self, x):
        t = []
        for i in x:
            t.append(i[0])

    def format_as_table(self, x):
        t = []
        for i in x:
            t.append(i[0])
        return t
       
    def update_results_table(self, con, ips, commands, db, doc):
        for key in db.keys():
            r = []
            d = []
            i,c = key.split('_')
            ip = ips[int(i)-1]           #  from key figure iut ip 
            command = commands[int(c)-1] #  from key figure out command
            new_result = db[key]  # The value retrieved from machine
            if new_result.startswith('ERROR: Could Not connect to Server'):
                doc.append(HTMLgen.PRE("Can not connect to server: %s"%(ip)))
                doc.append(HTMLgen.BR())
                continue
    
            new_result = new_result.replace("'","")
            # First find out the date of latest update for ip and command 
            sql="SELECT `date`,`result` FROM `results` WHERE `ip`='%s' AND `command`='%s' ORDER BY `date` DESC LIMIT 1;"%(ip,command)
            d = self.sql_execute(sql)

            result_previous=''
            if len(d) >= 1:
                # There is previous entry in databse for ip and command
                result_previous = d[0][1]
                # command was executed for ip last time at date
                # Now we are verifying if results were identical
                date = str(d[0][0])
                # Check if previous entry has result identical to new result
                sql="SELECT * FROM `results` WHERE `date`='%s' AND `ip`='%s' AND `command`='%s' AND `result`='%s';"%(date, ip,command, new_result)
                d = self.sql_execute(sql)
    
            if len(d) <= 0 :
                # Insert new result only when identical entry is not found 
                diff = compare(result_previous, new_result)
                date = datetime.datetime.now() # '2014-12-05 17:45:00' 
                date = str(date.strftime("%Y-%m-%d %H:%M:%S"))
                values ="'%s','%s','%s','%s', '%s'"%(date, ip,command, new_result, diff)
                sql="INSERT INTO results(date, ip, command, result, diff) VALUES(%s);"%(values)
                # print sql
                doc.append(HTMLgen.Heading(6,"Updated '%s' for %s with value:"%(command, ip)))
                doc.append(HTMLgen.PRE("%s"%(new_result)))
                self.sql_execute_and_commit(sql)
    
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
        
    
    def main(self, Sender, Recipient, emailid):
        
        self.login_dict = Recipient
        self.idict = Sender
        
        self.set_theme()
        # self.set_themes()
        self.prefered_language = Recipient.value('pref_lang')
        # print "PREFERED LANGUAGE %s"%self.prefered_language
        
        stylesheets = [ "%s/%sgenealogy_style.css"%(IMAGES, self.theme['directory']) , 
                       "https://cdn.jsdelivr.net/npm/bootstrap@5.3.1/dist/css/bootstrap.min.css"]
        
        # scripts = ["../js/sorttable.js", "../js/clickable.js"]
        
        
        style_for = ""

        # scripts = ["", ""]
        scripts = []
        meta = '<META HTTP-EQUIV="Content-Type" content="text/html; charset=ISO-8859-2">'
        meta = ''
    
        doc_simple  = HTMLGen.SimpleDocument(cgi="True", 
                                             screen_capture_injected="true", 
                                             meta=meta,
                                             title="Family Tree", 
                                             stylesheet=stylesheets, 
                                             script=scripts,
                                             style=style_for)
     
        doc = HTMLgen.Div(id = 'main')         

        sql = ''
        # Create instance of FieldStorage 
        # form = cgi.FieldStorage()       
    
        # wczytaj parametry zalogowanego uzytkownika
        
        login_uid = self.login_dict.value('uid')
        sql = "SELECT * FROM %s WHERE uid='%s';"%(TABLE, login_uid)
        row = self.sql_execute(sql)
        self.login_dict = self.convert_sqlrow_to_dict(row[0])
        
        
        uid = self.idict.value('uid')
        
        div = HTMLgen.Div(id = "item")
        
        
        if Sender.g():
            sender_he_she = "he"  #
        else:
            sender_he_she = "she"  # 
        
        if Recipient.g():
            recip_he_she = "male"   # Twoj 
        else:
            recip_he_she = "female" # Twoja
        
        br =HTMLgen.BR()
        
        # header = "%s %s zaprosi\xb3%s Ci\xea do rodzinnego drzewa genealogicznego DRZEWO.ME"%( Sender.value('prenom'), Sender.value('nom'), g)
        text = "%s invited you to the genealogy tree"%(sender_he_she)
        text = self.c_lang(text)
        header = "%s %s %s"%( Sender.value('prenom'), Sender.value('nom'), text)
        strong = HTMLgen.Strong(header)
        div.append(strong)  
        div.append(br)
        
        r = Relations.Relation()
        relation = r.get_relationship(Recipient.value('uid'), Sender.value('uid'))
        if relation == "":
            pass
        else:
            relation = self.c_lang(relation)
            text = "is for you"
            text_is = self.c_lang(text)
            header = "%s %s %s : %s"%( Sender.value('prenom'), Sender.value('nom'), text_is, relation)
            strong = HTMLgen.Strong(header)
            div.append(strong)  
            div.append(br)
        
        uid = Recipient.value('uid')
        # header = "Tw\xf3j osobisty identyfikator jest : %s"%uid
        text = "your personal identifier is"
        text = self.c_lang(text)
        header = "%s : %s"%(text, uid)
        strong = HTMLgen.Strong(header)
        div.append(strong)   
        div.append(br)
        
        key = self.get_key(uid)
        
        # header = "A Tw\xf3j klucz : %s"%key
        text = "your key is"
        text = self.c_lang(text)
        header = "%s : %s"%(text, key)
        strong = HTMLgen.Strong(header)
        div.append(strong)
        div.append(br)
        
        text = "Kliknij w ten link aby potwierdzi\xe6 odebranie tej wiadomo\xb6ci"
        text = "click here to confirm reception of this invitation"
        text = self.c_lang(text)
        url = "https://drzewo.me/tr/drzewo.py?action=accepted&uid=%s&key=%s&emailid=%s"%(Recipient.value('uid'),key, emailid)
        #######################################################################
        #######################################################################
        # CHANGE URL TO drzewo.py when promoting file dr.py to drzewo.py 
        #######################################################################
        #######################################################################
        # url = "https://drzewo.me/tr/drzewo.py?action=accepted&uid=%s&key=%s&emailid=%s"%(Recipient.value('uid'),key, emailid)
        href = HTMLgen.Href(url, text)
        div.append(href)
        div.append(br)    
        
        text = "Kliknij w ten link aby zalogowa\xe6 si\xea do drzewa przy pomocy identyfikatora i klucza"
        text = "click here to log into the tree using your personal ID and key"
        text = self.c_lang(text)
        url = "https://drzewo.me"
        href = HTMLgen.Href(url, text)
        div.append(href)
        div.append(br)
        
        text = "Kliknij w ten link aby wej\xb6\xe6 do drzewa Twoim osobistym kluczem dost\xeapu"
        text = "click here to log into the tree using a personalized link"
        text = self.c_lang(text)
        url = "https://drzewo.me/tr/drzewo.py?action=login&uid=%s&key=%s"%(Recipient.value('uid'), key)
        href = HTMLgen.Href(url, text)
        div.append(href)
        div.append(br)
        div.append(HTMLgen.HR())
        
        
        doc_simple.append(div)
      
                
        owner_uid = self.idict.value('owner_uid')        
        doc.append(self.show_item(uid, owner_uid))          
    
        doc_simple.append(doc)
        
        return str(doc_simple)    
        



if '__main__' == __name__:

    if True:     
        emailer = Emailer(839397534, pref_lang = "PL")
        emailer.run_emails()
        
        # print "DO NOT FORGET TO FLIP LINE 310  TO REAL EMAIL SERVER and 371 TO UPDATE MYSQL THAT EMAIL WAS SEND"
        
        # print emailer.c_lang("  you  are his father")
    else:
        # print "ERROR"
        pass
                                             
