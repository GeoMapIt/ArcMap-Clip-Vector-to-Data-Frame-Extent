"""
Clips user specified vector data to user specified data frame within mxd document.
Projects result if user specifies coordinate system.
Run as tool in Arcmap.
Made by Nathan R
"""

import arcpy
from arcpy import env
from arcpy import mapping

#Script Parameters
data_to_clip = arcpy.GetParameterAsText(0)
data_frame = arcpy.GetParameterAsText(1) 
export_location = arcpy.GetParameterAsText(2)
coord_sys = arcpy.GetParameterAsText(3)
add_to_toc = arcpy.GetParameterAsText(4)

#Creates DF_Extent feature class in default arcgis workspace
mxd = mapping.MapDocument("CURRENT")
df = mapping.ListDataFrames(mxd, "*")[int(data_frame)-1]
coord_sys = df.spatialReference
frameExtent = df.extent

array = arcpy.Array()
array.add(arcpy.Point(frameExtent.XMin, frameExtent.YMin))
array.add(arcpy.Point(frameExtent.XMin, frameExtent.YMax))
array.add(arcpy.Point(frameExtent.XMax, frameExtent.YMax))
array.add(arcpy.Point(frameExtent.XMax, frameExtent.YMin))
array.add(arcpy.Point(frameExtent.XMin, frameExtent.YMin))
polygon = arcpy.Polygon(array)

#Creates temporary feature class in default arcgis workspace to be used as clip boundary
arcpy.CopyFeatures_management(polygon, "DF_Extent_TODELETE")

#Defines temporary feature class to data frame coordinate system
arcpy.DefineProjection_management("DF_Extent_TODELETE", coord_sys)

#Clips vector data to temporary feature class and projects if needed
if coord_sys != "": #checks if cs is set
    arcpy.Clip_analysis(data_to_clip, "DF_Extent_TODELETE", "Temp_Clip_TODELETE")
    arcpy.Project_management("Temp_Clip_TODELETE", export_location, coord_sys)
    arcpy.Delete_management("DF_Extent_TODELETE")
    arcpy.Delete_management("Temp_Clip_TODELETE")
else:
    arcpy.Clip_analysis(data_to_clip, "DF_Extent_TODELETE", export_location)
    arcpy.Delete_management("DF_Extent_TODELETE")

#Adds result into TOC
if add_to_toc == "true":
    try:
        addlayer = arcpy.mapping.Layer(export_location)
    except:
        addlayer = arcpy.mapping.Layer(export_location + ".shp")
    arcpy.mapping.AddLayer(df, addlayer, "TOP")
