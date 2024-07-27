##########################################################
#   Written by PhilipW./Rauhm, usable under CCLicense-2024
#             just name me as Tech Support
##########################################################


##########################################################
# library import
##########################################################

import maya.cmds as cmds

##########################################################
# global parameters
##########################################################

__version__ = "0.2.0"
__build_date__ = "July 23, 2024"

##########################################################
# global util methods
##########################################################


##########################################################
# global parameter handling
##########################################################

def version():
    return __version__

def buildDate():
    return __build_date__

def copyRightText():
    return 'Written by Philip Wersonig - ' + version()


##########################################################
# UI related
##########################################################
"""
 Fills a UI Optional Menu with menu Items based on the given elements list
 elements list is expected to be an array of strings
"""
def fillOptionMenuWithElements(elements):
    for element in elements:
        cmds.menuItem( label=element )
