# Importing the required libraries
import requests
#import pandas as pd
from bs4 import BeautifulSoup



file1 = open('download_link.txt', 'r')
Lines = file1.readlines()



for line in Lines:
	# Downloading contents of the web page
	url = line
	data = requests.get(url).text

	# Creating BeautifulSoup object
	soup = BeautifulSoup(data, 'html.parser')


	data = []
	table = soup.find('table', attrs={'class':'downloadsTable'})
	table_body = table.find('tbody')

	rows = table_body.find_all('a')
	for row in rows:
		#cols = row.find_all('a')
		cols = row.get('href')
		#cols = 
		data.append(cols)
		#print(cols.get('href'))
		
	#print(data)
	print(data[0])
	# writing to file
    #file1 = open('myfile.txt', 'w')
	#file1.writelines(data[0])
	#file1.close()
	
