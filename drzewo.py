#!/usr/bin/python
# -*- coding: iso-8859-2 -*-


#=======================================================================================================
# HISTORY:   |  CHANGE:
# Date:      |
# 6-Mar-2017 |  Osoba która zmarła ma wyświetloną datę śmierci 
# 6-Mar-2017 |  Poprawione wpisywanie pustych dat "bapt,deces' do mySQL jako NULL jezeli wartość z CGI jest ''
# 3-Sep-2023 |  Dopisane staropolskie relacje 


'''
PURPOSE:
  This scripts is executable as Web CGI to monitor list of 
  linux machines accessible with root password

  This scripts should be executables as 
  http://localhost/cgi-bin/LabMonitorTool.py 

  From Menu you create list of nodes IPs, 
  create list of executable Linux commands. 
  Execute requests to all machines by clicking on Execute 
  And displaying Results 

REQUIREMENTS:
a. INSTALLED SOFTWARE 
   Linux Ubuntu 12.04 or newer
   apache2 - web server 
   python2.7 installed as CGI for Apache2
   mysql-server database server accessible with password root/root

a. PYTHON PACKAGES
   python-mysqldb  access to MYSQL from python 
   python-htmlgen  generating HTML web pages from python 

b. LIST OF FILES: 
   cgi-bin/all_for_web.py -executig threaded ssh calls to nodes and storing results in /tmp/all.db
   cgi-bin/HTMLGen.py -customized HTMLgen python library  
   cgi-bin/mmsgennodes.sql -Database containing list of IPs, list of Commands and results 
                    storrage. This file is used only for SQL mmsgennodes database initialization 
   css/html.css - stylesheets 
   css/jq.css
   css/style.css

   js/sortable.js - java scripts for displaying sortable table 

'''
from CookieLoginClass import LoginCookie
import MySQLdb as mdb
import os, sys
import os.path
import datetime
import time
# Import modules for CGI handling 
import cgi 
import cgitb;  cgitb.enable()
import difflib
# import all_for_web
import HTMLgen
import HTMLGen
import HTMLGeoLocation
import hashlib

import Leafs 

SCRIPT = os.path.basename(sys.argv[0])
MYSQL_DATABASE_NAME='nukedemo'
MYSQL_USER='root'
MYSQL_PASSWORD='rmld29'
TABLE  = 'nuke_genealogy'
SQL_LIMIT = 0

PATH_TO_PICTURES = 'image/drzewo'
PATH_TO_TREE="../demo/modules.php?op=modload&name=MyNukeGenealogy&file=index&noleftblocks=true&do=display&id=%s"

SUPER_USERS = [614101095, 839397534, 682508999]
# SUPER_USERS = []

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


c_polish={
'id':            'id',
'pere':          'ojciec',
'mere':          'matka',
'prenom':        'imi\xea',
'nom':           'nazwisko',
'notes':         'notatki',
'naissance':     'data urodzenia',
'naissance_plac':'miejsce urodzenia',
'deces':         'zmar\xb3',
'deces_plac':    'miejsce \xb6mierci',
'occu':          'zaw\xf3d',
'address':       'ulica',
'city':          'miejscowo\xb6\xe6',
'zip':           'kod pocztowy',
'state':         'wojew\xf3dztwo',
'country':       'kraj',
'phone':         'telefon',
'email':         'email',
'facebook':      'facebook',
'facebook_id':   'facebook ID',
'owner_uid':     'ID w\xb3a\xb6ciciela wpisu',
'change_time':   'czas zmiany',
'picture_id':    'zdj\xeacie',
'geo_location':  'geo lokacja',
}

hidden=             ['id', 'uid', 'pere','mere','genre','conjoint','bapt','bapt_plac','epouse','deces_plac','picture_id','facebook_id','owner_uid','change_time']
hidden_for_editing= ['id', 'uid', 'pere','mere','genre','conjoint','bapt','bapt_plac','epouse','owner_uid','change_time','facebook_id','picture_id']

dates_items = ['bapt', 'naissance', 'deces'] #Pola w bazie danych ktore sa datami

RADIUS = 3
COLOR = 'yellow'
STEM = 0.0

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
        
    def get_links(self, uid):
        # Return all infor for uid in the form of dictionary
        self.cur.execute("SELECT * from %s WHERE uid='%s';"%(TABLE, uid))
        row = self.cur.fetchall()
        try:
            row_data = row[0]
            return [row_data[12], row_data[13], row_data[14]]
        except:
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
        

