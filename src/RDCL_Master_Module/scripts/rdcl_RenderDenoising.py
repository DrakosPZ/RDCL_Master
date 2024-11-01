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

import json



##########################################################
# Deactivate all AOVS of currently active Layer
##########################################################

""" Creates all overrides for all AOVs and turns them off """
class PW_DeactivateAllAOVs(object):
    #constructor
    def __init__(self):
        self.createAOVOverrides(pwUtils.getAOVs(), ["aiAOV_RGBA"]);
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
        if not isinstance(layer, maya.app.renderSetup.model.renderLayer.DefaultRenderLayer):
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
        allAOVs = pwUtils.getAOVs(1)
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
        allAOVsString = pwUtils.getAOVsAsString(plainText, checkActivity, True);
        pyperclip.copy(allAOVsString);

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
        self.presets = [
            ('BASEData', [
                ('ID', 'None', True, False, 'Util'),
                ('N', 'None', True, False, 'Util'),
                ('P', 'None', True, False, 'Util'),
                ('Z', 'None', True, False, 'Util')
            ]),
            ('BASEPass', [
                ('RGBA', 'None', True, False, 'Base'),
                ('albedo', 'None', True, False, 'Base'),
                ('background', 'None', True, False, 'Base')
            ]),
            ('Full_DetailAssembly', [
                ('crypto_object', 'None', True, False, 'Util'),
                ('N', 'None', True, False, 'Util'),
                ('P', 'None', True, False, 'Util'),
                ('Z', 'None', True, False, 'Util'),
                ('RGBA', 'None', True, True, 'Base'),
                ('albedo', 'None', True, True, 'Base'),
                ('background', 'None', True, True, 'Base'),
                ('RGBA', 'Every', True, True, 'LightGroup'),
                ('RGBA_direct', 'Every', True, True, 'LightGroup'),
                ('RGBA_indirect', 'Every', True, True, 'LightGroup'),
                ('diffuse', 'Every', True, True, 'LightGroup'),
                ('diffuse_direct', 'Every', True, True, 'LightGroup'),
                ('diffuse_indirect', 'Every', True, True, 'LightGroup'),
                ('coat', 'Every', True, True, 'LightGroup'),
                ('coat_direct', 'Every', True, True, 'LightGroup'),
                ('coat_indirect', 'Every', True, True, 'LightGroup'),
                ('emission', 'Every', True, True, 'LightGroup'),
                ('emission_direct', 'Every', True, True, 'LightGroup'),
                ('emission_indirect', 'Every', True, True, 'LightGroup'),
                ('sheen', 'Every', True, True, 'LightGroup'),
                ('sheen_direct', 'Every', True, True, 'LightGroup'),
                ('sheen_indirect', 'Every', True, True, 'LightGroup'),
                ('sss', 'Every', True, True, 'LightGroup'),
                ('sss_direct', 'Every', True, True, 'LightGroup'),
                ('sss_indirect', 'Every', True, True, 'LightGroup'),
                ('specular', 'Every', True, True, 'LightGroup'),
                ('specular_direct', 'Every', True, True, 'LightGroup'),
                ('specular_indirect', 'Every', True, True, 'LightGroup'),
                ('transmission', 'Every', True, True, 'LightGroup'),
                ('transmission_direct', 'Every', True, True, 'LightGroup'),
                ('transmission_indirect', 'Every', True, True, 'LightGroup'),
                ('shadow_matte', 'Every', True, True, 'LightGroup'),
                ('volume', 'Every', True, True, 'LightGroup')
            ]),
            ('Full_Simple', [
                ('crypto_object', 'None', True, False, 'Util'),
                ('N', 'None', True, False, 'Util'),
                ('P', 'None', True, False, 'Util'),
                ('Z', 'None', True, False, 'Util'),
                ('RGBA', 'None', True, True, 'Base'),
                ('albedo', 'None', True, True, 'Base'),
                ('background', 'None', True, True, 'Base'),
                ('RGBA', 'Every', True, True, 'LightGroup'),
                ('diffuse', 'Every', True, True, 'LightGroup'),
                ('coat', 'Every', True, True, 'LightGroup'),
                ('emission', 'Every', True, True, 'LightGroup'),
                ('sheen', 'Every', True, True, 'LightGroup'),
                ('sss', 'Every', True, True, 'LightGroup'),
                ('specular', 'Every', True, True, 'LightGroup'),
                ('transmission', 'Every', True, True, 'LightGroup'),
                ('shadow_matte', 'Every', True, True, 'LightGroup'),
                ('volume', 'Every', True, True, 'LightGroup')
            ]),
            ('Full_RGBA', [
                ('crypto_object', 'None', True, False, 'Util'),
                ('N', 'None', True, False, 'Util'),
                ('P', 'None', True, False, 'Util'),
                ('Z', 'None', True, False, 'Util'),
                ('RGBA', 'None', True, True, 'Base'),
                ('albedo', 'None', True, True, 'Base'),
                ('background', 'None', True, True, 'Base'),
                ('RGBA', 'Every', True, True, 'LightGroup')
            ]),
            ('Full_Direct_Indirect', [
                ('crypto_object', 'None', True, False, 'Util'),
                ('N', 'None', True, False, 'Util'),
                ('P', 'None', True, False, 'Util'),
                ('Z', 'None', True, False, 'Util'),
                ('RGBA', 'None', True, True, 'Base'),
                ('albedo', 'None', True, True, 'Base'),
                ('background', 'None', True, True, 'Base'),
                ('RGBA_direct', 'Every', True, True, 'LightGroup'),
                ('RGBA_indirect', 'Every', True, True, 'LightGroup'),
                ('emission', 'Every', True, True, 'LightGroup')
            ]),
            ('DetailAssembly', [
                ('crypto_object', 'None', True, False, 'Util'),
                ('N', 'None', True, False, 'Util'),
                ('P', 'None', True, False, 'Util'),
                ('Z', 'None', True, False, 'Util'),
                ('RGBA', 'None', True, True, 'Base'),
                ('albedo', 'None', True, True, 'Base'),
                ('background', 'None', True, True, 'Base'),
                ('RGBA_direct', 'None', True, True, 'Base'),
                ('RGBA_indirect', 'None', True, True, 'Base'),
                ('diffuse', 'None', True, True, 'Base'),
                ('diffuse_direct', 'None', True, True, 'Base'),
                ('diffuse_indirect', 'None', True, True, 'Base'),
                ('coat', 'None', True, True, 'Base'),
                ('coat_direct', 'None', True, True, 'Base'),
                ('coat_indirect', 'None', True, True, 'Base'),
                ('emission', 'None', True, True, 'Base'),
                ('emission_direct', 'None', True, True, 'Base'),
                ('emission_indirect', 'None', True, True, 'Base'),
                ('sheen', 'None', True, True, 'Base'),
                ('sheen_direct', 'None', True, True, 'Base'),
                ('sheen_indirect', 'None', True, True, 'Base'),
                ('sss', 'None', True, True, 'Base'),
                ('sss_direct', 'None', True, True, 'Base'),
                ('sss_indirect', 'None', True, True, 'Base'),
                ('specular', 'None', True, True, 'Base'),
                ('specular_direct', 'None', True, True, 'Base'),
                ('specular_indirect', 'None', True, True, 'Base'),
                ('transmission', 'None', True, True, 'Base'),
                ('transmission_direct', 'None', True, True, 'Base'),
                ('transmission_indirect', 'None', True, True, 'Base'),
                ('shadow_matte', 'None', True, True, 'Base'),
                ('volume', 'None', True, True, 'Base')
            ]),
            ('Simple', [
                ('crypto_object', 'None', True, False, 'Util'),
                ('N', 'None', True, False, 'Util'),
                ('P', 'None', True, False, 'Util'),
                ('Z', 'None', True, False, 'Util'),
                ('RGBA', 'None', True, True, 'Base'),
                ('albedo', 'None', True, True, 'Base'),
                ('background', 'None', True, True, 'Base'),
                ('diffuse', 'None', True, True, 'Base'),
                ('coat', 'None', True, True, 'Base'),
                ('emission', 'None', True, True, 'Base'),
                ('sheen', 'None', True, True, 'Base'),
                ('sss', 'None', True, True, 'Base'),
                ('specular', 'None', True, True, 'Base'),
                ('transmission', 'None', True, True, 'Base'),
                ('shadow_matte', 'None', True, True, 'Base'),
                ('volume', 'None', True, True, 'Base')
            ]),
            ('RGBA', [
                ('crypto_object', 'None', True, False, 'Util'),
                ('N', 'None', True, False, 'Util'),
                ('P', 'None', True, False, 'Util'),
                ('Z', 'None', True, False, 'Util'),
                ('RGBA', 'None', True, True, 'Base'),
                ('albedo', 'None', True, True, 'Base'),
                ('background', 'None', True, True, 'Base'),
            ]),
            ('Direct_Indirect', [
                ('crypto_object', 'None', True, False, 'Util'),
                ('N', 'None', True, False, 'Util'),
                ('P', 'None', True, False, 'Util'),
                ('Z', 'None', True, False, 'Util'),
                ('RGBA', 'None', True, True, 'Base'),
                ('albedo', 'None', True, True, 'Base'),
                ('background', 'None', True, True, 'Base'),
                ('RGBA_direct', 'None', True, True, 'Base'),
                ('RGBA_indirect', 'None', True, True, 'Base'),
                ('emission', 'None', True, True, 'Base')
            ])
        ]
        self.integratedAOVs = [
            ('ID',['Utility']),
            ('N',['Utility']),
            ('P',['Utility']),
            ('Z',['Utility']),
            ('crypto_object',['Utility']),
            ('crypto_asset',['Utility']),
            ('crypto_material',['Utility']),
            ('motionvector',['Utility']),
            ('highlight',['Utility']),
            ('opacity',['Utility']),
            ('raycount',['Utility']),
            ('rim_light',['Utility']),
            ('volume_Z',['Utility']),
            ('volume_opacity',['Utility']),
            ('RGBA',['Integrated','Lightgroup']),
            ('RGBA_indirect',['Integrated','Lightgroup']),
            ('RGBA_direct',['Integrated','Lightgroup']),
            ('diffuse',['Integrated','Lightgroup']),
            ('diffuse_indirect',['Integrated','Lightgroup']),
            ('diffuse_direct',['Integrated','Lightgroup']),
            ('coat',['Integrated','Lightgroup']),
            ('coat_albedo',['Integrated','Lightgroup']),
            ('coat_indirect',['Integrated','Lightgroup']),
            ('coat_direct',['Integrated','Lightgroup']),
            ('emission',['Integrated','Lightgroup']),
            ('emission_indirect',['Integrated','Lightgroup']),
            ('emission_direct',['Integrated','Lightgroup']),
            ('sheen',['Integrated','Lightgroup']),
            ('sheen_albedo',['Integrated','Lightgroup']),
            ('sheen_indirect',['Integrated','Lightgroup']),
            ('sheen_direct',['Integrated','Lightgroup']),
            ('specular',['Integrated','Lightgroup']),
            ('specular_albedo',['Integrated','Lightgroup']),
            ('specular_indirect',['Integrated','Lightgroup']),
            ('specular_direct',['Integrated','Lightgroup']),
            ('sss',['Integrated','Lightgroup']),
            ('sss_albedo',['Integrated','Lightgroup']),
            ('sss_indirect',['Integrated','Lightgroup']),
            ('sss_direct',['Integrated','Lightgroup']),
            ('transmission',['Integrated','Lightgroup']),
            ('transmission_albedo',['Integrated','Lightgroup']),
            ('transmission_indirect',['Integrated','Lightgroup']),
            ('transmission_direct',['Integrated','Lightgroup']),
            ('albedo',['Integrated']),
            ('background',['Integrated']),
            ('direct',['Integrated','Lightgroup']),
            ('indirect',['Integrated','Lightgroup']),
            ('shadow',['Integrated']),
            ('shadow_diff',['Integrated']),
            ('shadow_mask',['Integrated']),
            ('shadow_matte',['Integrated']),
            ('volume',['Integrated','Lightgroup']),
            ('volume_albedo',['Integrated']),
            ('volume_direct',['Integrated','Lightgroup']),
            ('volume_indirect',['Integrated','Lightgroup']),
        ]
        self.presetsShort = [''] + [preset[0] for preset in self.presets][2:]
        self.AOVPasses = [aovPass[0] for aovPass in self.integratedAOVs if 'Integrated' in aovPass[1]]
        self.AOVLGPasses = [aovPass[0] for aovPass in self.integratedAOVs if 'Lightgroup' in aovPass[1]]
        self.UtilityPasses = [aovPass[0] for aovPass in self.integratedAOVs if 'Utility' in aovPass[1]]
        self.custom = []

        #UI Global Parameters
        self.window = 'PW_PopulateAOVs_Window'
        self.title = 'AOV Master'
        self.size = (900, 800)
        self.rowHorizontalGap = 5
        self.columnVerticalGapBig = 20
        self.columnVerticalGapMedium = 10
        self.columnVerticalGapSmall = 5
        
        self.ListOfAOVS = []
        self.ListOfLightGroups = pwUtils.getLightGroupsFromLights()
        self.AOVIndexCounter = 0
        self.UtilC = ''
        self.BaseC = ''
        self.LightGroupsCs = []
        self.LightGroupEvery = []
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
        pwUtils.fillOptionMenuWithElements(self.presetsShort)
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
        # set up per light group management UI
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
            cmds.button(label='Add Pass', command = partial(self.addPass_BTNAction, parentUI, self.AOVLGPasses, -1, groupList, index, False, False, 'LightGroup'))
            cmds.separator(width = self.rowHorizontalGap, style = 'none')
            cmds.setParent(tempC)

        # setup Every Templating Section
        cmds.separator(height=self.columnVerticalGapMedium, style='none')
        cmds.text('Templating Every Light Group AOVs')
        cmds.text('These are only used for the Tempalte Feature')
        parentUI  = cmds.columnLayout(adjustableColumn = True)
        self.LightGroupEvery.append(('Every', parentUI))
        tmpRowWidth = [self.size[0]*0.3, self.size[0]*0.3, self.size[0]*0.1, self.size[0]*0.15]
        cmds.rowLayout(numberOfColumns = 7, width = self.size[0])
        cmds.separator(width = self.rowHorizontalGap, style = 'none')
        AOVPass = cmds.optionMenu(label = 'AOV Pass', width = tmpRowWidth[1])
        pwUtils.fillOptionMenuWithElements([''])
        cmds.optionMenu(AOVPass, edit = True, select = 1, enable = False)
        cmds.separator(width = self.rowHorizontalGap, style = 'none')
        lightGroup = cmds.optionMenu(label = 'Light Group', width = tmpRowWidth[0])
        pwUtils.fillOptionMenuWithElements(['Every'])
        cmds.optionMenu(lightGroup, edit = True, select = 1, enable = False)
        cmds.separator(width = self.rowHorizontalGap, style = 'none')
        cmds.button(label='Add Pass', command = partial(self.addPass_BTNAction, parentUI, self.AOVLGPasses, -1, ['Every'], 0, False, False, 'LightGroup'))
        cmds.separator(width = self.rowHorizontalGap, style = 'none')
        cmds.setParent(tempC)
        cmds.setParent(self.mainCL)

    def refreshInstructionUI(self):
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

    
    #--- UI Interaction functions from here on
    def createAOVs_BTNAction(self, *args):
        AOVConstructionObject = self.unpackAOVTulipforList(self.ListOfAOVS)
        AOVConstructionObject = [instruction for instruction in AOVConstructionObject if instruction[1] != 'Every']
        pwUtils.createAOVs(AOVConstructionObject)
        
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
        self.refreshInstructionUI()
                
       
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
        AOVConstructionObject = self.unpackAOVTulipforList(self.ListOfAOVS, True)
        dialogResult = cmds.fileDialog2(bbo = 2, cap = 'Open Template as', fm = 0)
        if len(dialogResult) > 0:
            pickedFile = dialogResult[0]
            file = open(pickedFile, "w")
            file.write(pwUtils.jsonfy(AOVConstructionObject))
            file.close()
            cmds.confirmDialog(
                title='AOV Master Templater',
                message='Template has been stored to given location.',
            )
        else : 
            cmds.confirmDialog(
                title='AOV Master Templater',
                message='Error: Provide one Location with a given Filename.txt',
            )
        
    def presetLoad_BTNAction(self, *args):
        dialogResult = cmds.fileDialog2(bbo = 2, cap = 'Open Template as', fm = 1)
        if len(dialogResult) > 0:
            pickedFile = dialogResult[0]
            file = open(pickedFile, "r")
            fileOutput = file.read()
            file.close()

            python_obj = pwUtils.deJsonfy(fileOutput)
            AOVCustomTemplate = []
            for element in python_obj:
                partialTuple = ()
                for partial in element:
                    partialTuple = partialTuple + (partial, )
                AOVCustomTemplate.append(partialTuple)
            
            self.custom = AOVCustomTemplate
            menuItems = cmds.optionMenu(self.PresetUI, q=True, itemListLong=True)
            if menuItems:
                cmds.deleteUI(menuItems)
            pwUtils.fillOptionMenuWithElements(self.presetsShort + ['Custom'], self.PresetUI)
            cmds.optionMenu(self.PresetUI, edit = True, select = len(self.presetsShort + ['Custom']))

            self.refreshInstructionUI()

            cmds.confirmDialog(
                title='AOV Master Templater',
                message='Template has been loaded and added as Custom Preset.',
            )
        else : 
            cmds.confirmDialog(
                title='AOV Master Templater',
                message='Error: Provide one Location with a given Filename.txt',
            )
    
    #--- helper functions 
    """ unpacks Tulip and window element into => (AOVPass, AOVName, Create AOV, Denoise AOV, (optional)Origin) """
    def unpackAOVTulipforList(self, list, origin = False):
        unpackedList = []
        for strIndex, aovNameUI, aovPassUI, createUI, denoiseUI, element, type in list:
            aovName = cmds.optionMenu(aovNameUI, query = True, value=True)
            aovPass = cmds.optionMenu(aovPassUI, query = True, value=True)
            create = cmds.checkBox(createUI, query = True, value=True)
            denoise = cmds.checkBox(denoiseUI, query = True, value=True)
            if origin:
                unpackedList.append((aovPass, aovName, create, denoise, type))
            else:
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
        if category == 'Custom': 
            instructions = self.custom
        else :
            instructions = dict(self.presets).get(category, [])
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