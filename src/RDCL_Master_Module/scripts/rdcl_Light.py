##########################################################
#   Written by PhilipW./Rauhm, usable under CCLicense-2024
#             just name me as Tech Support
##########################################################



import maya.cmds as cmds;
import rdcl_utils as pwUtils;
import re



##########################################################
# Name Light Group AOVs as Lights Names
##########################################################

""" Creates all overrides for all AOVs and turns them off """
class PW_SetLightGroupsToNames(object):
    #constructor
    def __init__(self):
        self.lightsToFilter = []
        print('Implement double click feature to select which light can be filtered for and not')
        self.nameChangingRegEx = "^(.+?)_"
        print('Implement double click feature to change the pattern by which the LightsTransform name is changed to the AOV Light Group Name')
        self.nameLightGroupsAsNames(self.lightsToFilter, self.nameChangingRegEx);

    '''
     when Lights are selected it uses the selected set of Lights 
     otherwise it fetches all light groups based on the given lights to filters,
         per default the getLights() function only fetches Arnold Lights
     it then sets all lights' AOVs to the lights' name in the outliner, using the nameChangingRegEx to format the name
        per default it will remove every character before the first _ (aiAL_TestLight => TestLight)
     
     lightsToFilter: String[] => an array of light sources name to be filtered for, per default empty
     nameChangingRegEx: String => The regex expression to match remove from the lights name for.
    '''
    def nameLightGroupsAsNames(self, lightsToFilter, nameChangingRegEx):
        lights = [];
        selected = cmds.ls(sl=True,long=True) or [];

        if len(selected) > 0:
            lights = selected
        else:
            lights = pwUtils.getLights()
        for light in lights:
            aovName = re.sub(nameChangingRegEx, '', str(light.getParent()))
            light.aiAov.set(aovName)
