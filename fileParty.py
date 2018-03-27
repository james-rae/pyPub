import csv

with open('C:\\Git\\pyPub\\data\\test.csv','rb') as csvfile:
    fileReader = csv.reader(csvfile, delimiter=',')
    for row in fileReader:
        print row[0]
        print row[1]