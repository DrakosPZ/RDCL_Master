##########################################################
#   Written by PhilipW./Rauhm, usable under CCLicense-2024
#             just name me as Tech Support
##########################################################


##########################################################
# library import
##########################################################

import maya.cmds as cmds;
import pymel.core as pmc;
import mtoa.aovs as aovs;
import json;

##########################################################
# global parameters
##########################################################

__version__ = "0.2.1"
__build_date__ = "August 25, 2024"

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
# Light Related Utils
##########################################################

mayaLights = ['ambientLight','directionalLight','pointLight', 'spotLight','areaLight','volumeLight']

arnoldLights = ['aiAreaLight','aiSkyDomeLight','aiPhotometricLight','aiLightPortal'];

allLights = mayaLights + arnoldLights;

'''
 checks if the given Light is a Maya Light
 
 lightStr => String name of the light source
 
 returns true if first found light with that name is a default Maya light, otherwise false
'''
def lightIsMayaLight(lightStr):
    return lightIsOfType(lightStr, mayaLights);

'''
 checks if the given Light is a Arnold Light
 
 lightStr => String name of the light source
 
 returns true if first found light with that name is a default Arnold light, otherwise false
'''
def lightIsArnoldLight(lightStr):
    return lightIsOfType(lightStr, arnoldLights);

'''
 checks if the given Light is of th egiven Type Array
 
 lightStr => String name of the light source
 lightTypes => [] a Strring array containg all Types to be checked against
 
 returns true if first found light with that name is of one of the lightTypes, otherwise false
'''
def lightIsOfType(lightStr, lightTypes):
    node = cmds.ls ('*'+lightStr, long=True, showType = True);
    nodeType = node[1];
    if nodeType in lightTypes:
        return True;
    return False;

##########################################################
# Rendering and AOV Related Utils
##########################################################


'''
 get All AOVs
 arrayNameType: 
     0 => LongName/NodeName Array
     1 => Shortname/ readable Name Array
     2 => Short and Long Name Tulip Array
 Depending on Shortname flag raised or not, the returned Array containes the AOVs ShortName or LongName/NodeName
'''
def getAOVs(arrayNameType = 0):
    aovNames = [];
    aovPairs = aovs.AOVInterface().getAOVNodes(names = True);
    if arrayNameType == 0: 
        aovNames = getAOVLongName(aovPairs);
    if arrayNameType == 1: 
        aovNames = getAOVShortName(aovPairs);
    if arrayNameType == 2: 
        aovNames = aovPairs;
    return aovNames;
    
'''
 A small helper function that reduces the list of AOVs down to only contain the AOVs shortName
'''
def getAOVShortName(AOVs):
    aovNames = [];
    for aovElement in AOVs:
        aovNames.append(aovElement[0]);
    return aovNames;

'''
 A small helper function that reduces the list of AOVs down to only contain the AOVs longName
'''
def getAOVLongName(AOVs):
    aovNames = [];
    for aovElement in AOVs:
        aovNames.append(aovElement[1]);
    return aovNames;

'''
 get All AOVs as String
 plainText: Boolean
 checkActivity: Boolean
 checkLightAOV: Boolean
 Depending on the plainText Flag the string is returned as "<AOV> <AOV> <...>" or adds the noice AOV script tag to it "-l <AOV> -l <AOV> <...>"
 Depending on the checkActivity Flag only AOVs are returned that are also turned on in the current renderView
 Depending on the checkLightAOV Flag only AOVs are returned that are also LightGroupAOVs
'''
def getAOVsAsString(plainText, checkActivity, checkLightAOV = True):
    allAOVsString = '';
    AOVs = getAOVs(2);
    AOVShortNames = getAOVShortName(AOVs);
    
    preFlag = '';
    
    if plainText == False: 
        preFlag = "-l ";
    
    for aovString in AOVShortNames:
        allAOVsString += preFlag + aovString + ' ';
    
    allAOVsString = allAOVsString[:-1];
    if checkActivity: 
        #TODO
        print('getAOVsAsString with checkActivity has still to be implemented');
    if checkLightAOV: 
        #TODO
        print('getAOVsAsString with checkLightAOV has still to be implemented');
    return allAOVsString;

"""a counter used to properly keep track how many and which AOV connections have been added to the rendering node in maya"""
aovPositionCounter = 1;

""" 
    Add AOVs with VarianceFilterAdded as well as if the toAdd flag is raised, adds the filter necessary for the noice denoiser
    If the script finds its to add a crypto AOV, it calls instead the specific addCryptoAOV() function,
    
    name: string => the name of the AOV
    type: string => the type of data aggregated i.e. rgb, rgba, float, etc.
    filterType: string => the type of filter used i.e. closest, gaussian, etc.
    toAdd: boolean => if the denoising filter should be added or not
"""
def addAOVWithFilter(name, type, filterType, toAdd):
    global aovPositionCounter;
    if name == 'crypto_asset' or name == 'crypto_material' or name == 'crypto_object':
        addCryptoAOV(name);
    else: 
        newAOV = aovs.AOVInterface().addAOV(name,aovType=type);
        if toAdd:
            aifilter = pmc.createNode('aiAOVFilter', n='aiAOVFilter');
            aifilter.setAttr('aiTranslator', 'variance');
            cmds.connectAttr('defaultArnoldDriver.message', aovs.AOVInterface().getAOVNode(name)+'.outputs['+str(aovPositionCounter)+'].driver');
            cmds.connectAttr(aifilter+'.message', aovs.AOVInterface().getAOVNode(name)+'.outputs['+str(aovPositionCounter)+'].filter');
    aovPositionCounter+=1;
    
