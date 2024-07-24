##########################################################
#   Written by PhilipW./Rauhm, usable under CCLicense-2024
#             just name me as Tech Support
##########################################################


##########################################################
# library import
##########################################################

import maya.cmds as cmds
import mtoa.aovs as aovs;
import pymel.core as pmc
from functools import partial
import maya.app.renderSetup.views.overrideUtils as utils;
import maya.app.renderSetup.model.renderSetup as renderSetup


##########################################################
# Fill AOV from Light Group
##########################################################
#globalParameters
presets = ['', 'full_Assembly','Only_RGBA','RGBA_Diffuse_Specular','All_But_Emission_Transmission', 'full_DetailAssembly']
AOVPasses = ['RGBA', 'RGBA_indirect', 'RGBA_direct', 'diffuse', 'diffuse_indirect', 'diffuse_direct', 'coat', 'coat_albedo', 'coat_indirect', 'coat_direct', 'emission', 'emission_indirect', 'emission_direct', 'sheen', 'sheen_albedo', 'sheen_indirect', 'sheen_direct', 'specular', 'specular_albedo', 'specular_indirect', 'specular_direct', 'sss', 'sss_albedo', 'sss_indirect', 'sss_direct', 'transmission', 'transmission_albedo', 'transmission_indirect', 'transmission_direct', 'albedo', 'background', 'direct', 'indirect', 'shadow', 'shadow_diff', 'shadow_mask', 'shadow_matte', 'volume', 'volume_albedo', 'volume_direct', 'volume_indirect']
UtilityPasses = ['ID','N','P','Z','crypto_object', 'crypto_asset', 'crypto_material', 'motionvector', 'highlight', 'opacity', 'raycount', 'rim_light', 'volume_Z', 'volume_opacity']

pickedUtilityPasses = ['ID','N','P','Z','crypto_object']
pickedBasePasses = ['RGBA','albedo','background','shadow', 'volume',]

#globalCounter
PW_aovPositionCounter = 1;

""" Add AOVs with VarianceFilterAdded """
def PW_addAOVWithFilter(name, type, filterType, toAdd):
    global PW_aovPositionCounter;
    newAOV = aovs.AOVInterface().addAOV(name,aovType=type);
    if toAdd:
        aifilter = pmc.createNode('aiAOVFilter', n='aiAOVFilter');
        aifilter.setAttr('aiTranslator', 'variance');
        cmds.connectAttr('defaultArnoldDriver.message', aovs.AOVInterface().getAOVNode(name)+'.outputs['+str(PW_aovPositionCounter)+'].driver');
        cmds.connectAttr(aifilter+'.message', aovs.AOVInterface().getAOVNode(name)+'.outputs['+str(PW_aovPositionCounter)+'].filter');
    PW_aovPositionCounter+=1;

""" get Lights """
def PW_getLights():
    return pmc.ls(type=['aiAreaLight','aiSkyDomeLight','aiPhotometricLight','aiLightPortal'])

""" get AOVs from Lights """
def PW_getLightGroups():
    groups = [];
    filteredGroups = [];
    for light in PW_getLights():
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
  resolves instructions and creates AOVs accordingly  
  instruction => (AOVPass, AOVName, Create AOV, Denoise AOV)     
