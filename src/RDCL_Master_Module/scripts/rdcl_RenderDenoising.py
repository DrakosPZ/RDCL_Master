##########################################################
#   Written by PhilipW./Rauhm, usable under CCLicense-2024
#             just name me as Tech Support
##########################################################


##########################################################
# library import
##########################################################

import maya.cmds as cmds
import mtoa.aovs as aovs;
import pymel.core as pmc;
from functools import partial;
import maya.app.renderSetup.views.overrideUtils as utils;
import maya.app.renderSetup.model.renderSetup as renderSetup;
import mtoa.ui.arnoldmenu;
import pyperclip
import rdcl_utils as pwUtils;

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
    
    name: string => the name of the AOV
    type: string => the type of data aggregated i.e. rgb, rgba, float, etc.
    filterType: string => the type of filter used i.e. closest, gaussian, etc.
    toAdd: boolean => if the denoising filter should be added or not
"""
def addAOVWithFilter(name, type, filterType, toAdd):
    global aovPositionCounter;
    newAOV = aovs.AOVInterface().addAOV(name,aovType=type);
    if toAdd:
        aifilter = pmc.createNode('aiAOVFilter', n='aiAOVFilter');
        aifilter.setAttr('aiTranslator', 'variance');
        cmds.connectAttr('defaultArnoldDriver.message', aovs.AOVInterface().getAOVNode(name)+'.outputs['+str(aovPositionCounter)+'].driver');
        cmds.connectAttr(aifilter+'.message', aovs.AOVInterface().getAOVNode(name)+'.outputs['+str(aovPositionCounter)+'].filter');
    aovPositionCounter+=1;

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
def getLightGroupsFromLights(lights = getLights()):
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
    
    instruction: Array[(AOVPass, AOVName, Create AOV, Denoise AOV]) => the set of instructions
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
# Deactivate all AOVS of currently active Layer
##########################################################

""" Creates all overrides for all AOVs and turns them off """
class PW_DeactivateAllAOVs(object):
    #constructor
    def __init__(self):
        self.createAOVOverrides(getAOVs(), ["aiAOV_RGBA"]);
        self.switchOffAllAOVsForActive();

    '''
     create Overrides and set To false
    '''
    def createAOVOverrides(self, aovs, ignoredAOVs):
        ''' remove to be ignored aovs from aov list '''
        for aov in ignoredAOVs:
            if aov in aovs:
                aovs.remove(aov)
        for aov in aovs:
            utils.createAbsoluteOverride(aov, 'enabled');
    '''    
     switch all AOVs overrides in the currently active RenderLayer to be turned off
    '''
    def switchOffAllAOVsForActive(self):
        rs = renderSetup.instance() 
        layer = rs.getVisibleRenderLayer()
        collections = layer.getCollections()
        for collection in collections:
            if 'AOVCollection' in collection.name():
                aovCollections = collection.getCollections()
                for aovCollection in aovCollections:
                    overrides = aovCollection.getOverrides()
                    for override in overrides:
                        cmds.setAttr(override.name()+'.attrValue', 0);

##########################################################
# Remove All set AOVs from Scene
##########################################################

""" My Implementation of the Delete All AOV Button """
class PW_RemoveAllAOVs(object):
    #constructor
    def __init__(self):
        self.removeAOVs([]);

    '''
     removes a single AOV
    '''
    def removeAOV(self, aov):
        aovs.AOVInterface().removeAOV(aov);
    
    '''
     removes all AOVs
    '''
    def removeAOVs(self, ignoredAOVs):
        allAOVs = getAOVs(1)
        for aov in ignoredAOVs:
            if aov in allAOVs:
                allAOVs.remove(aov)
        aovs.AOVInterface().removeAOVs(allAOVs);

##########################################################
# Copy AOVs for further Denoising
##########################################################

""" A method Copying all AVOs names prepped for further use in either a denoising script or the Arnold Noice Denosier """
class PW_CopyAOVs(object):
    #constructor
    def __init__(self):
        self.copyAOVs();

    '''
     removes a single AOV
    '''
    def copyAOVs(self, plainText = False, checkActivity = False):
        # for now so I don't forget about it
        checkActivity = True;
        allAOVsString = getAOVsAsString(plainText, checkActivity, True);
        pyperclip.copy(allAOVsString);
        print('copied AOVs to Clipboard');
        print(allAOVsString);

##########################################################
# Open AOV Master Window for a mroe artist friendly AOV and Denoising Approach
##########################################################

""" 
    A function to better manage AOVs and Denoising for repetitve tasks or beginners.
    Assumes that there are no prior set AOVs 
    aswell that the already set AOVs are instantiated with the default closest gausian Filter.
    !!! This does not yet properly work with already instantiated AOVs
    !!! And not yet checks for doubles
    !!! The definition of Data/Utility Passes also hasn't been clearly communicated to me so there may be some fringe Passes that may be misshandled