class FamilyTree:
    def __init__(self):
        self.con = mdb.connect('localhost',MYSQL_USER,MYSQL_PASSWORD,MYSQL_DATABASE_NAME)
        self.cur = self.con.cursor()
        self.column_names = [] 
        self.get_column_names()
        self.login_dict = Dict()
        self.owner_uid = ''
        self.svg = ''

        # Open connection to MySQL


    def get_new_uid(self):
        return int(time.time())

    def show_menu(self, uid):
        idict = self.get_dict(uid)
        if self.login_dict.g() :
            gender_form = 'y'
        else:
            gender_form = 'a'

        menu = HTMLgen.Div(id = 'menu') 
        menu_text= [('GENEALOGY', TABLE),( "ZOBACZ NA DRZEWIE", PATH_TO_TREE), ("LOGOUT", ""),("Jeste\xb6 zalogowan%s jako : "%(gender_form), "") ]
    
        url = "%s?action=list"%(SCRIPT)
        icon = '<img class="icon" src="images/b_%s.png" alt="Structure" /> '%(menu_text[0][1])
        href = HTMLgen.Href( url, icon+menu_text[0][0])
        # menu.append(href)
        menu.append(" ")
    

        # url = "%s?action=show_tree&uid=%s"%(SCRIPT, idict['uid'])    
        url = "%s?action=show_tree&uid=%s"%(SCRIPT, uid)                   
        icon = '<img class="icon" src="images/b_tree.png" alt="Structure" /> '
        href = HTMLgen.Href(url, icon+menu_text[1][0], target="new")
        menu.append(href)
        menu.append(" ")
    
        url = "%s?action=logout"%(SCRIPT)
        icon = '<img class="icon" src="images/b_logout.png" alt="Structure" /> '
        href = HTMLgen.Href(url, icon+menu_text[2][0] )
        menu.append(href)
        menu.append(" ")
    
     
        url = "%s?action_show&uid=%s"%(SCRIPT, self.login_dict['uid'])
        logged_user = "%s %s "%(self.login_dict['prenom'], self.login_dict['nom'])
        icon = '<img class="icon" src="images/b_person.png" alt="Structure" /> '
        href = HTMLgen.Href(url, icon+menu_text[3][0]+logged_user )
        menu.append(href)
        image = HTMLgen.Image('%s'%(self.get_picture(self.login_dict)), width="30", height="40")
        href = HTMLgen.Href(url, image )
        menu.append(href)
        menu.append(" ")
        return menu 
    
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
        # Return all infor for uid in the form of dictionary
        self.cur.execute("SELECT * from %s WHERE uid='%s';"%(TABLE, uid))
        row = self.cur.fetchall()
        try:
            row_data = row[0]
            return self.convert_sqlrow_to_dict(row[0])
        except:
            return 
 
    def get_tabela_grandparents(self, text, idict, uid):
    
        dedit = HTMLgen.Div(id = 'parents')
        table = HTMLgen.TableLite(border=0, cell_spacing=1, width=None, body=[])
        tr = HTMLgen.TR()
        pere_dict = self.get_dict(int(idict.value('pere')))
        if not pere_dict is None:
            url = "%s?action=show&uid=%s"%(SCRIPT, idict['pere'])           
            td = HTMLgen.TD()
            td.append(self.one_person('Dziadek %sy'%text, url, pere_dict))
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
            td.append(self.one_person('Babcia %sa'%text, url, mere_dict))
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
        image = HTMLgen.Image('%s'%( self.get_picture(dict)), width="30", height="40")
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
            td_grandparents.append(self.get_tabela_grandparents('ojczyst', pere_dict,  uid))
            tr_grandparents.append(td_grandparents)  
            
            td = HTMLgen.TD()          
            td.append(tr_grandparents)
            tr.append(td)

            url = "%s?action=show&uid=%s"%(SCRIPT, idict['pere'])
            td = HTMLgen.TD()
            td.append(self.one_person('Ojciec', url, pere_dict))
            tr.append(td)
    
        else: # Dadaj tate
            if True or self.check_permission_to_edit(idict):
                url = "%s?action=add_parent&genre=1&uid=%s"%(SCRIPT,uid)
                href = HTMLgen.Href( url, "Dodaj Ojca %s (+)"%(self.kogo(idict)))
                td = HTMLgen.TD()
                td.append(href)
                tr.append(td)
                url = "%s?action=link_papa&genre=1&nom=%s&uid=%s&dob=%s"%(SCRIPT, idict.value('nom'),uid,idict.value('naissance'))
                href = HTMLgen.Href( url, "Dolacz Ojca %s (->)"%(self.kogo(idict)))
                td = HTMLgen.TD()
                td.append(href)
                tr.append(td)
            #     table.append(tr)
        
        mere_dict = self.get_dict(int(idict.value('mere')))
        if not mere_dict is None:
            # tr_grandparents= HTMLgen.TR()
            td_grandparents= HTMLgen.TD()
            td_grandparents.append(self.get_tabela_grandparents('mateczn', mere_dict,  uid))
            tr_grandparents.append(td_grandparents)  
            '''          
            td = HTMLgen.TD()          
            td.append(tr_grandparents)
            tr.append(td)                      
            '''
            
            url = "%s?action=show&uid=%s"%(SCRIPT, idict.value('mere'))
            td = HTMLgen.TD()
            td.append(self.one_person('Matka', url, mere_dict))
            tr.append(td)
        else: # Dadaj mame
            if self.check_permission_to_edit(idict):
                url = "%s?action=add_parent&genre=0&uid=%s"%(SCRIPT,uid)
                href = HTMLgen.Href( url, "Dodaj Matke %s (+)"%(self.kogo(idict)))
                td = HTMLgen.TD()
                td.append(href)
                tr.append(td)

                url = "%s?action=link_mama&genre=0&nom=%s&uid=%s&dob=%s"%(SCRIPT, idict.value('nom'),uid,idict.value('naissance'))
                href = HTMLgen.Href( url, "Dolacz Matke %s (->)"%(self.kogo(idict)))
                td = HTMLgen.TD()
                td.append(href)
                tr.append(td)
        
        table.append(tr)
            
        dedit.append(table)
        return dedit
    
    def get_gr_children_td(self, idict, uid, picture_scale, recursive_counter ):
    
        # Wyszukaj grand children 
        sql = "SELECT * from %s WHERE pere='%s' OR mere='%s' ORDER BY  `naissance` ASC ;"%(TABLE, uid, uid) 
        self.cur.execute(sql)
        gr_children = self.cur.fetchall()
        
        #return empty when no children found 
        if len(gr_children) == 0: 
            return ""
        
        counter = recursive_counter - 1
        if counter < 0: 
            return ""
        
        if counter % 2 == 0:  
            children_div = HTMLgen.Div(id = 'children')
        else:
            children_div = HTMLgen.Div(id = 'children_odd')
        
        scale = picture_scale * 0.8  
        width = int(3*scale)
        height =int(4*scale)

        
        td1 = HTMLgen.TD()      
        # td1.append(uid)
        td = HTMLgen.TD()
        tr = HTMLgen.TR()  
        tb = HTMLgen.TableLite(border=0, cell_spacing=1, width=None, body=[])
        for child in gr_children:
            
            child_uid = child[1]
            child_name ="%s "%(child[3])  # imie 
            url = "%s?action=show&uid=%s"%(SCRIPT,child_uid)
            href1 = HTMLgen.Href( url, child_name)
            
            child_uid = child[1]
            child_name =" %s"%(child[4]) #nazwisko
            url = "%s?action=show&uid=%s"%(SCRIPT,child_uid)
            href2 = HTMLgen.Href( url, child_name)

            child_dict = self.get_dict(child_uid)
            # dedit.append(child_uid)
            image = HTMLgen.Image('%s'%( self.get_picture(child_dict)), width="%s"%width, height="%s"%height)
            href_image = HTMLgen.Href( url, image)

            tr = HTMLgen.TR()
            td_text = HTMLgen.TD()
            td_image = HTMLgen.TD()
            td = HTMLgen.TD()

            
            td_text.append(href1)
            td_text.append(HTMLgen.BR())
            td_text.append(href2)            
            td_image.append(href_image)

            tr.append(td_text)
            tr.append(td_image)              
            td = self.get_gr_children_td(child, child_uid, scale, counter)  # recursive 
            tr.append(td)
            tb.append(tr)
        
        children_div(tb)        
        td1.append(children_div)

        return(td1)    
            

    
    def get_tabela_children(self, idict, children, uid):
        dedit = HTMLgen.Div(id = 'children')
        table_big = HTMLgen.TableLite(border=0, cell_spacing=1, width=None, body=[])
        tr_big = HTMLgen.TR()
        td_big = HTMLgen.TD()

        table = HTMLgen.TableLite(border=0, cell_spacing=1, width=None, body=[])
        table_of_images = HTMLgen.TableLite(border=0, cell_spacing=5, width=None, body=[])
              
        tr_of_images = HTMLgen.TR()
        if children:  # Paka linki dzieci 
            for child in children:
                child_uid = child[1]
                child_name ="%s %s"%(child[3],child[4])
                url = "%s?action=show&uid=%s"%(SCRIPT,child_uid)
                href = HTMLgen.Href( url, child_name)
                
                child_dict = self.get_dict(child_uid)
                image = HTMLgen.Image('%s'%( self.get_picture(child_dict)), width="60", height="80")
                href_image = HTMLgen.Href( url, image)

                tr = HTMLgen.TR()
                td_text = HTMLgen.TD()
                td_image = HTMLgen.TD()
                td = HTMLgen.TD()
                
                td_text.append(href)
                td_image.append(href_image)
                
                tr.append(td_text)
                tr.append(td_image)              
                
                td = self.get_gr_children_td(child, child_uid, 20, 12) # recursive call 
                tr.append(td)
                table.append(tr)
               
            td_big.append(table)
            tr_big.append(td_big)
            td_big = HTMLgen.TD()
            tr_big.append(td_big)
            table_big.append(tr_big) 
            dedit.append(table_big)

        if True:
            dedit.append(HTMLgen.HR())
            if True:  # To show edit link"
                if self.check_permission_to_edit(idict):
                    table = HTMLgen.TableLite(border=0, cell_spacing=1, width=None, body=[])
                    url = "%s?action=add_child&uid=%s&genre=0"%(SCRIPT, uid)
                    #PL href = HTMLgen.Href( url, "dodaj c\xf3rke %s (+)"%(self.kogo(idict)))
                    text1 = "Add"
                    text2 ="daughter"
                    href = HTMLgen.Href( url, " %s %s %s (+) "%(text1, self.kogo(idict), text2))                    
                    tr = HTMLgen.TR()
                    td = HTMLgen.TD()
                    td.append(href)
                    tr.append(td)
                    table.append(tr)
    
                    tr = HTMLgen.TR()
                    url = "%s?action=add_child&uid=%s&genre=1"%(SCRIPT, uid)
                    # href = HTMLgen.Href( url, "dodaj syna %s (+)"%(self.kogo(idict)))
                    text1 = "Add"
                    text2 ="son"
                    href = HTMLgen.Href( url, " %s %s %s (+) "%(text1, self.kogo(idict), text2))                 
                    td = HTMLgen.TD()
                    td.append(href)
                    tr.append(td)
                    table.append(tr)

                    # LINKING CHILD IS ANABLE ONLY FOR SUPER USERS 
                    if self.am_i_superuser():
                        tr = self.get_connect_child(uid, idict)
                        table.append(tr)

                    dedit.append(table)
        return dedit

    def kogo(self, idict):
        imie = idict.value('prenom')
        if idict.g(): 
            # if imie in ['Jacek','Wojtek','Zbyszek','Przemek']:
            if imie[-2:] in ['ek']:
                return "%ska"%(imie[:-2]) 
            # if imie in ['Jerzy','Wincenty','Konstanty',itp]:
            if imie[-1:] in ['y']: 
                return "%sego"%(imie[:-1]) 
            return "%sa"%(imie)
        else: 
            if imie[-2:] in ['ia','ja']:
                return "%si"%(imie[:-1])
            return "%sy"%(imie[:-1])


    def get_connect_child(self, uid, idict):
        if idict.g():
            url = "%s?action=link_child&uid=%s&nom=%s"%(SCRIPT, uid, idict.value('nom'))
        else:
            spouse_dict = self.get_dict(int(idict.value('conjoint')))
            if spouse_dict is None or spouse_dict['nom'] is None:
                url = "%s?action=link_child&uid=%s&nom=%s"%(SCRIPT, uid, idict.value('nom'))
            else:
                url = "%s?action=link_child&uid=%s&nom=%s"%(SCRIPT, uid, spouse_dict['nom'])
        href = HTMLgen.Href( url, "dol\xb1cz potomka (-->!!! BARDZO OSTROZNIE !!!<--)")
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
         " Serdecznie zapraszam do Drzewa rodzinnego.",
         "",
         " https://drzewo.me/tr/drzewo.py?action=login\\&ampuid=%s\\ampkey=%s"%(ID,key),
         " Twoj identyfikator : %s"%(ID),
         " Twoj klucz : %s"%(key),
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
                href = HTMLgen.Href( url, "M\xb1\xbf: %s %s"%(spouse_dict['prenom'], spouse_dict['nom']))
            else:
                href = HTMLgen.Href( url, "\xafona: %s %s"%(spouse_dict['prenom'], spouse_dict['nom']))
    
            tr = HTMLgen.TR()
            td = HTMLgen.TD()
            td.append(href)
            tr.append(td)


            image = HTMLgen.Image('%s'%( self.get_picture(spouse_dict)), width="30", height="40")
            href = HTMLgen.Href( url, image)
            td = HTMLgen.TD()
            td.append(href)
            tr.append(td)

            table.append(tr)
        else: # Dadaj spouse
            genre = 1
            spouse = 'm\xea\xbfa'
            if idict.g(): 
                genre =0
                spouse = '\xbfone'
        
            if True:  # To show edit link"
                if self.check_permission_to_edit(idict):
                    url = "%s?action=add_spouse&uid=%s&genre=%s"%(SCRIPT, uid, genre)
                    href = HTMLgen.Href( url, "Dodaj %s %s (+)"%(spouse, self.kogo(idict)))
                    tr = HTMLgen.TR()
                    td = HTMLgen.TD()
                    td.append(href)
                    tr.append(td)
    
                    url = "%s?action=link_spouse&uid=%s&genre=%s"%(SCRIPT, uid, genre)
                    href = HTMLgen.Href( url, "Dol\xb1cz %s %s (->)"%(spouse, self.kogo(idict)))
                    td = HTMLgen.TD()
                    td.append(href)
                    tr.append(td)
                    table.append(tr)
    
        dedit.append(table)
        return dedit

    def show_pictures(self, idict ):

        import os
        text = ''
        id = idict.value('id')
        basepath = PATH_TO_PICTURES
        listdir = os.listdir(basepath)
        listdir.sort()
        pictures_container = HTMLgen.Div(id = 'pictures_container')
        for fname in listdir:
           
            if not os.path.isfile(os.path.join(basepath,fname)): continue
            if not (fname.endswith('.JPG') or fname.endswith('.jpg')) : continue
            if not (fname.startswith('%s_'%id)) and not(fname.startswith('%s.'%id)): continue
            if fname.startswith('.') : continue
            path = '%s/%s'%(PATH_TO_PICTURES, fname)
            # image = HTMLgen.Image('%s'%(path), width="150", height="200")
            image = HTMLgen.Image('%s'%(path), width="", height="200")
            url ='%s/%s'%(PATH_TO_PICTURES, fname)
            href = HTMLgen.Href(url, image, target="new")
            pictures_container.append(href)
        return pictures_container

    
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
        
        picture_path = "images/smiley.gif"    
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
        td_picture_form.append('Zmie\xF1 zdj\xeacie profilowe')
        dd_upload_picture.append(form)
        td_picture_form.append(dd_upload_picture)
        td_picture_form.append("Wybierz zdj\xeacie do portretu ")
        td_picture_form.append(HTMLgen.BR())
        td_picture_form.append("w proporcjach szeroko\xb6ci i wysoko\xb6ci 300x400.")
        td_picture_form.append(HTMLgen.BR())
        td_picture_form.append("Program przyjmie ka\xbfde zdj\xeacie ")
        td_picture_form.append(HTMLgen.BR())
        td_picture_form.append("w formacie JPG i nie wi\xeaksze ni\xbf 2MB.")
        td_picture_form.append(HTMLgen.BR())
        td_picture_form.append("Wybrany do wys\xb3ania zbi\xf3r ")
        td_picture_form.append(HTMLgen.BR())
        td_picture_form.append("powinen by\xe6 z rozszerzeniem .jpg.")
        td_picture_form.append(HTMLgen.BR())


        any_picture_form = HTMLgen.Form( enctype="multipart/form-data", cgi="%s"%SCRIPT)
        any_picture_form.append( HTMLgen.BR())
        any_picture_form.append( HTMLgen.Input( type='file', name="file"))
        any_picture_form.append( HTMLgen.Input( type='hidden', name="file_name", value="%s"%(idict.value('id'))))
        any_picture_form.append( HTMLgen.Input( type='hidden', name="uid", value="%s"%(idict.value('uid'))))
        any_picture_form.append( HTMLgen.Input( type='hidden', name="prefix", value="YES"))
        any_picture_form.append( HTMLgen.Input( type='hidden', name="profile_picture", value="NO"))

        dd_upload_any_picture = HTMLgen.Div(id = 'upload')

        td_picture_form.append(HTMLgen.BR())
        td_picture_form.append('Umie\xb6\xe6 jakiekolwiek zdj\xeacie (JPG)')
        dd_upload_any_picture.append(any_picture_form)
        td_picture_form.append(dd_upload_any_picture)
        
        return (td_picture_form)

    def show_item(self, row, children, uid, owner_uid):
    
        dedit = HTMLgen.Div(id = 'show')
        dedit_item = HTMLgen.Div(id = 'item')
        
        
        dedit_picture = HTMLgen.Div(id = 'picture_item')
        table_big = HTMLgen.TableLite(border=0, cell_spacing=1, heading=self.column_names[1:], width=None, body=[])        
        table = HTMLgen.TableLite(border=0, cell_spacing=1, heading=self.column_names[1:], width=None, body=[])
        table_with_picture = HTMLgen.TableLite(border=0, cell_spacing=1, heading=self.column_names[1:], width=None, body=[])
    
        idict = Dict()
        
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
                td.append("%s :"%(c_polish[c]))
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

                if c == 'facebook': 
                    url = "http://www.facebook.com/%s"%(idict.value('facebook'))
                    # icon = '<img src="image/facebook.jpg"> '
                    icon = '<img class="icon" src="images/facebook.jpg" width="30", height="30", alt="Structure" />'
                    href = HTMLgen.Href(url, icon, target="new")
                    line_to_show = href

                td.append(line_to_show)
                tr.append(td)
                table.append(tr)
    
       # Tu dodaje się stopien pokrewieństwa / relation
        relation = self.get_relationship(idict)
        if relation <> '': 
            dd_relation = HTMLgen.Div(id = 'relation')
            dd_relation.append(relation)
            font = HTMLgen.Font(size="20")
            td = HTMLgen.TD( align="left", colspan="3", bgcolor="#88FF88" )
            tr = HTMLgen.TR()
            td.append(dd_relation)
            tr.append(td)
            table_with_picture.append(tr)
            
        # Tu dadaje sie zdjecie
        image = HTMLgen.Image('%s'%(self.get_picture(idict)), width="150", height="200")
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
        tr = HTMLgen.TR()
        if idict.value('owner_uid') >0 :
            try:
                td = HTMLgen.TD( align="left" )
                owner_dict= self.get_dict( idict['owner_uid'])
                url = "%s?action=show&uid=%s"%(SCRIPT, owner_dict.value('uid'))
                name = "%s %s"%(owner_dict.value('prenom'), owner_dict.value('nom'))
                href = HTMLgen.Href( url, name)
                td.append("w\xb3a\xb6cicielem wpisu jest : " )
                td.append(href)
                tr.append(td)
                table_footer.append(tr)
            except:
                # You are here because your owner does not exist
                pass
            
        tr = HTMLgen.TR()
        td = HTMLgen.TD( align="left" )
        td.append("wpis ostatnio zmieniony : %s"%(idict.value('change_time')))
        tr.append(td)
        table_footer.append(tr)
        
        if not self.owner_uid is None:  # To show edit link"
            if self.check_permission_to_edit(idict):
                url = "%s?action=edit&uid=%s&owner_uid=%s"%(SCRIPT,uid, self.owner_uid)
                href = HTMLgen.Href( url, " Edycja dozwolona: %s"%self.msg)
                tr = HTMLgen.TR()
                td = HTMLgen.TD( align="left" )
                td.append(href)
                tr.append(td)
                table_footer.append(tr)
                to_addr = idict.value('email')
                if  self.am_i_superuser() :
                    uid = str(idict.value('uid'))
                    key = self.get_key(uid)
                    msg = 'Identyfikator: %s Klucz: %s  '%(uid, key) 
                    tr = HTMLgen.TR()
                    td = HTMLgen.TD( align="left" )
                    td.append(msg)
                    tr.append(td)
                    table_footer.append(tr)
                    if  to_addr.find('@') > 0 :
                        dedit_item.append(HTMLgen.BR())
                        imie = "%s %s"%(idict.value('prenom'), idict.value('nom'))
                        ID = idict.value('uid')
                        key = self.get_key(ID)
                        msg = self.get_message(imie, ID, self.get_key(ID))
                        mail = HTMLGen.MailTo( address="%s"%(to_addr), subject="Zaproszenie do Drzewa", body=msg, text="wyslij email do %s"%imie)
                        tr = HTMLgen.TR()
                        td = HTMLgen.TD( align="left" )
                        td.append(mail)
                        tr.append(td)
                        table_footer.append(tr)
                    if  len(idict.value('facebook')) > 0 :
                        to_addr = "%s@facebook.com"%(idict.value('facebook'))
                        dedit_item.append(HTMLgen.BR())
                        imie = "%s %s"%(idict.value('prenom'), idict.value('nom'))
                        ID = idict.value('uid')
                        key = self.get_key(ID)
                        msg = self.get_message(imie, ID, self.get_key(ID))
                        mail = HTMLGen.MailTo( address="%s"%(to_addr), subject="Zaproszenie do Drzewa", body=msg, text="wyslij Facebook email do %s"%imie)
                        tr = HTMLgen.TR()
                        td = HTMLgen.TD( align="left" )
                        td.append(mail)
                        tr.append(td)
                        table_footer.append(tr)
                        
                    url = "%s?action=login&uid=%s&key=%s"%(SCRIPT, uid, key)
                    href = HTMLgen.Href( url, " Zmiana loginu: ")  
                    tr = HTMLgen.TR()
                    td = HTMLgen.TD( align="left" )
                    td.append(href)
                    tr.append(td)
                    table_footer.append(tr)
            else:
                tr = HTMLgen.TR()
                td = HTMLgen.TD( align="left" )
                # td.append("Edycja nie jest dozwolona (1): %s<>%s"%( idict.value('owner_uid'), self.owner_uid))
                td.append("Edycja nie jest dozwolona:") 
                tr.append(td)
                table_footer.append(tr)
                # dedit_item.append("%s<>%s"%( idict.value('owner_uid'), self.owner_uid))
        else:
            # dedit_item.append("%s<>%s"%( idict.value('owner_uid'), self.owner_uid))
            tr = HTMLgen.TR()
            td = HTMLgen.TD( align="left" )
            # td.append("Edycja nie jest dozwolona (2): %s<>%s"%( idict.value('owner_uid'), self.owner_uid))
            td.append("Edycja nie jest dozwolona:") 
            tr.append(td)
            table_footer.append(tr)
                
        tr = HTMLgen.TR()        
        td = HTMLgen.TD( align="left", colspan="3" )
        td.append(table_footer)
        tr.append(td)
        
        td = HTMLgen.TD( align="left" , colspan="2" )
         
        table_with_picture.append(tr)
                
        dedit_item.append(table_with_picture)  
        
        # geo = ''
        # name = "%s %s"%(idict.value('prenom'),idict.value('nom'))
        # city = idict.value('city')
        # address = idict.value('address')
        # geo_location = idict.value('geo_location')
        # geo = HTMLGeoLocation.geo_location(geo_location = geo_location, name = name, city=city, street=address)
        # dedit_item.append(geo)                        
            
    
        tabela_rodzice = self.get_tabela_rodzice(idict, uid)
        dedit.append(tabela_rodzice)
    
        tabela_spouse = self.get_tabela_spouse(idict, uid)
        dedit.append(tabela_spouse)
        
        dedit.append(dedit_item)
        
        tabela_children = self.get_tabela_children(idict, children, uid)
        text = "Descendants"
        text = "Potomkowie"
        text = "Potomkowie"
        
        dedit.append(text)
        dedit.append(tabela_children)
        
        return dedit

    def am_i_superuser(self):
        return int(self.login_dict.value('uid')) in SUPER_USERS

    def calculate_date( date, years):
        year = str(int(date[:4]) + years)
        return "%s%s"%(year, data[4:])

    def get_relationship(self, idict):

        Person = idict
        # if True:
        Me = self.login_dict
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
        
        twoj = "To jest Tw\xf3j"
        twoja = "To jest Twoja"

        self.msg = ""
        
        try:  # try
            # Test myself 
            if person == me:
                self.msg  = "To jeste\xb6 Ty"
                return self.msg
            
            # Ojciec test 
            if Me.papa() > 0:
                My_papa = self.get_dict(Me.papa())
                if  person == Me.papa():
                    self.msg = "%s Ojciec."%twoj
                    return self.msg
            
            if Me.mama() > 0 :
                My_mama = self.get_dict(Me.mama())
                if  person == Me.mama():
                    self.msg = "%s Matka."%twoja
                    return self.msg   
                
            if Me.papa() > 0:       
                if My_papa.papa()  >0: 
                    if person == My_papa.papa():
                        self.msg = "%s dziadek ojczysty."%twoj
                        return self.msg
                                               
                if My_papa.mama() >0: 
                    if person == My_papa.mama():
                        self.msg = "%s babcia ojczysta."%twoja
                        return self.msg    
                     
            if Me.mama() > 0:                      
                if My_mama.papa()  >0: 
                    if person == My_mama.papa() :
                        self.msg = "%s dziadek mateczny."%twoj
                        return self.msg                      
      
                if My_mama.mama()>0: 
                    if person == My_mama.mama():
                        self.msg = "%s babcia mateczna."%twoja
                        return self.msg

            # Macocha test 
            if Me.mama() > 0:        
                if My_papa.conj() > 0:
                    if  person == My_papa.conj():
                        self.msg = "%s macocha."%twoja
                        return self.msg          

            # Ojczym test 
                if My_mama.conj() > 0:
                    if  person == My_mama.conj():
                        self.msg = "%s ojczym."%twoj
                        return self.msg       
                    
                    
            # Małzonek i tesciowie 
            my_spouse = Me.conj()  
            if Me.conj() > 0 :
                My_spouse = self.get_dict(Me.conj())
                if  person == Me.conj():
                    if Person.g(): 
                        self.msg = "%s m\xb1\xbf."%twoj
                    else:
                        self.msg = "%s \xbfona."%twoja
                    return self.msg
                
                if My_spouse.papa() >0: 
                    My_spouse_papa = self.get_dict(My_spouse.papa())
                    # Logged person is male 
                    if person == My_spouse.papa():  
                        if Me.g():
                            self.msg = "%s te\xb6\xe6. Po staropolsku: cie\xb6\xe6."%twoj
                        else:    
                            self.msg = "%s te\xb6\xe6. Po staropolsku: \xb6wiekr."%twoj
                        return self.msg
                    
                if My_spouse.mama() >0: 
                    My_spouse_mama = self.get_dict(My_spouse.mama())
                    # Logged person is male 
                    if person == My_spouse.mama(): 
                        if Me.g():
                            self.msg = "%s te\xb6ciowa. Po staropolsku: cie\xb6cia."%twoja
                        else:    
                            self.msg = "%s te\xb6ciowa. Po staropolsku: \xb6wiekra."%twoja  
                        return self.msg       
                    
            #================================================    
            
            # Dzieci      
            person_papa = Person.papa()
            if person_papa > 0:
                if me == person_papa:
                    if Person.g(): 
                        self.msg = "%s syn. Jeste\xb6 jego ojcem."%twoj
                        return self.msg
                    else:
                        self.msg = "%s c\xf3rka. Jeste\xb6 jej ojcem."%twoja
                        return self.msg
                        person_papa = Person.papa()  
                        
            person_mama = Person.mama()                        
            if person_mama > 0:
                if me == person_mama:
                    if Person.g(): 
                        self.msg = "%s syn. Jeste\xb6 jego matk\xb1."%twoj
                        return self.msg
                    else:
                        self.msg = "%s c\xf3rka. Jeste\xb6 jej matk\xb1."%twoja
                        return self.msg   

                    
            #===============================================
            # Rodzeństwo
                                       
            my_mama = Me.mama()
            my_papa = Me.papa()
            person_mama = Person.mama()
            person_papa = Person.papa()
            
            
            # sister and brother test             
            if my_mama > 0 and my_papa > 0 and person_mama > 0 and person_papa > 0:   
    
                if  my_mama == person_mama and my_papa == person_papa:
                    if Person.g() : 
                        self.msg = "%s brat."%twoj
                    else:
                        self.msg = "%s siostra."%twoja                         
                    return self.msg
                elif my_mama == person_mama or my_papa == person_papa:
                        if Person.g() : 
                            self.msg = "%s p\xf3\xb3 brat."%twoj
                        else:
                            self.msg = "%s p\xf3\xb3 siostra."%twoja  
                        return self.msg    
                   
            my_spouse = Me.conj()  
            # szwagier test
            if my_spouse > 0 :
                My_spouse = self.get_dict(my_spouse)  
                my_spouse_papa = My_spouse.papa()
                my_spouse_mama = My_spouse.mama()
                
                if  person_papa == my_spouse_papa or person_mama == my_spouse_mama:
                    if My_spouse.g(): 
                        if Person.g(): 
                            self.msg = "%s szwagier (brat m\xea\xbfa). Po staropolsku: dziewierz."%twoj
                            return self.msg
                        else:
                            self.msg = "%s szwagierka (siostra m\xea\xbfa). Po staropolsku: ze\xb3wa."%twoja
                            return self.msg
                    else:
                        if Person.g(): 
                            self.msg = "%s szwagier(brat \xbfony). Po staropolsku: surzy."%twoj
                            return self.msg                        
                        else:
                            self.msg = "%s szwagierka(siostra \xbfony). Po staropolsku: \xb6wie\xb6\xe6."%twoja
                            return self.msg

            person_papa = Person.papa()
            person_mama = Person.mama()
            # Wnuczek od syna test 
            if person_papa >0: 
                Papa = self.get_dict(person_papa)
                if  me in [Papa.papa(), Papa.mama()]:
                    if Person.g(): 
                        self.msg = "%s wnuk (syn syna). Po staropolsku: wn\xeak."%twoj
                        return self.msg
                    else:
                        self.msg = "%s wnuczka (c\xf3rka syna). Po staropolsku: wn\xeaka."%twoja
                        return self.msg
    
            # Wnuczek od corki test 
            if person_mama >0 : 
                Mama = self.get_dict(person_mama)
                if  me in [Mama.papa(), Mama.mama()]:
                    if Person.g() : 
                        self.msg = "%s wnuczek (syn c\xf3rki). "%twoj
                        return self.msg                        
                    else:
                        self.msg = "%s wnuczka (c\xf3rka c\xf3rki)."%twoja
                        return self.msg
                    
                    
            # ziec i synowa test 
            if person_spouse >0: 
                Spouse = self.get_dict(person_spouse)
                if  me in [ Spouse.papa(), Spouse.mama()]:
                    if Person.g(): 
                        self.msg = "%s zi\xea\xe6."%twoj
                        return self.msg
                    else:
                        self.msg = "%s synowa. Po staropolsku: sneszka."%twoja
                        return self.msg
              
            # bratanek test 
            if Person.papa() >0: 
                Papa = self.get_dict(Person.papa())
                if  my_papa in [Papa.papa() ] or my_mama in [Papa.mama() ]:
                    if Person.g() : 
                        self.msg = "%s bratanek. Po staropolsku: synowiec"%twoj
                    else:
                        self.msg = "%s bratanica. Po staropolsku: synowica"%twoja
                    return self.msg

            # sistrzeniec test 
            if Person.mama() >0: 
                Mama = self.get_dict(Person.mama())
                if  my_papa in [Mama.papa() ] or my_mama in [Mama.mama() ]:
                    if Person.g() : 
                        self.msg = "%s siostrzeniec."%twoj
                    else:
                        self.msg = "%s siostrzenica."%twoja
                    return self.msg

            # brat przyrodni test 
            if  my_papa in [Person.papa()] or my_mama in [Person.mama()]:
                if Person.g() : 
                    self.msg = "%s brat przyrodni"%twoj
                else:
                    self.msg = "%s siostra przyrodnia"%twoja
                return self.msg

            # szwagier od siotry lub brata
            
            # szwagier od siostry test 
            if Person.conj() >0: 
                Spouse = self.get_dict(Person.conj())
                if  my_papa ==Spouse.papa() or my_mama == Spouse.mama():
                    if Person.g() : 
                        self.msg = "%s szwagier (m\xb1\xbf siostry). Po staropolsku: siostrzanek"%twoj
                    else:
                        self.msg = "%s bratowa (\xbfona brata). Po staropolsku: j\xb1trew"%twoja
                    return self.msg