"""  
def PW_createAOVs(instructions):
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
        
        #safeguarding against datapass denosing and right parameter settings
        match AOVName: 
            case 'RGBA':
                type = 'rgba'
            case 'ID':
                type = 'uint'
                beDenoised = False
            case 'N':
                type = 'vector'
                filterType = 'closest'
                beDenoised = False
            case 'P':
                type = 'vector'
                filterType = 'closest'
                beDenoised = False
            case 'Pref':
                filterType = 'closest'
                beDenoised = False
            case 'Z':
                type = 'float'
                filterType = 'closest'
                beDenoised = False
            case 'crypto_object':
                beDenoised = False
            case 'crypto_asset':
                beDenoised = False
            case 'crypto_material':
                beDenoised = False
            case 'highlight':
                beDenoised = False
            case 'motionvector':
                beDenoised = False
            case 'opacity':
                beDenoised = False
            case 'rim_light':
                beDenoised = False
            case 'shadow_diff':
                beDenoised = False
            case 'shadow_mask':
                beDenoised = False
            case 'cputime':
                type = 'float'
                beDenoised = False
            case 'shadow_matte':
                type = 'rgba'
            case 'volume_Z':
                type = 'float'
                filterType = 'closest'
                beDenoised = False
            case 'volume_opacity':
                beDenoised = False
        
        if CreateAOV:
            PW_addAOVWithFilter(AOVPass + AOVName, type, filterType, beDenoised)

""" Assumes that there are no prior set AOVs aswell that the already set AOVs are instantiated with the default closest gausian Filter """
class PW_PopulateAOVs_Window(object):
    #constructor
    def __init__(self):
        self.window = 'PW_PopulateAOVs_Window'
        self.title = 'Better AOV And Denoising'
        self.size = (900, 800)
        self.rowHorizontalGap = 5
        self.columnVerticalGapBig = 20
        self.columnVerticalGapMedium = 10
        self.columnVerticalGapSmall = 5
        self.ListOfAOVS = []
        self.ListOfLightGroups = PW_getLightGroups()
        self.AOVIndexCounter = 0
        self.UtilC = ''
        self.BaseC = ''
        self.LightGroupsCs = []
        self.PresetUI = ''

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
        cmds.text('Written by Philip Wersonig - v0.1.0', align='right')
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
        fillOptionMenuWithElements(presets)
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
 
    def createUtilCheckBoxes(self):
        cmds.scrollLayout(width = self.size[0], height = self.size[1]*0.2)
        self.UtilC  = cmds.columnLayout(adjustableColumn = True)
        
        instructions = self.createUIInstructions('BASEData')
        self.executeUiInstructions(instructions)
        
        cmds.setParent(self.mainCL) 
        tmpRowWidth = [self.size[0]*0.1, self.size[0]*0.8]
        cmds.rowLayout(numberOfColumns = 3, width = self.size[0])
        cmds.separator(width=tmpRowWidth[0], style='none')
        cmds.button(label='Add Pass', width=tmpRowWidth[1], command = partial(self.addPass_BTNAction, self.UtilC, UtilityPasses, -1, [], -1, False, False, 'Util'))
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
        cmds.button(label='Add Pass', width=tmpRowWidth[1], command = partial(self.addPass_BTNAction, self.BaseC, AOVPasses, -1, [], -1, False, False, 'Base'))
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
            fillOptionMenuWithElements([''])
            cmds.optionMenu(AOVPass, edit = True, select = 1, enable = False)
            cmds.separator(width = self.rowHorizontalGap, style = 'none')
            lightGroup = cmds.optionMenu(label = 'Light Group', width = tmpRowWidth[0])
            fillOptionMenuWithElements(groupList)
            cmds.optionMenu(lightGroup, edit = True, select = index + 1, enable = False)
            cmds.separator(width = self.rowHorizontalGap, style = 'none')
            cmds.button(label='Add Pass', command = partial(self.addPass_BTNAction, parentUI, AOVPasses, -1, groupList, index, False, False, 'LightGroup'))
            cmds.separator(width = self.rowHorizontalGap, style = 'none')
            cmds.setParent(tempC)
        cmds.setParent(self.mainCL)
        
    def createAOVs_BTNAction(self, *args):
        AOVConstructionObject = self.unpackAOVTulipforList(self.ListOfAOVS)
        print(AOVConstructionObject)
        PW_createAOVs(AOVConstructionObject)
        
    def addPass_BTNAction(self, parentUI, AOVGroup, AOVIndex, LightGroup, LGIndex, createAOV, denoise, type, *args):
        cmds.setParent(parentUI)            
        tmpRowWidth = [self.size[0]*0.3, self.size[0]*0.3, self.size[0]*0.1, self.size[0]*0.15, self.size[0]*0.1]
        passRow = cmds.rowLayout(numberOfColumns = 11, width = self.size[0])
        cmds.separator(width = self.rowHorizontalGap, style = 'none')
        AOVPass = cmds.optionMenu(label='AOV Pass')
        fillOptionMenuWithElements(AOVGroup)
        if AOVIndex > -1:
            cmds.optionMenu(AOVPass, edit = True, select = AOVIndex + 1)
        else: 
            cmds.optionMenu(AOVPass, edit = True, select = 1)
        cmds.separator(width = self.rowHorizontalGap, style = 'none')
        lightGroup = cmds.optionMenu(label = 'Light Group', width = tmpRowWidth[0])
        fillOptionMenuWithElements(LightGroup)
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
        print('Preset Apply clicked')
        presetSelected = cmds.optionMenu(self.PresetUI, query = True, value=True)
        if presetSelected != '':
            #Construct UI Instruction based on Preset
            instructions = self.createUIInstructions(presetSelected)
            #Apply Instructions
            self.applyUiInstructions(instructions)
                
       
    def presetRecreate_BTNAction(self, *args):
        print('Preset Recreate clicked')
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
        
   #---helper functions 
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
                        print('Lightgroup')
                        print(data)
                        print(uiInstruction)
                        dataLightGrpUI = data[1]
                        dataLightGrp = cmds.optionMenu(dataLightGrpUI, query = True, value=True)
                        if (instructionLightGroup == 'Every' or instructionLightGroup == dataLightGrp) :
                            self.applyCreateAndDenoiseTo(data[3], data[4], instructionCreate, instructionDenoise)
                    else: 
                        if dataPass == instructionPass:
                            self.applyCreateAndDenoiseTo(data[3], data[4], instructionCreate, instructionDenoise)
                            
                        
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
                    AOVIndex = self.getIndexFromElementInList(aov, UtilityPasses)
                    AOVGroups = UtilityPasses
                    uiContainer = self.UtilC
                    self.addPass_BTNAction(uiContainer, AOVGroups, AOVIndex, lightGroups, lightGroupIndex, createAOV, denoise, 'Util')
                case 'Base':
                    AOVIndex = self.getIndexFromElementInList(aov, AOVPasses)
                    AOVGroups = AOVPasses
                    uiContainer = self.BaseC
                    self.addPass_BTNAction(uiContainer, AOVGroups, AOVIndex, lightGroups, lightGroupIndex, createAOV, denoise, 'Base')
                case 'LightGroup':
                    AOVIndex = self.getIndexFromElementInList(aov, AOVPasses)
                    AOVGroups = AOVPasses
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
        
    def addPassToDataStructure(self, lightGroup, AOVPass, create, denoising, parentElement, type):
        self.ListOfAOVS.append((self.AOVIndexCounter, lightGroup, AOVPass, create, denoising, parentElement, type))
        self.AOVIndexCounter = self.AOVIndexCounter + 1
    
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

#Execution
PW_PopulateAOVsWindow = PW_PopulateAOVs_Window();

##########################################################

import mtoa.aovs as aovs;
import array

#get All AOVs
def getAOVs():
    aovNames = [];
    aovPairs = aovs.AOVInterface().getAOVNodes(names=True)
    for aovElement in aovPairs:
        print(aovElement[0])
        aovNames.append(aovElement[0]);
    return aovNames;

#set AOVs
def removeAOV(aov):
    aovs.AOVInterface().removeAOV(aov);

#Executable
def removeAOVs():
    aovs.AOVInterface().removeAOVs(getAOVs());

##########################################################


#SetUp Library Paths
import sys; 
sys.path.append(r'C:\users\phili\appdata\local\programs\python\python310\lib\site-packages');

#Actual Script
import mtoa.aovs as aovs;
import mtoa.ui.arnoldmenu;
import pyperclip

# Fetching all AOV names as a string
allAOVsString = '';
aovArray = aovs.AOVInterface().getAOVNodes(names=True);

for aovElement in aovArray:
    allAOVsString += '-l ' + aovElement[0] + ' ';

allAOVsString = allAOVsString[:-1];

# Copy the string to the clipboard
pyperclip.copy(allAOVsString);
print('copied AOVs to Clipboard');
print(allAOVsString);

##########################################################

import maya.cmds as cmds
import mtoa.aovs as aovs;
import maya.app.renderSetup.views.overrideUtils as utils;
import maya.app.renderSetup.model.renderSetup as renderSetup

#Executable
def Executable():
    createOverrides(getAOVs());
    switchOffAllAOVsForActive();

#get All AOVs
def getAOVs():
    aovNames = [];
    aovPairs = aovs.AOVInterface().getAOVNodes();
    if "aiAOV_RGBA" in aovPairs:
        aovPairs.remove("aiAOV_RGBA")
    return aovPairs;

#create Overrides and set To false
def createOverrides(aovs):
    for aov in aovs:
        utils.createAbsoluteOverride(aov, 'enabled');

#switch all AOVs overrides in the currently active RenderLayer to be turned off
def switchOffAllAOVsForActive():
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

#Execution
Executable();