"""
class PW_AOVMaster(object):
    #constructor
    def __init__(self):
        #Functionality Parameters
        self.presets = ['', 'full_Assembly','Only_RGBA','RGBA_Diffuse_Specular','All_But_Emission_Transmission', 'full_DetailAssembly']
        self.AOVPasses = ['RGBA', 'RGBA_indirect', 'RGBA_direct', 'diffuse', 'diffuse_indirect', 'diffuse_direct', 'coat', 'coat_albedo', 'coat_indirect', 'coat_direct', 'emission', 'emission_indirect', 'emission_direct', 'sheen', 'sheen_albedo', 'sheen_indirect', 'sheen_direct', 'specular', 'specular_albedo', 'specular_indirect', 'specular_direct', 'sss', 'sss_albedo', 'sss_indirect', 'sss_direct', 'transmission', 'transmission_albedo', 'transmission_indirect', 'transmission_direct', 'albedo', 'background', 'direct', 'indirect', 'shadow', 'shadow_diff', 'shadow_mask', 'shadow_matte', 'volume', 'volume_albedo', 'volume_direct', 'volume_indirect']
        self.UtilityPasses = ['ID','N','P','Z','crypto_object', 'crypto_asset', 'crypto_material', 'motionvector', 'highlight', 'opacity', 'raycount', 'rim_light', 'volume_Z', 'volume_opacity']
        
        #UI Global Parameters
        self.window = 'PW_PopulateAOVs_Window'
        self.title = 'AOV Master'
        self.size = (900, 800)
        self.rowHorizontalGap = 5
        self.columnVerticalGapBig = 20
        self.columnVerticalGapMedium = 10
        self.columnVerticalGapSmall = 5
        self.ListOfAOVS = []
        self.ListOfLightGroups = getLightGroupsFromLights()
        self.AOVIndexCounter = 0
        self.UtilC = ''
        self.BaseC = ''
        self.LightGroupsCs = []
        self.PresetUI = ''
        
        self.initMainUI();
    
    """Initializes the Main UI and displays it"""
    def initMainUI(self):
        #close window if already open
        if cmds.window(self.window, exists = True):
            cmds.deleteUI(self.window, window = True)

        #create new Window
        self.window = cmds.window(self.window, title=self.title, width=self.size[0], height=self.size[1])

        #UI Segment
        self.mainCL  = cmds.columnLayout(adjustableColumn = True)
        
        tmpRowWidth = [self.size[0]*0.78, self.size[0]*0.05]
        cmds.rowLayout(numberOfColumns = 3, width = self.size[0])
        cmds.separator(width=tmpRowWidth[0], style='none')
        cmds.text(pwUtils.copyRightText(), align='right')
        cmds.separator(width=tmpRowWidth[1], style='none')
        cmds.setParent(self.mainCL)
        
        cmds.separator(height=self.columnVerticalGapBig)
        cmds.text('Assumes that there are no prior set AOVs!!!')
        cmds.text('Aswell that the already set AOVs are instantiated with the default closest gausian Filter!!!')
        cmds.text('Aswell in the current version if you want to setup denoising for an AOV you also have to create with this plugin first!!!')
        cmds.text('So best, delete all AOVs before executing this window!!!')
        cmds.separator(height=self.columnVerticalGapBig)
        cmds.text('Presets')
        cmds.separator(height=self.columnVerticalGapMedium, style='none')
        tmpRowWidth = [self.size[0]*0.1, self.size[0]*0.4, self.size[0]*0.1]
        cmds.rowLayout(numberOfColumns = 11, width = self.size[0])
        cmds.separator(width=tmpRowWidth[0], style='none')
        self.PresetUI = cmds.optionMenu(label = 'Preset Configuration')
        pwUtils.fillOptionMenuWithElements(self.presets)
        cmds.separator(width=self.rowHorizontalGap, style='none')
        self.actionBTN = cmds.button(label='Apply', width=tmpRowWidth[2], command=self.presetApply_BTNAction)
        cmds.separator(width=self.rowHorizontalGap, style='none')
        self.actionBTN = cmds.button(label='Recreate', width=tmpRowWidth[2], command=self.presetRecreate_BTNAction)
        cmds.separator(width=self.rowHorizontalGap, style='none')
        self.actionBTN = cmds.button(label='Save', width=tmpRowWidth[2], command=self.presetSave_BTNAction)
        cmds.separator(width=self.rowHorizontalGap, style='none')
        self.actionBTN = cmds.button(label='Load', width=tmpRowWidth[2], command=self.presetLoad_BTNAction)
        cmds.separator(width=tmpRowWidth[0], style='none')
        cmds.setParent(self.mainCL)
        cmds.separator(height=self.columnVerticalGapBig)
        cmds.text('Utility AOVs')
        self.createUtilCheckBoxes()
        cmds.separator(height=self.columnVerticalGapMedium, style='none')
        cmds.text('Base AOVs')
        self.createBaseCheckBoxes()
        cmds.separator(height=self.columnVerticalGapMedium, style='none')
        cmds.text('Found Light Groups')
        self.createAOVCheckBoxes()
        cmds.separator(height=self.columnVerticalGapBig, style='none')
        tmpRowWidth = [self.size[0]*0.1, self.size[0]*0.8]
        cmds.rowLayout(numberOfColumns = 3, width = self.size[0])
        cmds.separator(width=tmpRowWidth[0], style='none')
        self.actionBTN = cmds.button(label='Create AOVs', width=tmpRowWidth[1], command=self.createAOVs_BTNAction)
        cmds.separator(width=tmpRowWidth[0], style='none')
        cmds.setParent(self.mainCL)
        cmds.separator(height=self.columnVerticalGapBig, style='none')

        #display
        cmds.showWindow() 
    
    
    #--- create UI Functions from here
    def createUtilCheckBoxes(self):
        cmds.scrollLayout(width = self.size[0], height = self.size[1]*0.2)
        self.UtilC  = cmds.columnLayout(adjustableColumn = True)
        
        instructions = self.createUIInstructions('BASEData')
        self.executeUiInstructions(instructions)
        
        cmds.setParent(self.mainCL) 
        tmpRowWidth = [self.size[0]*0.1, self.size[0]*0.8]
        cmds.rowLayout(numberOfColumns = 3, width = self.size[0])
        cmds.separator(width=tmpRowWidth[0], style='none')
        cmds.button(label='Add Pass', width=tmpRowWidth[1], command = partial(self.addPass_BTNAction, self.UtilC, self.UtilityPasses, -1, [], -1, False, False, 'Util'))
        cmds.separator(width=tmpRowWidth[0], style='none')
        cmds.setParent(self.mainCL)
 
    def createBaseCheckBoxes(self):
        cmds.scrollLayout(width = self.size[0], height = self.size[1]*0.2)
        self.BaseC  = cmds.columnLayout(adjustableColumn = True)
        
        instructions = self.createUIInstructions('BASEPass')
        self.executeUiInstructions(instructions)
            
        cmds.setParent(self.mainCL)
        tmpRowWidth = [self.size[0]*0.1, self.size[0]*0.8]
        cmds.rowLayout(numberOfColumns = 3, width = self.size[0])
        cmds.separator(width=tmpRowWidth[0], style='none')
        cmds.button(label='Add Pass', width=tmpRowWidth[1], command = partial(self.addPass_BTNAction, self.BaseC, self.AOVPasses, -1, [], -1, False, False, 'Base'))
        cmds.separator(width=tmpRowWidth[0], style='none')
        cmds.setParent(self.mainCL)

    def createAOVCheckBoxes(self):
        self.createAOVLightGroupRow(self.ListOfLightGroups)
        
    def createAOVLightGroupRow(self, groupList):
        tempC = cmds.scrollLayout(width = self.size[0], height = self.size[1]*0.4)
        for index in range(len(groupList)):
            lightGroup = groupList[index]
            parentUI  = cmds.columnLayout(adjustableColumn = True)
            self.LightGroupsCs.append((lightGroup, parentUI))
            tmpRowWidth = [self.size[0]*0.3, self.size[0]*0.3, self.size[0]*0.1, self.size[0]*0.15]
            cmds.rowLayout(numberOfColumns = 7, width = self.size[0])
            cmds.separator(width = self.rowHorizontalGap, style = 'none')
            AOVPass = cmds.optionMenu(label = 'AOV Pass', width = tmpRowWidth[1])
            pwUtils.fillOptionMenuWithElements([''])
            cmds.optionMenu(AOVPass, edit = True, select = 1, enable = False)
            cmds.separator(width = self.rowHorizontalGap, style = 'none')
            lightGroup = cmds.optionMenu(label = 'Light Group', width = tmpRowWidth[0])
            pwUtils.fillOptionMenuWithElements(groupList)
            cmds.optionMenu(lightGroup, edit = True, select = index + 1, enable = False)
            cmds.separator(width = self.rowHorizontalGap, style = 'none')
            cmds.button(label='Add Pass', command = partial(self.addPass_BTNAction, parentUI, self.AOVPasses, -1, groupList, index, False, False, 'LightGroup'))
            cmds.separator(width = self.rowHorizontalGap, style = 'none')
            cmds.setParent(tempC)
        cmds.setParent(self.mainCL)
        
    #--- UI Interaction functions from here on
    def createAOVs_BTNAction(self, *args):
        AOVConstructionObject = self.unpackAOVTulipforList(self.ListOfAOVS)
        createAOVs(AOVConstructionObject)
        
    def addPass_BTNAction(self, parentUI, AOVGroup, AOVIndex, LightGroup, LGIndex, createAOV, denoise, type, *args):
        cmds.setParent(parentUI)            
        tmpRowWidth = [self.size[0]*0.3, self.size[0]*0.3, self.size[0]*0.1, self.size[0]*0.15, self.size[0]*0.1]
        passRow = cmds.rowLayout(numberOfColumns = 11, width = self.size[0])
        cmds.separator(width = self.rowHorizontalGap, style = 'none')
        AOVPass = cmds.optionMenu(label='AOV Pass')
        pwUtils.fillOptionMenuWithElements(AOVGroup)
        if AOVIndex > -1:
            cmds.optionMenu(AOVPass, edit = True, select = AOVIndex + 1)
        else: 
            cmds.optionMenu(AOVPass, edit = True, select = 1)
        cmds.separator(width = self.rowHorizontalGap, style = 'none')
        lightGroup = cmds.optionMenu(label = 'Light Group', width = tmpRowWidth[0])
        pwUtils.fillOptionMenuWithElements(LightGroup)
        if LGIndex > -1:
            cmds.optionMenu(lightGroup, edit = True, select = LGIndex + 1, enable = False)
        cmds.separator(width = self.rowHorizontalGap, style = 'none')
        create = cmds.checkBox(label = 'create AOV', width = tmpRowWidth[2], value = createAOV)
        cmds.separator(width = self.rowHorizontalGap, style = 'none')
        denoising = cmds.checkBox(label = 'setup Denoising', width = tmpRowWidth[3], value = denoise)
        cmds.separator(width = self.rowHorizontalGap, style = 'none')
        cmds.button(label='Remove', width = tmpRowWidth[4], command = partial(self.removePass_BTNAction, self.AOVIndexCounter))
        cmds.separator(width = self.rowHorizontalGap, style = 'none')
        cmds.setParent('..')
        
        self.addPassToDataStructure(lightGroup, AOVPass, create, denoising, passRow, type)
        
    def removePass_BTNAction(self, index, *args):
        self.removePassFromDataStructure(index)

    def changedOptionElement_OPTNChange(self, element):
        print(element)
        
    def presetApply_BTNAction(self, *args):
        presetSelected = cmds.optionMenu(self.PresetUI, query = True, value=True)
        if presetSelected != '':
            #Construct UI Instruction based on Preset
            instructions = self.createUIInstructions(presetSelected)
            #Apply Instructions
            self.applyUiInstructions(instructions)
                
       
    def presetRecreate_BTNAction(self, *args):
        presetSelected = cmds.optionMenu(self.PresetUI, query = True, value=True)
        if presetSelected != '':
            #Wipe list
            while len(self.ListOfAOVS) > 0:
                element = self.ListOfAOVS[0]
                self.removePassFromDataStructure(element[0])
            #Construct UI Instruction based on Preset
            instructions = self.createUIInstructions(presetSelected)
            #Execute Instructions
            self.executeUiInstructions(instructions)
        
    def presetSave_BTNAction(self, *args):
        print('Preset Save clicked')
        presetSelected = cmds.optionMenu(self.PresetUI, query = True, value=True)
        
    def presetLoad_BTNAction(self, *args):
        print('Preset Load clicked')
        presetSelected = cmds.optionMenu(self.PresetUI, query = True, value=True)
    
    #--- helper functions 
    """ unpacks Tulip and window element into => (AOVPass, AOVName, Create AOV, Denoise AOV) """
    def unpackAOVTulipforList(self, list):
        unpackedList = []
        for strIndex, aovNameUI, aovPassUI, createUI, denoiseUI, element, type in list:
            aovName = cmds.optionMenu(aovNameUI, query = True, value=True)
            aovPass = cmds.optionMenu(aovPassUI, query = True, value=True)
            create = cmds.checkBox(createUI, query = True, value=True)
            denoise = cmds.checkBox(denoiseUI, query = True, value=True)
            unpackedList.append((aovPass, aovName, create, denoise))
        return unpackedList
    
    def getIndexFromElementInList(self, element, list):
        for index in range(len(list)):
            listElement = list[index]
            if listElement == element:
                return index         
    
    """
      This function takes a category, and depending on the category it generates a set of UI instructions for further use
      these can be 
          BASEData => for the initial Data Pass settings
          BASEPass => for the initial Base Light Pass settings
          any other preset name => for related preset configuration
    """
    def createUIInstructions(self, category):
        instructions = []
        match category:
            case 'BASEData':
                instructions.append(('ID', 'None', True, False, 'Util'))
                instructions.append(('N', 'None', True, False, 'Util'))
                instructions.append(('P', 'None', True, False, 'Util'))
                instructions.append(('Z', 'None', True, False, 'Util'))
            case 'BASEPass':
                instructions.append(('RGBA', 'None', True, False, 'Base'))
                instructions.append(('albedo', 'None', True, False, 'Base'))
                instructions.append(('background', 'None', True, False, 'Base'))
            case 'full_DetailAssembly':
                instructions.append(('crypto_object', 'None', True, False, 'Util'))
                instructions.append(('N', 'None', True, False, 'Util'))
                instructions.append(('P', 'None', True, False, 'Util'))
                instructions.append(('Z', 'None', True, False, 'Util'))
                instructions.append(('RGBA', 'None', True, True, 'Base'))
                instructions.append(('albedo', 'None', True, True, 'Base'))
                instructions.append(('background', 'None', True, True, 'Base'))
                instructions.append(('RGBA', 'Every', True, True, 'LightGroup'))
                instructions.append(('RGBA_direct', 'Every', True, True, 'LightGroup'))
                instructions.append(('RGBA_indirect', 'Every', True, True, 'LightGroup'))
                instructions.append(('diffuse', 'Every', True, True, 'LightGroup'))
                instructions.append(('diffuse_direct', 'Every', True, True, 'LightGroup'))
                instructions.append(('diffuse_indirect', 'Every', True, True, 'LightGroup'))
                instructions.append(('coat', 'Every', True, True, 'LightGroup'))
                instructions.append(('coat_direct', 'Every', True, True, 'LightGroup'))
                instructions.append(('coat_indirect', 'Every', True, True, 'LightGroup'))
                instructions.append(('emission', 'Every', True, True, 'LightGroup'))
                instructions.append(('emission_direct', 'Every', True, True, 'LightGroup'))
                instructions.append(('emission_indirect', 'Every', True, True, 'LightGroup'))
                instructions.append(('sheen', 'Every', True, True, 'LightGroup'))
                instructions.append(('sheen_direct', 'Every', True, True, 'LightGroup'))
                instructions.append(('sheen_indirect', 'Every', True, True, 'LightGroup'))
                instructions.append(('sss', 'Every', True, True, 'LightGroup'))
                instructions.append(('sss_direct', 'Every', True, True, 'LightGroup'))
                instructions.append(('sss_indirect', 'Every', True, True, 'LightGroup'))
                instructions.append(('specular', 'Every', True, True, 'LightGroup'))
                instructions.append(('specular_direct', 'Every', True, True, 'LightGroup'))
                instructions.append(('specular_indirect', 'Every', True, True, 'LightGroup'))
                instructions.append(('transmission', 'Every', True, True, 'LightGroup'))
                instructions.append(('transmission_direct', 'Every', True, True, 'LightGroup'))
                instructions.append(('transmission_indirect', 'Every', True, True, 'LightGroup'))
                instructions.append(('shadow_matte', 'Every', True, True, 'LightGroup'))
                instructions.append(('volume', 'Every', True, True, 'LightGroup'))
            case 'full_Assembly':
                instructions.append(('crypto_object', 'None', True, False, 'Util'))
                instructions.append(('N', 'None', True, False, 'Util'))
                instructions.append(('P', 'None', True, False, 'Util'))
                instructions.append(('Z', 'None', True, False, 'Util'))
                instructions.append(('RGBA', 'None', True, True, 'Base'))
                instructions.append(('albedo', 'None', True, True, 'Base'))
                instructions.append(('background', 'None', True, True, 'Base'))
                instructions.append(('RGBA', 'Every', True, True, 'LightGroup'))
                instructions.append(('diffuse', 'Every', True, True, 'LightGroup'))
                instructions.append(('coat', 'Every', True, True, 'LightGroup'))
                instructions.append(('emission', 'Every', True, True, 'LightGroup'))
                instructions.append(('sheen', 'Every', True, True, 'LightGroup'))
                instructions.append(('sss', 'Every', True, True, 'LightGroup'))
                instructions.append(('specular', 'Every', True, True, 'LightGroup'))
                instructions.append(('transmission', 'Every', True, True, 'LightGroup'))
                instructions.append(('shadow_matte', 'Every', True, True, 'LightGroup'))
                instructions.append(('volume', 'Every', True, True, 'LightGroup'))
            case 'Only_RGBA':
                instructions.append(('crypto_object', 'None', True, False, 'Util'))
                instructions.append(('N', 'None', True, False, 'Util'))
                instructions.append(('P', 'None', True, False, 'Util'))
                instructions.append(('Z', 'None', True, False, 'Util'))
                instructions.append(('RGBA', 'None', True, True, 'Base'))
                instructions.append(('albedo', 'None', True, True, 'Base'))
                instructions.append(('background', 'None', True, True, 'Base'))
                instructions.append(('RGBA', 'Every', True, True, 'LightGroup'))
            case 'RGBA_Diffuse_Specular':
                instructions.append(('crypto_object', 'None', True, False, 'Util'))
                instructions.append(('N', 'None', True, False, 'Util'))
                instructions.append(('P', 'None', True, False, 'Util'))
                instructions.append(('Z', 'None', True, False, 'Util'))
                instructions.append(('RGBA', 'None', True, True, 'Base'))
                instructions.append(('albedo', 'None', True, True, 'Base'))
                instructions.append(('background', 'None', True, True, 'Base'))
                instructions.append(('RGBA', 'Every', True, True, 'LightGroup'))
                instructions.append(('diffuse', 'Every', True, True, 'LightGroup'))
                instructions.append(('specular', 'Every', True, True, 'LightGroup'))
            case 'All_But_Emission_Transmission':
                instructions.append(('crypto_object', 'None', True, False, 'Util'))
                instructions.append(('N', 'None', True, False, 'Util'))
                instructions.append(('P', 'None', True, False, 'Util'))
                instructions.append(('Z', 'None', True, False, 'Util'))
                instructions.append(('RGBA', 'None', True, True, 'Base'))
                instructions.append(('albedo', 'None', True, True, 'Base'))
                instructions.append(('background', 'None', True, True, 'Base'))
                instructions.append(('RGBA', 'Every', True, True, 'LightGroup'))
                instructions.append(('diffuse', 'Every', True, True, 'LightGroup'))
                instructions.append(('coat', 'Every', True, True, 'LightGroup'))
                instructions.append(('sheen', 'Every', True, True, 'LightGroup'))
                instructions.append(('specular', 'Every', True, True, 'LightGroup'))
        return instructions
    
    """
      Iterates through the entire data structure and checks it off with the given UI Instructions
      if objects are found that do not comply with the UI Instructions they are changed to comply again.
      no new AOV Passes are created or removed with this command
    """
    def applyUiInstructions(self, uiInstructions):
        for data in self.ListOfAOVS:
            dataType = data[6]
            for uiInstruction in uiInstructions:
                instructionType = uiInstruction[4]
                instructionPass = uiInstruction[0]
                instructionLightGroup = uiInstruction[1]
                instructionCreate = uiInstruction[2]
                instructionDenoise = uiInstruction[3]
                if dataType == instructionType:
                    dataPassUI = data[2]
                    dataPass = cmds.optionMenu(dataPassUI, query = True, value=True)
                    if dataType == 'LightGroup':
                        dataLightGrpUI = data[1]
                        dataLightGrp = cmds.optionMenu(dataLightGrpUI, query = True, value=True)
                        if (instructionLightGroup == 'Every' or instructionLightGroup == dataLightGrp) :
                            self.applyCreateAndDenoiseTo(data[3], data[4], instructionCreate, instructionDenoise)
                    else: 
                        if dataPass == instructionPass:
                            self.applyCreateAndDenoiseTo(data[3], data[4], instructionCreate, instructionDenoise)
    
    """function to set the create and denoise checkbox parameters as one instead of seperate calls"""
    def applyCreateAndDenoiseTo(self, createUI, denoiseUI, create, denoise):
        cmds.checkBox(createUI, edit = True, value=create)
        cmds.checkBox(denoiseUI, edit = True, value=denoise)
    
    """
      function takes a uiContainer to be filled and a set of uiInstructions to fill the container with, aswell as a string enum type to determine what container should be targeted
      uiI Instructions are organisedas tulips with the following structure
          (AOVPassToSet,LightGroupToSet/or None/ or Every,createAOV,Denoise,type)
    """
    def executeUiInstructions(self, uiInstructions):
        for instruction in uiInstructions:
            #set instruction parameters
            aov = instruction[0]
            lightgroup = instruction[1]
            createAOV = instruction[2]
            denoise = instruction[3]
            type = instruction[4]
            #set execution parameters
            lightGroups = []
            lightGroupIndex = -1
            AOVGroups = []
            AOVIndex = -1
            uiContainer = ''
            
            match type:
                case 'Util':
                    AOVIndex = self.getIndexFromElementInList(aov, self.UtilityPasses)
                    AOVGroups = self.UtilityPasses
                    uiContainer = self.UtilC
                    self.addPass_BTNAction(uiContainer, AOVGroups, AOVIndex, lightGroups, lightGroupIndex, createAOV, denoise, 'Util')
                case 'Base':
                    AOVIndex = self.getIndexFromElementInList(aov, self.AOVPasses)
                    AOVGroups = self.AOVPasses
                    uiContainer = self.BaseC
                    self.addPass_BTNAction(uiContainer, AOVGroups, AOVIndex, lightGroups, lightGroupIndex, createAOV, denoise, 'Base')
                case 'LightGroup':
                    AOVIndex = self.getIndexFromElementInList(aov, self.AOVPasses)
                    AOVGroups = self.AOVPasses
                    uiContainer = self.BaseC
                    match lightgroup:
                        case 'Every':
                            lightGroups = self.ListOfLightGroups
                            for element in self.LightGroupsCs:
                                lightGroupIndex = self.getIndexFromElementInList(element[0], self.ListOfLightGroups)
                                self.addPass_BTNAction(element[1], AOVGroups, AOVIndex, lightGroups, lightGroupIndex, createAOV, denoise, 'LightGroup')
                        case _:
                            lightGroupIndex = self.getIndexFromElementInList(lightgroup, self.ListOfLightGroups)
                            lightGroups = self.ListOfLightGroups
                            lightGroupContainer = self.LightGroupsCs[lightGroupIndex][1]
                            self.addPass_BTNAction(lightGroupContainer, AOVGroups, AOVIndex, lightGroups, lightGroupIndex, createAOV, denoise, 'LightGroup')
    
    """function to housekeep the UI and internal Datastructure to keep them on par when adding elements"""
    def addPassToDataStructure(self, lightGroup, AOVPass, create, denoising, parentElement, type):
        self.ListOfAOVS.append((self.AOVIndexCounter, lightGroup, AOVPass, create, denoising, parentElement, type))
        self.AOVIndexCounter = self.AOVIndexCounter + 1
    
    """function to housekeep the UI and internal Datastructure to keep them on par when removing elements"""
    def removePassFromDataStructure(self, strIndex):
        position = -1
        for index in range(len(self.ListOfAOVS)):
            element = self.ListOfAOVS[index]
            if element[0] == strIndex:
                position = index
                break;
        if position > -1:
            cmds.deleteUI(self.ListOfAOVS[position][5])
            del self.ListOfAOVS[position]