#========================================================================                

            My_papa = self.get_dict(my_papa)                    
            My_mama = self.get_dict(my_mama)

            # stryjek i ciotka od ojca rodzenstwo 
            if Me.papa() > 0: 
                if My_papa.mama() == Person.mama() or My_papa.papa() == Person.papa():
                    if Person.g() : 
                        self.msg = "%s wujek (brat ojca). Po staropolsku: stryj."%twoj
                    else:
                        self.msg = "%s ciocia (siostra ojca). Po staropolsku: ciotka."%twoja
                    return self.msg

            # wuj i ciotka od matki test 
            if Me.mama() >0: 
                if My_mama.mama() == Person.mama() or My_mama.papa() == Person.papa():
                    if Person.g() : 
                        self.msg = "%s wujek (brat matki).  Po staropolsku: wuj."%twoj
                    else:
                        self.msg = "%s ciocia (siostra matki).  Po staropolsku: ciotka."%twoja
                    return self.msg
            
            
            # rodzenstwo stryjeczne od ojca
            if Person.papa() > 0 and Me.papa() > 0:
                Person_papa = self.get_dict(Person.papa())
                if Person_papa.papa() == My_papa.papa() or Person_papa.mama() == My_papa.mama():  
                    if Person.g() : 
                        self.msg = "%s (syn brata ojca) brat stryjeczny."%twoj
                    else:
                        self.msg = "%s (c\xf3rka brata ojca) siostra stryjeczna."%twoja
                    return self.msg           
                             
                if Person_mama.papa() == My_papa.papa() or Person_mama.mama() == My_papa.mama() :
                    if Person.g() : 
                        self.msg = "%s (syn siostry ojca) brat cioteczny."%twoj
                    else:
                        self.msg = "%s (c\xf3rka siostry ojca) siostra cioteczna."%twoja
                    return self.msg

            # rodzenstwo cioteczne od mamy 
            if Person.mama() >0 and Person.papa() >0 and Me.mama() >0:
                My_mama = self.get_dict(Me.mama())   
                Person_mama = self.get_dict(Person.mama())   
                if Person_mama.mama() == My_mama.mama() or Person_mama.papa() == My_mama.papa():
                    if Person.g() : 
                        self.msg = "%s (syn siostry matki) brat cioteczny."%twoj
                    else:
                        self.msg = "%s (c\xf3rka siostry matki) siostra cioteczna."%twoja
                    return self.msg
 
                Person_papa = self.get_dict(Person.papa())  
                if Person_papa.mama() == My_mama.mama() or Person_papa.papa() == My_mama.papa():
                    if Person.g() : 
                        self.msg = "%s (syn brata matki) brat wujeczny."%twoj
                    else:
                        self.msg = "%s (c\xf3rka brata matki) siostra wujeczna."%twoja
                    return self.msg
                
            if Person.conj() >0 and Me.papa() > 0: 
                Spouse = self.get_dict(Person.conj())
                if Spouse.papa() == My_papa.papa() or Spouse.mama() == My_papa.mama():
                    if Person.g() : 
                        self.msg = "%s wujek (m\xb1\xbf cioci). Po staropolsku: naciot."%twoj
                    else:
                        self.msg = "%s ciocia (\xbfona stryja). Po staropolsku: stryjenka."%twoja
                    return self.msg
                
            if Person.conj() >0: 
                Spouse = self.get_dict(Person.conj())
                My_spouse = self.get_dict(Me.conj())
                if Spouse.papa() == My_spouse.papa() or Spouse.mama() == My_spouse.mama():
                    if Person.g() : 
                        self.msg = "%s (m\xb1\xbf siostry \xbfony). Po staropolsku: paszenog."%twoj
                    else:
                        self.msg = "%s (\xbfona brata \xbfony). Po staropolsku: paszenoga?."%twoja
                    return self.msg                

            # Siostra lub brat przyrodni test              
            if Person.mama()  > 0 and Me.papa() >0:   
                My_papa = self.get_dict(Me.papa())
                if  Person.mama() == My_papa.conj():
                    if Person.g() : 
                        self.msg = "%s brat (syn macochy) przyrodni."%twoj
                    else:
                        self.msg = "%s siostra (c\xf3rka macochy) przyrodnia."%twoja                         
                    return self.msg
            if Person.papa()  > 0 and Me.mama() >0:   
                My_mama = self.get_dict(Me.mama())
                if  Person.papa() == My_mama.conj():
                    if Person.g() : 
                        self.msg = "%s brat (syn ojczyma) przyrodni."%twoj
                    else:
                        self.msg = "%s siostra (c\xf3rka ujczyna) przyrodnia."%twoja                         
                    return self.msg
                  
            if Person.papa() > 0:
                if Me.conj() == person_papa:
                    if Person.g(): 
                        self.msg = "%s pasierb. Jeste\xb6 jego macoch\xb1."%twoj
                        return self.msg
                    else:
                        self.msg = "%s pasierbica. Jeste\xb6 jej macoch\xb1."%twoja
                        return self.msg
                        person_papa = Person.papa()   
                        
            if Person.mama() > 0:
                if Me.conj() == person_mama :
                    if Person.g(): 
                        self.msg = "%s pasierb. Jeste\xb6 jego ojczymem."%twoj
                        return self.msg
                    else:
                        self.msg = "%s pasierbica. Jeste\xb6 jej ojczymem."%twoja
                        return self.msg
                        person_papa = Person.papa()                           
            
        except:
            pass            

        return self.msg


    def check_permission_to_edit(self, person):
        self.msg = ''
        me = self.login_dict
        if  person.value('uid') == me.value('uid'):
            self.msg  += "To jeste\xb6 Ty"
            return True

        if  person.value('uid') == me.papa():
            self.msg += "To jest Tw\xf3j Ojciec"
            return True

        if  person.value('uid') == me.mama():
            self.msg += "To jest Twoja Matka"
            return True

        if  person.value('uid') == me.conj():
            self.msg += "To jest Tw\xf3j m\xb1\xbf lub \xbfona"
            return True

        if  person.papa() == me.value('uid'):
            self.msg += "Jeste\xb6 zalogowany jako ojciec tej osoby "
            return True

        if  person.mama() == me.value('uid'):
            self.msg += "Jeste\xb6 zalogowana jako matka tej osoby "
            return True

        if  person.value('owner_uid') == me.value('uid'):
            self.msg += "Ty jeste\xb6 wla\xb6cicielem tego wpisu "
            return True

        if  person.value('owner_uid') == self.owner_uid:
            self.msg += " Pokaza\xb3e\xb6 dobre id %s %s"%(person.value('owner_uid'), self.owner_uid)
            return True

        if  self.am_i_superuser():
            self.msg += "jako SUPERUSER"
            return True

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
                s = "zmieniony przez: %s %s %s"%(changer.value('prenom'), changer.value('nom'), person.value('change_time'))
            else:
                s = "zmieniony przez: Anonimowy Anonim %s"%( person.value('change_time'))
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
        td.append('imi\xea')
        tr.append(td)
        td = HTMLgen.TD( align="left" )
        td.append('nazwisko')
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
        
        form = HTMLgen.Form( cgi="%s"%SCRIPT, submit=HTMLgen.Input(type='submit',value="szukaj"))
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

    def get_edit_form(self, idict, uid):
        table = HTMLgen.TableLite(border=0, cell_spacing=1, width=None, body=[])
        present_time_string = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
        for c in self.column_names[0:]:
            if c in hidden_for_editing:
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
                s = "%s :"%(c_polish[c])
                td.append(s)
                tr.append(td)
                td = HTMLgen.TD()
                input = HTMLgen.Input( type='text', name="%s"%c, value="%s"%idict.value(c) , size="60")
                if c == 'notes':
                    input = HTMLgen.Textarea(name="%s"%c, rows=2, cols=60, text="%s"%idict.value(c))

                if c == 'change_time':
                    input = HTMLgen.Input( type='text', name="%s"%c, value="%s"%present_time_string)
                td.append(input)
                tr.append(td)
                table.append(tr)
        form = HTMLgen.Form( cgi="%s"%SCRIPT, submit=HTMLgen.Input(type='submit',value="Zapisz"))
        form.append(table)
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
        image = HTMLgen.Image('%s'%( self.get_picture(idict)), width="150", height="200")
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
            cur = self.con.cursor()
            self.cur.execute(sql)
            d = self.cur.fetchall()
            result_previous=''
            if len(d) >= 1:
                # There is previous entry in databse for ip and command
                result_previous = d[0][1]
                # command was executed for ip last time at date
                # Now we are verifying if results were identical
                date = str(d[0][0])
                # Check if previous entry has result identical to new result
                sql="SELECT * FROM `results` WHERE `date`='%s' AND `ip`='%s' AND `command`='%s' AND `result`='%s';"%(date, ip,command, new_result)
                self.cur.execute(sql)
                d = self.cur.fetchall()
    
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
                self.cur.execute(sql)
                self.con.commit()
    
    def get_column_names(self):
        # Przeczytaj atrybuty tabeli 'nuke_genealogy' 
        self.cur.execute('DESCRIBE %s'% TABLE)
        columns = self.cur.fetchall()
        column_names=[]
        for i in columns:
            column_names.append(i[0])
        self.column_names = column_names

    def place_person(self, x, y, person, ring=2):
        RADIUS = 90
        COLOR = 'white' 
        FRAME_COLOR = 'rgb(20,250,20)'
        FRAME_WIDTH = '10'
        WIDTH =  '160'
        HEIGHT = '160' 
        X_OFF =  '20'  # 200 = WIDTH/2
        Y_OFF =  '20'  # 200 = HEIGHT/2
        CORNER = '20'
                                
        out = ''   
        name = "%s %s"%(person['prenom'], person['nom'])
        uid = person['uid']
        picture = "%s"%(self.get_picture(person) )
        
        genre ='f'
        if person.g():
            genre = 'm'
            FRAME_COLOR = 'rgb(20,150,20)'    
            
        out += '<symbol id="%s">'%(uid)
        
 

        if self.styl in [0,1]:
            # Zielony kwadrat 
            out += '<rect x="%s" y="%s" rx="%s" ry="%s" width="%s" height="%s" style="fill:%s ;stroke-width:%s;stroke:%s" />'%(X_OFF, Y_OFF, CORNER, CORNER, WIDTH, HEIGHT, COLOR, FRAME_WIDTH, FRAME_COLOR)

        if self.styl in [2,3,5]:
            # Zielone kółeczko 
            out += '<circle cx="%s" cy="%s" r="%s"  stroke="%s" stroke-width="%s" fill="%s"  />\n'%(100,100,  RADIUS, FRAME_COLOR, FRAME_WIDTH, COLOR)   

        if self.styl in [1,3]:    
            out += '<use x="10" y="10" transform="scale(1.0) translate(0,0)" xlink:href="#leaf%s%s"  filter="url(#Blur)" />'%(ring, genre)    
            
        img = '<image xlink:href="%s" x="%s" y="%s" width="90" height="120" <desc>%s</desc></image>'%(picture, 60, 35, name)
        out += '<a xlink:href="?action=show_tree&uid=%s"> %s </a>'%(uid, img)     
        out += '<a xlink:href="?action=show&uid=%s"> <text text-anchor="middle" style="font-family:Verdana;font-size:10"  x="%s" y="%s">%s</text></a>'%(uid, 100, 165, name)

        if self.styl >= 4:   
            # Zielone Listki
            out += '<use x="1" y="1" transform="scale(1.0) translate(0,0)" xlink:href="#ring%s%s"  filter="url(#Blur)" />'%(ring, genre)    
               
        out += '</symbol>' 
        out += '<use x="%s" y="%s" transform="scale(1.0) translate(0,0)" xlink:href="#%s"  />'%(x,y, uid)            
        return out

    def place_person_with_ancestors(self, gen, x_distance, y_distance, x, y, person):   
        RADIUS = 90
        COLOR = 'white' 
        out = ""
    
        if gen > 5 :
            return out
        gen += 1 
        
        ring = gen
        if ring > 6: ring = 6
        if ring < 1: ring = 1        
        

                    
        if int(person.papa()) > 0:
            p = self.get_dict(person.papa())                      
            out += self.place_person_with_ancestors(gen, x_distance/2, y_distance, x-x_distance, y-y_distance, person=p )
            
        if int(person.mama()) > 0:
            m = self.get_dict(person.mama())                      
            out += self.place_person_with_ancestors(gen, x_distance/2, y_distance, x+x_distance, y-y_distance, person=m )

        out += self.place_person(x,y,person, ring=gen)

        return out
    
    
    def show_tree(self, row, children, uid, owner_uid):    

        #KP debugging
        # doc.append(sql)
        width = 2000
        height =1600
        X_CENTER = 1000
        Y_CENTER = 600
        SCALE = 0.7
           
        person = self.get_dict(uid)
                
        svg = '<center><svg width="%s" height="%s"><g transform="scale(%s)">'%(width, height, SCALE) 
        

        
        doc = []
        filters = Leafs.Filters()
        doc.append(filters.get())

        scale = {1:0.25, 2:0.27, 3:0.30, 4:0.34, 5:0.36, 6:0.40}
        for i in range(1,7):
            leaf = Leafs.Leaf(name='leaf%s'%(i), scale=scale[i])    
            doc.append(leaf.get('f'))

        scale = {1:0.25, 2:0.27, 3:0.30, 4:0.34, 5:0.36, 6:0.40}
        for i in range(1,7):
            for genre in ['m','f']:
                leaf = Leafs.Leaf(name='leaf%s%s'%(i,genre), scale=scale[i])    
                doc.append(leaf.get(genre))
                  

        leafs_number = {1:26, 2:24, 3:22, 4:20, 5:18, 6:16}
        for i in range(1,7):
            for genre in ['m','f']:
                ring = Leafs.Reef(name='ring%s%s'%(i,genre), leaf_name='leaf%s%s'%(i,genre), leaf_scale=0.1, leafs_number=leafs_number[i],  radius=100)
                doc.append(ring.get())
                
        leafs_number = {1:26, 2:24, 3:22, 4:20, 5:18, 6:16}
        for i in range(1,7):
            ring = Leafs.Reef(name='ring%s'%(i), leaf_name='leaf%s'%(i), leaf_scale=0.1, leafs_number=leafs_number[i],  radius=100)
            doc.append(ring.get())
                
        
        svg += '\n'.join(doc)
 
        # svg += '\n \n'.join(children)    
        
        #  doc.append('<use x="0" y="0" transform="translate(0,0)" xlink:href="#ring"  filter="url(#Blur)" />')

        if person.conj() >0:        
            svg += self.place_person( X_CENTER+130, Y_CENTER+10, self.get_dict(person.conj()), ring=3)         
        
        # svg += self.place_person_with_ancestors(3, x_distance=200, y_distance=120, x=600, y=400, person=person)
        svg += self.place_person_with_ancestors(2, 300, 150, X_CENTER, Y_CENTER, person) 


                
        
        i = 0
        n = len(children)
        start = X_CENTER - (100*(n-1) )
        for child_row in children:
            child = self.convert_sqlrow_to_dict(child_row)
            # svg += self.place_person_with_ancestors(5, 300, 150, start+200*i, Y_CENTER+200, child)
            svg += self.place_person( start+200*i, Y_CENTER+200, child, ring=2 )
            i += 1
        svg += '</g></svg></center>'

        return svg
        
    
    def main(self, form, login_uid):
        stylesheets = [ "css/genealogy_style.css",
                      "https://cdn.jsdelivr.net/npm/bootstrap@5.3.1/dist/css/bootstrap.min.css"]
        
        # scripts = ["../js/sorttable.js", "../js/clickable.js"]
        scripts = ["", ""]
        meta = '<META HTTP-EQUIV="Content-Type" content="text/html; charset=ISO-8859-2">'
    
        doc_simple  = HTMLGen.SimpleDocument(cgi="True", 
                                             screen_capture_injected="true", 
                                             meta=meta,
                                             title="Genealogia", 
                                             stylesheet=stylesheets, 
                                             script=scripts)
     
        doc = HTMLgen.Div(id = 'main') 
        # main = HTMLgen.Div(id = 'main') 

        sql = ''
        # Create instance of FieldStorage 
        # form = cgi.FieldStorage() 

        self.login_dict = self.get_dict(login_uid)
    
        # Get data from fields
        action = form.getvalue('action')
        uid     = form.getvalue('uid')
        # if uid is None: uid = login_uid 
        id      = form.getvalue('id')
        order = form.getvalue('order')
        checkbox = form.getvalue('checkbox')
        checkboxid = form.getvalue('checkboxid')
        owner_uid = form.getvalue('owner_uid')
        dob = form.getvalue('dob')
        nom = form.getvalue('nom')
        prenom = form.getvalue('prenom')
        genre = form.getvalue('genre')
        # this is for file upload
        dfile_name = form.getvalue('file_name')
        prefix = form.getvalue('prefix')
        profile_picture = form.getvalue('profile_picture') 
        styl = form.getvalue('styl')
        
        self.styl = 0 
        try:
            if int(styl) > 0:
                self.styl = int(styl) 
        except:
            pass        
        
        MAX_SIZE = 2*1024*1024
        valid_extentions = ['jpg','gif']
        path_start = ''

        if action == None: action = 'show'
        if order == None: order = "0"
        if owner_uid == None: 
            owner_uid= '1'
        self.owner_uid = owner_uid
        if id == None: id=0
        if uid == None: uid = login_uid
        if nom == None: nom = ""
        if prenom == None: prenom = ""
        if dob == None: dob = ""
    

        if form.has_key('file'):
            fileitem = form['file']
        
            if fileitem.filename:
            # if fileitem.filename:
                # strip leading path from file name to avoid directory traversal attacks^M
                fname = os.path.basename(fileitem.filename)

                file_name,extention = fname.split('.')
                ext = extention.lower()
                if ext in valid_extentions:
                    if dfile_name == '':
                        filename= "%s.%s"%(file_name, ext) 
                        destination = "%s/%s"%(PATH_TO_PICTURES, filename)  # /var/data/abcd.jpg 
                    else:
                        if prefix == 'YES':
                            timestamp = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d-%H-%M-%S')
                            filename= "%s_%s.%s"%(dfile_name, timestamp, ext) 
                            destination = "%s/%s"%(PATH_TO_PICTURES, filename) 
                              # /var/data/500_2015-12-23-12-03-34.jpg 
                        else:
                            filename= "%s.%s"%(dfile_name, ext) 
                            destination = "%s/%s"%(PATH_TO_PICTURES, filename) 
                              # /var/data/500.jpg 

                    file = fileitem.file.read()
                    # Check file type, and size etc
                    size = len(file)
                    if size < MAX_SIZE:
                        abs_destination = "%s%s"%(path_start,destination)
                        open( abs_destination, 'wb').write(file)
                        msg = 'SUCCESS: The file %s of size %s was uploaded under name %s '%(file_name, size, destination)

                        doc.append('profile picture %s'%profile_picture) 
                        if profile_picture == 'YES':
                            sql = "UPDATE  `%s` SET  `picture_id` = '%s' WHERE `uid`='%s';"%(TABLE, filename, uid)
                            self.cur.execute(sql)
                            self.con.commit()
                    else:
                        msg = "ERROR: File size %s is too big >%s"%(size, MAX_SIZE)
                else:
                    msg = 'ERROR: File extention is %s. Must be %s'%(ext,  valid_extentions)
                    destination = "  %s"%(file_name)

            else:
                msg = 'ERROR: File was not uploaded'
    

        PARAMS = ",".join(["%s=%s"%(i,form.getvalue(i)) for i in form.keys()])
        # cur = self.con.cursor()
    
        if True:
            # wczytaj parametry zalogowanego uzytkownika
            self.cur.execute("SELECT * from %s WHERE uid='%s';"%(TABLE, login_uid))
            row = self.cur.fetchall()
            self.login_dict = self.convert_sqlrow_to_dict(row[0])
            doc_simple.append(self.show_menu(uid))
    
        '''
        if checkbox is not None and checkboxid is not None and table in ['nuke_genealogy','commands']:
            ret = self.modify_checkbox(con, checkbox, checkboxid, table)
            # doc.append(HTMLgen.Heading(2, ret))
        '''
       
        if True:     
            if action == 'delete':
                sql="DELETE FROM %s WHERE id='%s';"%(TABLE, id)
            
            if action == 'add':
                f = ",".join(self.column_names)
                values =",".join([ "'%s'"%form.getvalue(i) for i in self.column_names[1:]])
                sql="INSERT INTO %s(%s) VALUES(%s);"%(TABLE, f, values)
            
        
            if action == 'save':
                v = {}
                values = ''
                period =''
                for i in self.column_names[1:]:
                    v= form.getvalue(i)
                    if v is None : v = ''
        
                    # values =",".join([ "`%s`='%s'"%(i, v[i]) for i in self.column_names[1:] ])
            
                    if i in dates_items and v == '':
                        values +=  "%s`%s`= NULL "%(period,i) 
                    else: 
                        values +=  "%s`%s`='%s'"%(period,i, v) 
                    period =','

                sql="UPDATE `%s` SET %s WHERE `%s`.`uid`=%s;"%(TABLE, values, TABLE, uid)
                self.cur.execute(sql)
                self.con.commit()
                action = "show"
            
            if action == 'edit':
                self.cur.execute("SELECT * from %s WHERE uid='%s';"%(TABLE, uid))
                row = self.cur.fetchall()
                doc.append(self.edit_item(row, uid))
            
            if action == 'add_parent':
                genre = form.getvalue('genre')
                dwarning = HTMLgen.Div(id = 'warning')
                dwarning.append('Nie dopisuj \xbfadnej osoby dwa razy.')
                dwarning.append(HTMLgen.BR())
                dwarning.append('Je\xbfeli ten rodzic jest juz dopisany,')
                dwarning.append(HTMLgen.BR())
                dwarning.append('wycofaj si\xea i wybierz opcje Do\xb3\xb1cz (-->)!')
                
                doc.append(dwarning)
                dict = Dict( genre=genre, uid= self.get_new_uid())
                doc.append(self.add_parent(dict, uid))

            if action == 'save_parent':
                v = {}
                for i in self.column_names:
                    v[i]= form.getvalue(i)
                    if v[i] is None : v[i] = ''
        
                uid = form.getvalue('uid')
                child_uid = form.getvalue('child_uid')
                _list =",".join([ "`%s`"%(i) for i in self.column_names ])
                values =",".join([ "'%s'"%(v[i]) for i in self.column_names ])
                sql="INSERT INTO `%s` (%s) VALUES (%s) ;"%(TABLE, _list, values)
                self.cur.execute(sql)
                self.con.commit()
                if form.getvalue('genre') == '1':
                    sql = "UPDATE  `%s` SET  `pere` = '%s' WHERE `uid`='%s';"%(TABLE, uid, child_uid)
                else:
                    sql = "UPDATE  `%s` SET  `mere` = '%s' WHERE `uid`='%s';"%(TABLE, uid, child_uid)
                self.cur.execute(sql)
                self.con.commit()
                action = 'show' 
            
            if action == 'add_spouse':
                genre = form.getvalue('genre')
                dwarning = HTMLgen.Div(id = 'warning')
                dwarning.append('Nie dopisuj \xbfadnej osoby dwa razy.')
                dwarning.append(HTMLgen.BR())
                dwarning.append('Je\xbfeli ten ma\xb3\xbfonek jest juz dopisany,' )
                dwarning.append(HTMLgen.BR())
                dwarning.append('wycofaj si\xea i wybierz opcje Do\xb3\xb1cz (-->)!')

                idict = Dict( genre=genre, uid= self.get_new_uid(), conjoint=uid)
                doc.append(dwarning)
                doc.append(self.add_spouse(idict, uid))
                action = 'show' 

            if action == 'save_spouse':
                v = {}
                for i in self.column_names:
                    v[i]= form.getvalue(i)
                    if v[i] is None : v[i] = ''
        
                uid = form.getvalue('uid')
                spouse_uid = form.getvalue('spouse_uid')
                _list =",".join([ "`%s`"%(i) for i in self.column_names ])
                values =",".join([ "'%s'"%(v[i]) for i in self.column_names ])
                sql="INSERT INTO `%s` (%s) VALUES (%s) ;"%(TABLE, _list, values)
                self.cur.execute(sql)
                self.con.commit()
                sql = "UPDATE  `%s` SET  `conjoint` = '%s' WHERE `uid`='%s';"%(TABLE, uid, spouse_uid)
                self.cur.execute(sql)
                self.con.commit()
                action = 'show' 
            
            if action == 'add_child':
                dwarning = HTMLgen.Div(id = 'warning')
                dwarning.append('Nie dopisuj \xbfadnej osoby dwa razy.')
                dwarning.append(HTMLgen.BR())
                dwarning.append('Je\xbfeli ten potomek jest juz dopisany,' )
                dwarning.append(HTMLgen.BR())
                dwarning.append('wycofaj si\xea i wybierz opcje Do\xb3\xb1cz (-->)!')

                genre = form.getvalue('genre')
                parent_idict = self.get_dict(uid)
                if parent_idict.value('genre') > 0:
                    child_dict = Dict( genre=genre, uid= self.get_new_uid(), pere=uid)
                else:
                    child_dict = Dict( genre=genre, uid= self.get_new_uid(), mere=uid)


                doc.append(dwarning)
                doc.append(self.add_child(child_dict, uid))

            if action == 'save_child':
                v = {}
                for i in self.column_names:
                    v[i]= form.getvalue(i)
                    if v[i] is None : v[i] = ''
        
                parent_uid = form.getvalue('parent_uid')
                child_uid = form.getvalue('child_uid')
                _list =",".join([ "`%s`"%(i) for i in self.column_names ])
                values =",".join([ "'%s'"%(v[i]) for i in self.column_names ])
                sql="INSERT INTO `%s` (%s) VALUES (%s) ;"%(TABLE, _list, values)
                self.cur.execute(sql)
                self.con.commit()
                
                idict = self.get_dict(parent_uid)
                if idict.value('genre') > 0:
                    sql = "UPDATE  `%s` SET  `pere` = '%s' WHERE `uid`='%s';"%(TABLE, uid, child_uid)
                else:
                    sql = "UPDATE  `%s` SET  `mere` = '%s' WHERE `uid`='%s';"%(TABLE, uid, child_uid)

                self.cur.execute(sql)
                self.con.commit()
                action = 'show' 
            
            if action == 'rlink_papa':
                uid = form.getvalue('uid')
                papa_uid = form.getvalue('who')
                sql = "UPDATE  `%s` SET  `pere` = '%s' WHERE `uid`='%s';"%(TABLE, papa_uid, uid)
                self.cur.execute(sql)
                self.con.commit()
                action = 'show' 

            if action == 'rlink_mama':
                uid = form.getvalue('uid')
                mama_uid = form.getvalue('who')
                sql = "UPDATE  `%s` SET  `mere` = '%s' WHERE `uid`='%s';"%(TABLE, mama_uid, uid)
                self.cur.execute(sql)
                self.con.commit()
                action = 'show' 
            
            if action == 'rlink_spouse':
                uid = form.getvalue('uid')
                spouse_uid = form.getvalue('who')
                sql = "UPDATE  `%s` SET  `conjoint` = '%s' WHERE `uid`='%s';"%(TABLE, spouse_uid, uid)
                self.cur.execute(sql)
                self.con.commit()

                # Te trzy linie dopisuja linka w rekordzie spouse wskazujacego na UID
                # NIE MOZEMY TEGO ROBIC GDY NIE MAMY KONTROLI NA TYM WPISEM
                '''
                sql = "UPDATE  `%s` SET  `conjoint` = '%s' WHERE `uid`='%s';"%(TABLE, uid, spouse_uid)
                self.cur.execute(sql)
                self.con.commit()
                '''
  
                action = 'show' 
            
            if action == 'rlink_child':
                uid = form.getvalue('uid')
                idict = self.get_dict(uid)
                child_uid = form.getvalue('who')
                if int(idict.value('genre')) > 0 :
                    sql = "UPDATE  `%s` SET  `pere` = '%s' WHERE `uid`='%s';"%(TABLE, uid, child_uid)
                else:               
                    sql = "UPDATE  `%s` SET  `mere` = '%s' WHERE `uid`='%s';"%(TABLE, uid, child_uid)

                self.cur.execute(sql)
                self.con.commit()
                action = 'show' 
            
            if action == 'enable':
                sql = "UPDATE  `mmsgennodes`.`%s` SET  `enabled` =1 WHERE `enabled`=0;"%(table)
                self.cur.execute(sql)
                row = self.cur.fetchall()
            
            if action == 'disable':
                sql = "UPDATE  `mmsgennodes`.`%s` SET  `enabled` =0 WHERE `enabled`=1;"%(table)
                self.cur.execute(sql)
                row = self.cur.fetchall()
            
            if action in ['show', 'login', 'show_tree']:
                # d = self.get_dict(uid)
                self.cur.execute("SELECT * from %s WHERE uid='%s';"%(TABLE,uid))
                row = self.cur.fetchall()
        
                if row[0][2] == 1: # 0 Kobieta 1 Mezczyzna
                    # Dla kobiet
                    # Szukaj osob ktore maja wpisane uid w polu mere/matka
                    # mere = row[0][13]
                    # doc.append(mere)
                    self.cur.execute("SELECT * from %s WHERE pere='%s' ORDER BY  `naissance` ASC ;"%(TABLE,uid))
                    children = self.cur.fetchall()
                else:
                    # Dla mezczyzn
                    # Szukaj osob ktore maja wpisane uid w polu pere/ojciec
                    # pere = row[0][12]
                    # doc.append(pere)
                    self.cur.execute("SELECT * from %s WHERE mere='%s' ORDER BY  `naissance` ASC ;"%(TABLE,uid))
                    children = self.cur.fetchall()
        
                # for debugging
                # doc.append(children)
                
                # doc.append( row[0]) 
                # svg = self.show_tree(row[0], children, uid, owner_uid)
                # doc.append(svg)
                
                if action in ['show_tree']:
                    svg = self.show_tree(row[0], children, uid, owner_uid)
                    doc_simple.append(svg)
                else:                    
                    doc.append(self.show_item(row, children, uid, owner_uid))
                

            if action in ['link_mama','link_papa','link_child', 'link_spouse']:
                wh = []
                if (prenom != ""): 
                    wh.append("prenom LIKE '%s'"%(prenom))
                if (nom != ""): 
                    wh.append("nom LIKE '%s'"%(nom))
                if not (genre is None): 
                    wh.append("genre='%s'"%(genre))

                if action in ['link_mama','link_papa']:
                    if not (dob is None) and not (dob == ''): 
                        wh.append("naissance < '%s'"%(dob))  # Tylko osoby starsze od daty urodzenia we wpisie 

                if action in ['link_child']:
                    if not (dob is None) and not (dob == ''): 
                        wh.append("naissance > '%s'"%(dob))  # Tylko osoby starsze od data urodzenia we wpisie 

                # ADD HERE to wh SQL LIMIT 

                where = " AND ".join(wh)

                sql = "SELECT * from %s WHERE %s;"%(TABLE, where)
                self.cur.execute(sql)
                rows= self.cur.fetchall()
                doc.append(self.show_search_results(rows, action, genre, uid, prenom, nom, dob))

            if action in ['list']:
                sql = "SELECT * FROM %s ORDER BY `change_time` DESC LIMIT 50;"%(TABLE)
                self.cur.execute(sql)
                rows= self.cur.fetchall()
                doc.append(self.show_list(rows))

            if action in ['show_pictures']:
                sql = "SELECT * FROM %s ORDER BY `change_time` DESC LIMIT 50;"%(TABLE)
                self.cur.execute(sql)
                rows= self.cur.fetchall()
                idict = self.get_dict(uid)
                doc.append(self.show_pictures(idict = idict))
 
 
            # print sql
            if action in ['show', 'delete', 'add', 'save', 'disable', 'enable']: 
                if sql is not '':
                    try:
                        self.cur.execute(sql)
                        self.con.commit()
                    except mdb.Error, e:
                        if self.con:
                            self.con.rollback()
                    
                        # doc.append(sql)
                        doc.append(HTMLgen.Heading(2, "Error %d: %s" % (e.args[0],e.args[1])))
        
                        # sys.exit(1)
                
                    #  finally:    
                    #     if con:    
                    #         con.close()
            
            '''
            if table != 'execute':
                order_by = 'id'
                sql = "SELECT * FROM %s ORDER BY %s LIMIT %s;"%(TABLE, order_by, SQL_LIMIT)
                # doc.append(HTMLgen.PRE(' SQL : %s'%sql))
                cur.execute(sql)
                rows = cur.fetchall()
        
                # doc.append(show_table(rows, table, column_names, order))
            '''
    
        doc_simple.append(doc)
        
        print doc_simple
        

                
 
