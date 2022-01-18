#!/usr/bin/env python3
# -*- coding: utf-8 -*-


#central bank actions tracking.
#url:  http://www.chinamoney.com.cn/chinese/yhgkscczh/

#extract all the tables for history action records.

#use selenium to handle javascript table presentation

from selenium.webdriver import Firefox
import time
import pandas as pd
import numpy as np
import sqlite3

executable_path="/home/alpha/Projects/database/web_scripting/geckodriver"
url="http://www.chinamoney.com.cn/chinese/yhgkscczh/"
#entries=[] #list of list


#browser=Firefox(executable_path=executable_path)
#
#browser.get(url)
#
##get table contents on current page
#y=browser.find_element_by_tag_name("tbody")
##strings of table contents  separated by \n
#y.text
#
#single_entry=[]
#entries=[] #list of list
#
##processing text into list items
#
#
##reach next page
#z=browser.find_element_by_link_text('下一页')
#z.click()
#
#
##each click wait for 5 seconds
#time.sleep(5)


def process_table_entries(text,entries):
    """
    convert table contents extracted from web page into list and make change to entries list.
    """
    string_list=text.split('\n')
    for i in string_list:
        entries.append(i.split(' '))
    
    pass
#    df=pd.DataFrame(np.array(entries),columns=['操作日期','期限(天)','交易量(亿)','中标利率(%)','正/逆回购'])
#    return df



def get_entries(pages=146):
    """
    grab all entries within given pages: click times=pages-1
    """
    global url
    global executable_path
    entries=[]
    browser=Firefox(executable_path=executable_path)
    browser.get(url)
    time.sleep(5)
    y=browser.find_element_by_tag_name("tbody")
    text=y.text
    print(text)
    time.sleep(3)
    process_table_entries(text,entries)
    for i in range(1,pages):
        #click 145(total page -1) times
        z=browser.find_element_by_link_text('下一页')
        z.click()
        #wait for 3 seconds for page to load
        time.sleep(5)
        #get table contents on current page
        m=browser.find_element_by_tag_name("tbody")
        text=m.text
        print(text)
        process_table_entries(text,entries)
        
    return entries


def create_entry_database(entries,database):
    """
    store enries in database
    """
    table_name='actions'
    db=sqlite3.connect(database)
    cursor=db.cursor()
    cursor.execute("CREATE TABLE {a} ('操作日期' text, '期限(天)' text, '交易量(亿)' text, '中标利率(%)' text, '正/逆回购' text)".format(a=table_name))
    db.commit()
    
    #insert entires into database
    for entry in entries:
        value_1=entry[0]
        value_2=entry[1]
        value_3=entry[2]
        value_4=entry[3]
        value_5=entry[4]
        row=(value_1,value_2,value_3,value_4,value_5)
        cursor.execute("INSERT INTO {a} VALUES{b}".format(a=table_name,b=row))
    db.commit()
    db.close()
    print('database complete.')
    pass



def database_entry_update(database,pages):
    """
    compare enries from database and web extracts and add new updates
    input pages must be no less than the page number of first entry in database,
    otherwise algorithm will go wrong.
    """
    #request recent entries
    recent_entries=get_entries(pages)
    #recent_data=pd.DataFrame(np.array(recent_entries),columns=['操作日期','期限(天)','交易量(亿)','中标利率(%)','正/逆回购'])
    
    #compare with database entry
    db=sqlite3.connect(database)
    cursor=db.cursor()
    cursor.execute("SELECT Count(*) FROM 'actions'")
    existing_records=int(cursor.fetchall()[0][0])       #count the number of existing records
    db.commit()
    db.close()
    
    #check total records number on webpage
    browser=Firefox(executable_path=executable_path)
    browser.get(url)
    #wait for 5 seconds for page to load
    time.sleep(5)
    y=browser.find_element_by_class_name('records-total')
    total_records_on_website=int(y.text)
    number_to_be_added=total_records_on_website-existing_records
    print('numbers of entries to be added into database: '+str(number_to_be_added))
    
    if number_to_be_added==0:
        print(database+" is already up to date.")
        return 0
    else:
        #construct added entries
        added_entries=[]
        for i in range(0,number_to_be_added):
            added_entries.append(recent_entries[i])
        print('new entries to be added to database: ')
        print(added_entries)
        #inserting rows into table
        db=sqlite3.connect(database)
        cursor=db.cursor()
        added_entries=added_entries[::-1]  #inserting recent date first
        for entry in added_entries:
            value_1=entry[0]
            value_2=entry[1]
            value_3=entry[2]
            value_4=entry[3]
            value_5=entry[4]
            row=(value_1,value_2,value_3,value_4,value_5)
            cursor.execute("INSERT INTO {} VALUES {}".format('actions',row))
        db.commit()
        db.close()
        print(database+" sucessfully updated.")
        return 0
























