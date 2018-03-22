import arcpy

# ############################################
#
#  printLog(logs, msg)
#
# Appends message to the log collection and prints it
#
# ############################################


def printLog(logs, msg):
    print msg
    logs.append("")  #have to add an empty line, otherwise no line break in email content
    logs.append(msg)

# ############################################

"""Publish the service.

    Args:
        sdFolder: Absolute path of workspace folder.
        sd: SD file to publish.
        connPath: Path to connection file that is used to connect to a GIS Server.
        serviceName: Name of the service.
        serverFolder: Name of the folder to publish in.
        logs: log list holds all log items for current publication

"""

# ############################################

def publishSD(sdFolder, sd, connPath, serviceName, serverFolder, logs):

    printLog(logs,"Publishing SD in: " + sdFolder)

    sdPath = sdFolder + "/" + sd

    # Execute UploadServiceDefinition.  This uploads the service definition
    # and publishes the service.
    arcpy.UploadServiceDefinition_server(sdPath, connPath, serviceName, "", "EXISTING", serverFolder)
    printLog(logs, serviceName + " has been published")

# ############################################

"""Convert service to tile. Does everything we want except enable on-demand

    Args:
        connPath: Path to connection file that is used to connect to a GIS Server.
        serviceName: Name of the service.
        serverFolder: Name of the folder to publish in.
        logs: log list holds all log items for current publication

"""

# ############################################

def convertToTile(connPath, serviceName, serverFolder, logs):

    serverPath = connPath + "\\" + serverFolder + "\\" + serviceName + ".MapServer"

    printLog(logs,"Targeting this service for tile: " + serverPath)

    arcpy.CreateMapServerCache_server(serverPath, "C:\\arcgisserver\\directories\\arcgiscache", "NEW", "CUSTOM", "9", "96", "256 x 256", "", "-34655800 39310000", "145000000;85000000;50000000;30000000;17500000;10000000;6000000;3500000;2000000", "JPEG", "75", "COMPACT")
    printLog(logs, serviceName + " has been tiled")

# ############################################
# Main Party

# ############################################

sdfolder = arcpy.GetParameterAsText(0)
sd = arcpy.GetParameterAsText(1)
logs = []

# update this to be real parameter
serverFolder = "PythonParty"

# Connection files lurk at
# C:\Users\<userid>\AppData\Roaming\ESRI\Desktop10.4\ArcCatalog\
# TODO change to param?
conn = "C:\\Users\\jamesr\\AppData\\Roaming\\Esri\\Desktop10.4\\ArcCatalog\\arcgis on cipgis.canadaeast.cloudapp.azure.com (publisher)"

printLog(logs, "Start the party")
printLog(logs, sd)

# step 1. check if service exists, delete it.

# step 2. publish service
# Todo will want service target name as proper var
publishSD(sdfolder, sd, conn, "Enhance2", serverFolder, logs)

# step 3. turn service into tiles
# Todo will want service target name as proper var
convertToTile(conn, "Enhance2", serverFolder, logs)