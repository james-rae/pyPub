import arcpy

# lines marked [switcher] are places to swap values when running on desktop vs server

# some globals that i'm too lazy to pass in as command line params

# location of connection file. should point to the target arcgis server
# [switcher]
# connFile = "X:\\maps\\misc\\pyPub\\arcgis_local_conn"
connFile = "C:\\Users\\jamesr\\AppData\\Roaming\\Esri\\Desktop10.4\\ArcCatalog\\arcgis on cipgis.canadaeast.cloudapp.azure.com (publisher)"


from arcpy import env
import os, sys, time, datetime, traceback, string

# List of input variables for map service properties

serviceName = "\\CMIP5_SnowDepth\\SnowDepth_2041_20yr_DJF_rcp85.MapServer"
inputService = connFile + serviceName
tilingSchemeType = "PREDEFINED"

# Set environment settings
# [switcher]
# env.workspace = "E:\\arcgisserver\\directories\\cache_workspace\\"
env.workspace = "C:\\temp\\workspace\\"

scales = [145000000,85000000,50000000,30000000,17500000,10000000,6000000,3500000,2000000]
numOfCachingServiceInstances = 2
updateMode = "RECREATE_ALL_TILES"
# [switcher]
# areaOfInterest = "X:\\maps\\misc\\tile_data\\tile_clip_lambert.shp"
areaOfInterest = "C:\\Data\\CCCP\\tileSupport\\tile_clip_lambert.shp"
waitForJobCompletion = "WAIT"
updateExtents = ""


currentTime = datetime.datetime.now()
arg1 = currentTime.strftime("%H-%M")
arg2 = currentTime.strftime("%Y-%m-%d %H:%M")
# [switcher]
# file = "X:\\maps\\misc\\pyPub\\report_%s.txt" % arg1
file = "C:\\git\\pyPub\\report_%s.txt" % arg1

# print results of the script to a report
report = open(file,'w')

# use "scales[0]","scales[-1]","scales[0:3]"

try:
    starttime = time.clock()
    result = arcpy.ManageMapServerCacheTiles_server(inputService, scales,
                                                    updateMode,
                                                    numOfCachingServiceInstances,
                                                    areaOfInterest, updateExtents,
                                                    waitForJobCompletion)                                           
    finishtime = time.clock()
    elapsedtime = finishtime - starttime

    #print messages to a file
    while result.status < 4:
        time.sleep(0.2)
    resultValue = result.getMessages()
    report.write ("completed " + str(resultValue))
    
    print "Created cache tiles for scale =" + str(scales[-1]) + "for " +\
    serviceName + "at " + cacheDir + " using specified feature class " +\
    areaOfInterest + " in " + str(elapsedtime) + " sec on " + arg2

except Exception, e:
    # If an error occurred, print line number and error message
    tb = sys.exc_info()[2]
    report.write("Failed at \n" "Line %i" % tb.tb_lineno)
    report.write(e.message)

report.close()     
print "Rereated Map server Cache Tiles"
print "for scale = " + str(scaleValues[-1]) + " using area of Interest"