import arcpy
import httplib
import urllib
import csv
import json

# HELLO
# if looking to run this, go to bottom of file and check the global vars that are sitting there.
# some might need adjustin'
# also, be sure the service folders on the arcgis server are defined prior to script runnin'

# ############################################
#
#  ASSER JSON SUCCESS FUNCTION
#  Returns True in case of success,
#  False otherwise
"""Checks that the input JSON object is not an error object.
    Args:
        data: JSON object.
    Returns:
        True if successful, False otherwise.
"""
# ############################################

def assertJsonSuccess(data):

    if 'status' in data and data['status'] == "error":
        print "Error: JSON object returns an error. " + str(data)
        return False
    else:
        return True

# ############################################
#
#  GET SERVICE RESPONCE FUNCTION
"""Connects to the service to get its current JSON definition.

    Args:
        serverName: Domain of server to connect to.
        serverPort: Port of server to connect to.
        service: URL of service.
        params: URL parameters.
        headers: URL headers.

    Returns:
        The service's current JSON object.
"""
#
# ############################################

def getServiceResponse(serverName, serverPort, service, params, headers):

    #Connect to service
    httpConn = httplib.HTTPSConnection(serverName, serverPort, context=ssl._create_unverified_context())
    httpConn.request("POST", service, params, headers)

    #Read response
    response = httpConn.getresponse()
    if (response.status != 200):
        httpConn.close()
        print "Could not read service information."
        return
    else:
        data = response.read()
        jdata = json.loads(data)

        #Check that data returned is not an error object
        if not assertJsonSuccess(jdata):
            print "Error when reading service information. " + str(jdata)
        else:
            if "edit" in service:
                print "Service edited successfully."
            else:
                print
                print service + " responded successfully."

            httpConn.close()
            return jdata

# ############################################
#
#  GET TOKEN FUNCTION
"""Generate an access token for ArcGIS Admin API.

    Reference:
        http://resources.arcgis.com/en/help/arcgis-rest-api/index.html#//02r3000000m5000000

    Args:
        username: Username of user who wants to get a token.
        password: Password of user who wants to get a token.
        serverName: Domain of server to connect to.
        serverPort: Port of server to connect to.

    Returns:
        The generated token.
"""
# ############################################

def getToken(username, password, serverName, serverPort):

    # Token URL is typically http://server[:port]/arcgis/admin/generateToken
    tokenURL = "/arcgis/admin/generateToken"

    # todo figure out how long our average session is, adjust expiration
    params = urllib.urlencode({'username': username, 'password': password, 'client': 'requestip', 'f': 'json', 'expiration': 20 })

    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}

    # Connect to URL and post parameters
    token = getServiceResponse(serverName, serverPort, tokenURL, params, headers)
    return token['token']

# ############################################

"""Publish the service.

    Args:
        sdFolder: Absolute path of workspace folder.
        sd: SD file to publish.
        connPath: Path to connection file that is used to connect to a GIS Server.
        serviceName: Name of the service.
        serverFolder: Name of the folder to publish in.

"""

# ############################################

def publishSD(sdFolder, sd, connPath, serviceName, serverFolder):

    print "Publishing SD in: " + sdFolder

    sdPath = sdFolder + "/" + sd

    # Execute UploadServiceDefinition.  This uploads the service definition
    # and publishes the service.
    arcpy.UploadServiceDefinition_server(sdPath, connPath, serviceName, "", "EXISTING", serverFolder)
    print serviceName + " has been published"

# ############################################

"""Convert service to tile. Does everything we want except enable on-demand

    Args:
        connPath: Path to connection file that is used to connect to a GIS Server.
        serviceName: Name of the service.
        serverFolder: Name of the folder to publish in.

"""

# ############################################

def convertToTile(connPath, serviceName, serverFolder):

    serverPath = connPath + "\\" + serverFolder + "\\" + serviceName + ".MapServer"

    print "Targeting this service for tile: " + serverPath

    arcpy.CreateMapServerCache_server(serverPath, "C:\\arcgisserver\\directories\\arcgiscache", "NEW", "CUSTOM", "9", "96", "256 x 256", "", "-34655800 39310000", "145000000;85000000;50000000;30000000;17500000;10000000;6000000;3500000;2000000", "JPEG", "75", "COMPACT")
    print serviceName + " has been tiled"

# ############################################

"""Remove any files related to tiles. Need to delete them to avoid ghost properties when republishing

    Args:
        connPath: Path to connection file that is used to connect to a GIS Server.
        serviceName: Name of the service.
        serverFolder: Name of the folder to publish in.

"""

# ############################################

def removeTiles(connPath, serviceName, serverFolder):

    serverPath = connPath + "\\" + serverFolder + "\\" + serviceName + ".MapServer"

    print "Targeting this service for tile removal: " + serverPath

    arcpy.DeleteMapServerCache_server(serverPath, 2)
    print serviceName + " has had tiles removed"

# ############################################

"""Set map tile service to be on demand.

    Args:

        serverName: Domain of server to connect to.
        serverPort: Port of server to connect to.
        serviceName: Name of the service.
        serverFolder: Name of the folder the service resides in.
        token: ArcGIS server secure token to allow our edits.

"""

# ############################################

def onDemandTile(serverName, serverPort, serviceName, serverFolder, token):

    # This request only needs the token and the response formatting parameter
    params = urllib.urlencode({'token': token, 'f': 'json'})
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}

    folderPath = "/arcgis/admin/services/" + serverFolder

    serviceUrl = folderPath + "/" + serviceName + ".MapServer"

    # get the admin json object for the service
    serviceJson = getServiceResponse(serverName, serverPort, serviceUrl, params, headers)

    # appears the values are encoded as text. attempt bools/ints if errors happen.
    serviceJson["properties"]["cacheOnDemand"] = "true"
    # serviceObj["properties"]["maxScale"] = "2000000"
    # serviceObj["properties"]["minScale"] = "145000000"

    # Serialize back into JSON
    updatedServiceJson = json.dumps(serviceJson)

    # Call the edit operation on the service.  Pass in modified JSON.
    editServiceUrl = serviceUrl + "/edit"
    params = urllib.urlencode({'token': token, 'f': 'json', 'service': updatedServiceJson})
    getServiceResponse(serverName, serverPort, editServiceUrl, params, headers)


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

# path of folder containing the .sd files to publish
sdFolder = "C:\\Git\\pyPub\\data\\"

# url of the target arcgis server, and port (SSL port)
# needs to be dns because dumb. this will fail: "https://cipgis.canadaeast.cloudapp.azure.com"
rootUrl = "52.235.40.173"
port = 443

# TODO consider changing the flags.
#      we could pair the pub and delete things together
#      only thinking this because if we delete files then wait a bit for delete service, more
#      more files could get made if a person surfs to the site.  maybe only pair the delete
#      as im concerned the service might not be spun up in time for the convert to on demand tile,
#      and more if we decide to pre-gen the first few layers

# pre-loop prep
token = ''
if opFlag in ['DEL_SERVICE', 'ON_DEMAND']:
    token = getToken(user, password, rootUrl, port)

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
            removeTiles(connFile, serviceName, folderName)

        if opFlag = 'PUB_SERVICE':
            publishSD(sdFolder, sdFileName, connFile, serviceName, folderName)
            convertToTile(connFile, serviceName, folderName)

        if opFlag = 'ON_DEMAND':
            onDemandTile(rootUrl, port, serviceName, folderName, token)
