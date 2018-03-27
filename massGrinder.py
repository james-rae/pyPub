import arcpy
import httplib
import urllib
import csv

# ############################################
# Main Party

# Do many great things.
# Command line args:
# Operation flag    what thing we want the script to do. See vals below.
# Server username   secret server user name. only required for DEL_SERVICE and ON_DEMAND operations
# Server password   secret server password. only required for DEL_SERVICE and ON_DEMAND operations

# flags for operation
# DEL_TILE      - deletes tile info from a service. do prior to deleting service. prevents ghost errors.
# DEL_SERVICE   - deletes a service from arcgis server
# PUB_SERVICE   - publishes a service and converts it to tile
# ON_DEMAND     - enables on demand tiling


# ############################################

# eat command line params
opFlag = arcpy.GetParameterAsText(0)
user = arcpy.GetParameterAsText(1)
password = arcpy.GetParameterAsText(2)

# some globals that i'm too lazy to pass in as command line params

# location of connection file. should point to the target arcgis server
connFile = "C:\\Users\\jamesr\\AppData\\Roaming\\Esri\\Desktop10.4\\ArcCatalog\\arcgis on cipgis.canadaeast.cloudapp.azure.com (publisher)"

# csv file containing things to target for this command
targetFile = "C:\\Git\\pyPub\\data\\target.csv"

# url of the target arcgis server
rootUrl = "https://cipgis.canadaeast.cloudapp.azure.com"


# pre-loop prep
token = ''
if opFlag in ['DEL_SERVICE', 'ON_DEMAND']:
    # TODO execute get token function, set token var

# read our file of targets and get loopin
with open(targetFile,'rb') as csvfile:
    fileReader = csv.reader(csvfile, delimiter=',')
    for row in fileReader:
        folderName = row[0]
        serviceName = row[1]
        sdFileName = row[2]

        if opFlag = 'DEL_SERVICE':
            # TODO call delete service
        if opFlag = 'DEL_TILE':
            # TODO call delete tile
        if opFlag = 'PUB_SERVICE':
            # TODO call publish service
        if opFlag = 'ON_DEMAND':
            # TODO call delete service