def login_screen( prompt = "Login"):

    stylesheets = [ "css/genealogy_style.css",
                    "css/style.css",
                     "https://cdn.jsdelivr.net/npm/bootstrap@5.3.1/dist/css/bootstrap.min.css"
                  ]
    
    scripts = ["", ""]
    meta = '<META HTTP-EQUIV="Content-Type" content="text/html; charset=ISO-8859-2">'
    
    doc_simple  = HTMLGen.SimpleDocument(cgi="True", screen_capture_injected="true", meta=meta,\
                    title="Genealogia", stylesheet=stylesheets, script=scripts)
     
    doc = HTMLgen.Div(id = 'menu') 
           
    banner =   HTMLgen.Div(id = 'login')
    banner.append('%s'%prompt)

    tb = HTMLgen.TableLite(border=0, cell_spacing='10', cell_padding='20', width="auto", body=[], body_color="#AAFFAA")
    tr = HTMLgen.TR()
    td = HTMLgen.TD()


    uid  = HTMLgen.Input( type='text', name="uid" )
    key  = HTMLgen.Input( type='password', name="key" )
    login  = HTMLgen.Input( type='hidden', name="action", value='login' )
    
    form = HTMLgen.Form( cgi="%s"%SCRIPT, submit=HTMLgen.Input(type='submit',value="Wejdz"))
    
    form.append(HTMLgen.BR())
    form.append('Indentyfikator:')
    form.append(HTMLgen.BR())
    form.append(uid)

    form.append(HTMLgen.BR())
    form.append('Klucz:')
    form.append(HTMLgen.BR())    

    form.append(key)
    form.append(HTMLgen.BR())
    form.append(login)

    form.append(HTMLgen.BR())

    td.append(form)
    tr.append(td)
    tb.append(tr)
    
    doc.append(tb)

    banner.append(doc)
    
    doc_simple.append(banner)

    return str(doc_simple)
        

