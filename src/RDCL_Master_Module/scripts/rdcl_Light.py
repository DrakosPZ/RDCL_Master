##########################################################
#   Written by PhilipW./Rauhm, usable under CCLicense-2024
#             just name me as Tech Support
##########################################################



import maya.cmds as cmds;
import pymel.core as pmc;
import rdcl_utils as pwUtils;
import re



##########################################################
# Name Light Group AOVs as Lights Names
##########################################################

""" Set Names of AOVs to the names the light source """
class PW_SetLightGroupsToNames(object):
    #constructor
    def __init__(self):
        #UI Global Parameters
        self.window = 'PW_NamingLightGroupsAOVsConfig_Window'
        self.title = 'Naming Light Groups Config'
        self.size = (900, 800)
        self.rowHorizontalGap = 5
        self.columnVerticalGapBig = 20
        self.columnVerticalGapMedium = 10
        self.columnVerticalGapSmall = 5

        self.lightsToFilter = []
        self.nameChangingRegEx = "^(.+?)_"
        
        self.configNameChangePattern = ''
        print('__init__ He He')

    def simpleClick(self):
        print('simpleClick')
        self.nameLightGroupsAsNames(self.lightsToFilter, self.nameChangingRegEx);

    def doubleClick(self):
        print('doubleClick')
        self.configUI();




    '''
        UI method opening the config UI to select 
            1: the AOV naming functions renaming behaviour.
            2: make the Types of Light filterable selectable for the artist.
    '''
    def configUI(self):
        print('configUI')
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
        
        
        ParentRowWidth = [self.size[0]*0.425, self.size[0]*0.05]
        parentRow = cmds.rowLayout(numberOfColumns = 5, width = self.size[0])
        
        cmds.columnLayout(width=ParentRowWidth[1])
        cmds.setParent(parentRow)
        
        cmds.columnLayout(width=ParentRowWidth[0])
        cmds.text(label = 'Naming pattern:', align = 'left')
        self.configNameChangePattern = cmds.textField( width = ParentRowWidth[0], text=self.nameChangingRegEx)
        cmds.text(label = 'Default: names the AOV with everything after the first _', align = 'left')
        cmds.text(label = '=> ai_test_light = test_Light', align = 'left')
        cmds.setParent(parentRow)
        
        cmds.columnLayout(width=ParentRowWidth[1])
        cmds.setParent(parentRow)
        
        cmds.columnLayout(width=ParentRowWidth[0])
        cmds.text(label = 'LightTypes')
        self.configTypeSelection = [];
        for lightType in pwUtils.allLights:
            checkbox = cmds.checkBox( label = lightType );
            self.configTypeSelection.append((lightType, checkbox));
        cmds.setParent(parentRow)
        
        cmds.columnLayout(width=ParentRowWidth[1])
        cmds.setParent(self.mainCL)
        
        
        cmds.separator(height=self.columnVerticalGapMedium, style='none')
        tmpRowWidth = [self.size[0]*0.1, self.size[0]*0.8]
        cmds.rowLayout(numberOfColumns = 3, width = self.size[0])
        cmds.separator(width=tmpRowWidth[0], style='none')
        self.actionBTN = cmds.button(label='Create AOVs', width=tmpRowWidth[1], command=self.executeConfigCommand)
        cmds.separator(width=tmpRowWidth[0], style='none')
        cmds.setParent(self.mainCL)
        cmds.separator(height=self.columnVerticalGapBig, style='none')

        #display
        cmds.showWindow() 

    '''
        Button action handle function, used to fetch the config selected Renaming behaviour aswell as the selected light types to be fetched.
    '''
    def executeConfigCommand(self, *args):
        configRegex = '';
        configTypes = [];
        configRegex = cmds.textField(self.configNameChangePattern, query = True)
        for configTypeElement in self.configTypeSelection:
            checkBoxValue = cmds.checkBox(configTypeElement[1], query = True, value=True);
            if checkBoxValue:
                configTypes.append(configTypeElement[0]);
        self.nameLightGroupsAsNames(configTypes, configRegex);
        


    '''
     when Lights are selected it uses the selected set of Lights 
     otherwise it fetches all light groups based on the given lights to filters,
         per default the getLights() function only fetches Arnold Lights
     it then sets all lights' AOVs to the lights' name in the outliner, using the nameChangingRegEx to format the name
        per default it will remove every character before the first _ (aiAL_TestLight => TestLight)
     
     lightsToFilter: String[] => an array of light sources name to be filtered for, per default empty
     nameChangingRegEx: String => The regex expression to match remove from the lights name for.
    '''
    def nameLightGroupsAsNames(self, lightsToFilter = None, nameChangingRegEx = None):
        print('nameLightGroupsAsNames')
        lights = [];
        selected = pmc.ls(sl=True,long=True) or [];
        
        
        if nameChangingRegEx is None:
            nameChangingRegEx = self.nameChangingRegEx;

        if len(selected) > 0:
            lights = selected
        else:
            if lightsToFilter is None or len(lightsToFilter) <= 0:
                lights = pwUtils.getLights();
            else:
                lights = pwUtils.getLights(lightsToFilter);
        for light in lights:
            aovName = re.sub(nameChangingRegEx, '', str(light))
            aovName = aovName.replace('Shape', '')
            try:
                light.aiAov.set(aovName)
            except:
                print('Light: ' + str(light) + ' is not arnold AOV Compatible.')