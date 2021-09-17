import mysql.connector
import pandas as pd
import os

from mysql.connector import Error
from os import listdir

# define db connection 
db_host = 'localhost'
db_name = 'mydatabase'
db_user = 'root'
db_password = 'password'

# for testing
data_import_limit = 0

# list all .csv files in the current directory
filenames = listdir('.')
csv_files = [ filename for filename in filenames if filename.endswith('.csv')] 

# define custom headers
global_data_header = 'year int, avg_temp DECIMAL(10,2)'
city_data_header = 'year int, city nvarchar(50), country nvarchar(50), avg_temp DECIMAL(10,2)'
city_list_header = 'city nvarchar(50), country nvarchar(50)'

try:
  connection = mysql.connector.connect(
    host = db_host, 
    database = db_name, 
    user = db_user, 
    password = db_password
    )
  if connection.is_connected():

    cursor = connection.cursor()
    cursor.execute('SELECT DATABASE();')
    record = cursor.fetchone()
    print("You are connected to database: ", record)

    for csv_file in csv_files:
      data = pd.read_csv(csv_file, index_col=False, delimiter = ',')

      # replace empty fields with NULL
      data = data.astype(object).where(pd.notnull(data), None)
      table_name = os.path.splitext(csv_file)[0]

      cursor.execute('DROP TABLE IF EXISTS ' + table_name + ';')
      print('Creating table "' + table_name + '"')

      table_header = '' 
      if table_name == 'global_data':
        table_header = global_data_header
      elif table_name == 'city_list': 
        table_header = city_list_header
      elif table_name == 'city_data': 
        table_header = city_data_header

      # create tables
      sql_query = 'CREATE TABLE ' + table_name + '(' + table_header + ')'
      print('Executing SQL query:\n' + sql_query)
      cursor.execute(sql_query)
      print('Table "' + table_name + '" created.')
      
      table_format = '%s'
      for i in range(0,len(data.columns)-1):
        table_format += ',%s'
        i += 1

      # loop through data
      for i,row in data.iterrows():
        sql_query = 'INSERT INTO ' + db_name + '.' + table_name + ' VALUES (' + table_format + ')'
        #print(sql_query)
        
        # push data
        cursor.execute(sql_query, tuple(row))
        connection.commit()

        if data_import_limit>0:
          break
      
      print(str(i) + ' records inserted into "' + table_name + '"')
except Error as e:
  print("Error while connecting to MySQL", e)

print('Data import completed.')