def logout_screen():
    
    stylesheets = [ "css/genealogy_style.css", "css/style.css"]
    scripts = ["", ""]
    meta = '<META HTTP-EQUIV="Content-Type" content="text/html; charset=ISO-8859-2">'
    
    doc_simple  = HTMLGen.SimpleDocument(cgi="True", screen_capture_injected="true", meta=meta,\
                    title="Genealogia", stylesheet=stylesheets, script=scripts)
     
    doc = HTMLgen.Div(id = 'menu') 
    demo = HTMLgen.Div(id = 'login') 
           
    banner =   HTMLgen.Div(id = 'login')
    banner.append('Wyszed\xB3e\xB6 z Drzewa')
    
    doc_simple.append(banner)
    
    href = HTMLgen.Href('%s'%SCRIPT,  'wr\xF3\xE6 do Drzewa')
    
    doc.append(href)
    banner.append(doc)
    doc_simple.append(banner)

    return str(doc_simple)
            
    
    
    '''
    html = 'Content-type: text/html\n\n'
    html += '<html>'
    html += '<body>'
    html += '<h1>Wyszedles !</h1>'
    html += '<pre> Do zabaczenia </pre>'
    html += '<a href="%s">wracaj</a><br>'%(SCRIPT)
    html += '</body>'
    html += '</html>'
    return html
    '''

def main_cookie():
    form = cgi.FieldStorage() 
    _cookie = LoginCookie(login_screen, logout_screen, prompt="Zaloguj si\xEA do Drzewa")
    (login_uid, key, cont) = _cookie.test_login_cookie(form )
    if cont:
       tree = FamilyTree()
       tree.main(form, login_uid)


if '__main__' == __name__:
    try:   # NEW
        # print("Content-type: text/html\n")   # say generating html
        main_cookie()
    except:
        cgi.print_exception()
                                             