""" 
    Adds cryptomatte AOV to render AOVs.
    If the cryptomatteShader hasn't yet been instantiated, it is automatically created and used. otherwise it takes the first shader containing the name CryptoMatte
    
    name: string => the name of the AOV but should be one of the three cryptomatte AOVs
"""
def addCryptoAOV(name):
    cryptoAOV = aovs.AOVInterface().addAOV(name);
    nodes = cmds.ls()
    cryptoMatteShaders = [node for node in nodes if 'cryptomatte' in node]
    if len(cryptoMatteShaders) > 0:
        cryptoMatteShader = cryptoMatteShaders[0]
    else:
        cryptoMatteShader = pmc.createNode('cryptomatte')
    cmds.connectAttr(cryptoMatteShader + '.outColor', cryptoAOV.node + '.defaultValue');

""" 
    returns a list of given types of lights that are currently in the executed scene
    
    lights: Array[strings] => an array of strings, containign all types of ligths to be returned
        by default set to only return arnold lights
"""
def getLights(lights = ['aiAreaLight','aiSkyDomeLight','aiPhotometricLight','aiLightPortal']):
    return pmc.ls(type = lights)

""" 
    returns a list of lightGroups set on the given list of lights
    Also corrects for duplicates.
    
    lights: Array[Maya Light objects] => the given list of light elements of which the light groups should be extracted
        by detault set to use getLights()
"""
def getLightGroupsFromLights(lights = []):
    if len(lights) == 0 : 
        lights = getLights();
    
    groups = [];
    filteredGroups = [];
    for light in lights:
        groups.append(light.aiAov.get())
    for i in range(0, len(groups)):    
        foundDuplicate = 0;
        for j in range(i+1, len(groups)):    
            if(groups[i] == groups[j]):    
                foundDuplicate = 1;
                break;
        if(foundDuplicate == 0):
            filteredGroups.append(groups[i]);
    return filteredGroups;

"""
    resolves instructions and creates AOVs accordingly ,
    also corrects for data and light pass settings.
    and also only creates the AOV if Create AOV Flag is raised in the tulip
    
    instruction: Array[(AOVPass, AOVName, Create AOV, Denoise AOV)] => the set of instructions
"""  
def createAOVs(instructions):
    for instruction in instructions:
        #instruction dissection
        AOVPass = instruction[0]
        if instruction[1] == None:
            AOVName = ''
        else:
            AOVName = '_'+instruction[1]
        CreateAOV = instruction[2]
        DenoiseAOV = instruction[3]
        #parameter initialisation
        type = 'rgb'
        filterType = 'gaussian'
        beDenoised = DenoiseAOV
        #special case Parameters initialization
        aov_params = {
            'RGBA': ('rgba', 'gaussian', DenoiseAOV),
            'ID': ('uint', 'gaussian', False),
            'N': ('vector', 'closest', False),
            'P': ('vector', 'closest', False),
            'Pref': ('rgb', 'closest', False),
            'Z': ('float', 'closest', False),
            'crypto_object': ('rgb', 'gaussian', False),
            'crypto_asset': ('rgb', 'gaussian', False),
            'crypto_material': ('rgb', 'gaussian', False),
            'highlight': ('rgb', 'gaussian', False),
            'motionvector': ('rgb', 'gaussian', False),
            'opacity': ('rgb', 'gaussian', False),
            'rim_light': ('rgb', 'gaussian', False),
            'shadow': ('rgb', 'gaussian', False),
            'shadow_diff': ('rgb', 'gaussian', False),
            'shadow_mask': ('rgb', 'gaussian', False),
            'cputime': ('float', 'gaussian', False),
            'shadow_matte': ('rgba', 'gaussian', DenoiseAOV),
            'volume_Z': ('float', 'closest', False),
            'volume_opacity': ('rgb', 'gaussian', False)
        }
        
        # Safeguarding against datapass denoising and right parameter settings
        if AOVName in aov_params:
            type, filterType, beDenoised = aov_params[AOVName]

        if CreateAOV:
            addAOVWithFilter(AOVPass + AOVName, type, filterType, beDenoised)



##########################################################
# UI related
##########################################################
"""
 Fills a UI Optional Menu with menu Items based on the given elements list
 elements list is expected to be an array of strings
"""
def fillOptionMenuWithElements(elements, parent = ''):
    if len(parent) > 0:
        for element in elements:
            cmds.menuItem( label=element , parent = parent)
    else:
        for element in elements:
            cmds.menuItem( label=element )



##########################################################
# Data management related
##########################################################
"""
 Handles turning objects into JSON format
 so far it assumes the object is an array of string
"""
def jsonfy(object):
    return json.dumps(object)
"""
 Handles turning JSON objects into python objects format
 so far it assumes the object is an array of string
"""
def deJsonfy(object):
    return json.loads(object)