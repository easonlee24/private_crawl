# -*- coding: utf8 -*-
# @author: 'lizhen05'
# @date: '2017-11-26'

#--encoding:utf-8--  
#  
import MySQLdb  
import sys  
reload(sys)  
sys.setdefaultencoding('utf8')
  
class MySQLHelper:  
    myVersion=0.1  
    def __init__(self,host,user,password,charset="utf8"):  
        self.host=host  
        self.user=user  
        self.password=password  
        self.charset=charset  
        try:  
            self.conn=MySQLdb.connect(host=self.host,user=self.user,passwd=self.password)  
            self.conn.set_character_set(self.charset)  
            self.cursor=self.conn.cursor()  
        except MySQLdb.Error as e:  
            print ('MySql Error : %d %s' %(e.args[0],e.args[1]))  
      
    def use_db(self,db):  
        try:  
            self.conn.select_db(db)  
        except MySQLdb.Error as e:  
            print ('Set Db Error: %d %s' %(e.args[0],e.args[1]))  

    def create_database(self, database):
        try:
            sql = "create database if not exists %s" % database
            self.execute(sql)
        except MySQLdb.Error as e:
            print('Create Database Error: %s SQL: %s' % (e, sql))

    """
    Execute a sql statement, do not help it return.These sql statement can
    be: create database/create table/drop table/delete...
    """
    def execute(self, sql):
        self.cursor.execute(sql)
      
    def query(self,sql):  
        try:  
            rows=self.cursor.execute(sql)  
            return rows;  
        except MySQLdb.Error as e:  
            print('MySql Error: %s SQL: %s'%(e, sql.encode('utf8')))  
              
    def query_only_row(self,sql):  
        try:  
            self.query(sql)  
            result=self.cursor.fetchone()  
            desc=self.cursor.description  
            row={}  
            for i in range(0,len(result)):  
                row[desc[i][0]]=result[i]  
            return row;  
        except MySQLdb.Error as e:  
            print('MySql Error: %s SQL: %s'%(e,sql))  
      
    def query_all(self,sql):  
        try:  
            self.query(sql)  
            result=self.cursor.fetchall()  
            desc=self.cursor.description  
            rows=[]  
            for cloumn in result:  
                row={}  
                for i in range(0,len(cloumn)):  
                    row[desc[i][0]]=cloumn[i]  
                rows.append(row)    
            return rows;  
        except MySQLdb.Error as e:  
            print('MySql Error: %s SQL: %s'%(e,sql))  
      
    def insert(self,tableName,pData):  
        try:  
            newData={}  
            for key in pData:  
                #newData[key]="'"+ MySQLdb.escape_string(pData[key])+"'"  
                newData[key]="'"+ MySQLdb.escape_string(pData[key])+"'"  
            key=','.join(newData.keys())  
            value=','.join(newData.values())  
            sql="replace into "+tableName+"("+key+") values("+value+")"  
            self.query("set names 'utf8'")  
            self.query(sql)  
            self.commit()  
        except MySQLdb.Error as e:  
            print('MySql Error: %s %s'%(e.args[0],e.args[1]))  
            self.conn.rollback()  
            print('MySql Error: %s %s'%(e.args[0],e.args[1]))  
      
    def update(self,tableName,pData,whereData):  
        try:  
            newData=[]  
            keys=pData.keys()  
            for i in keys:  
                item="%s=%s"%(i,"'""'"+pData[i]+"'")  
                newData.append(item)  
            items=','.join(newData)  
            newData2=[]  
            keys=whereData.keys()  
            for i in keys:  
                item="%s=%s"%(i,"'""'"+whereData[i]+"'")  
                newData2.append(item)  
            whereItems=" AND ".join(newData2)  
            sql="update "+tableName+" set "+items+" where "+whereItems  
            self.query("set names 'utf8'")  
            self.query(sql)  
            self.commit()  
        except MySQLdb.Error as e:  
            self.conn.rollback()  
            print('MySql Error: %s %s'%(e.args[0],e.args[1]))  
        finally:  
            self.close()  
      
    def get_last_insert_rowid(self):  
        return self.cursor.lastrowid  
      
    def get_row_count(self):  
        return self.cursor.rowcount  
      
    def commit(self):  
        self.conn.commit()  
      
    def close(self):  
        self.cursor.close()  
        self.conn.close()  


if __name__ == '__main__':
    mysql_helper = MySQLHelper("localhost", "root", "123456")
    oa_database = "oa"
    mysql_helper.create_database(oa_database)
    mysql_helper.use_db(oa_database)
    create_table_sql = "create table if not exists article_info(" \
                        "collection_id varchar(50) NOT NULL," \
                        "source_id varchar(50) NOT NULL,"\
                        "system_id varchar(50) NOT NULL,"\
                        "ro_id varchar(50) NOT NULL,"\
                        "work_id varchar(50) NOT NULL,"\
                        "doi varchar(50) NOT NULL,"\
                        "work_title varchar(50) NOT NULL,"\
                        "issn varchar(20),"\
                        "eissn varchar(20),"\
                        "collection_title varchar(50) NOT NULL,"\
                        "platform_url varchar(50) NOT NULL,"\
                        "source_name varchar(50) NOT NULL,"\
                        "keywords text,"\
                        "language varchar(20) NOT NULL,"\
                        "abstract text,"\
                        "country varchar(20) NOT NULL,"\
                        "publish_year varchar(20) NOT NULL,"\
                        "publish_date varchar(20) NOT NULL,"\
                        "volume varchar(10) NOT NULL,"\
                        "issue varchar(10) NOT NULL,"\
                        "access_url varchar(100) NOT NULL,"\
                        "license_text text,"\
                        "license_url varchar(50),"\
                        "copyright text,"\
                        "ro_title varchar(50) NOT NULL,"\
                        "xml_url varchar(200) NOT NULL,"\
                        "pdf_uri varchar(200) NOT NULL,"\
                        "pdf_access_url varchar(200) NOT NULL,"\
                        "creator varchar(20) NOT NULL,"\
                        "create_time datetime NOT NULL,"\
                        "finished tinyint(1) NOT NULL DEFAULT 0,"\
                        "extra varchar(50) comment 'extra info',"\
                        "PRIMARY KEY(work_id)) DEFAULT CHARSET=utf8;"
    mysql_helper.execute(create_table_sql)

    author_create_table_sql = "create table if not exists article_author("\
                              "work_id varchar(50) NOT NULL,"\
                              "author_name varchar(50) NOT NULL,"\
                              "institution_name text,"\
                              "PRIMARY KEY(work_id, author_name)) DEFAULT CHARSET=utf8;"
    mysql_helper.execute(author_create_table_sql)
