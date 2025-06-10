##########################################################
#   Written by PhilipW./Rauhm, usable under CCLicense-2024
#             just name me as Tech Support
##########################################################


##########################################################
# library import
##########################################################

import maya.cmds as cmds;


##########################################################
# Toggle Proxys/Renders
##########################################################

""" Set Names of AOVs to the names the light source """
class PW_ToggleRenderAndProxy(object):
    #constructor
    def __init__(self):
        self.refreshLists()

    def refreshLists(self):
        self.proxys = cmds.ls( 'proxy' ,tr = True)
        self.renders = cmds.ls( 'render' ,tr = True)
    
    def show(self, show, elements):
            if show:
                cmds.showHidden(elements)
            else:
                cmds.hide(elements)
    
    def toggle(self):
        self.refreshLists()
        proxyVisible = cmds.getAttr(self.proxys[0]+".visibility")
        renderVisible = cmds.getAttr(self.renders[0]+".visibility")
        if (proxyVisible and not renderVisible):
            self.show(True, self.renders)
            self.show(False, self.proxys)
        elif (not proxyVisible and renderVisible):
            self.show(False, self.renders)
            self.show(True, self.proxys)
        else:
            self.show(False, self.renders)
            self.show(True, self.proxys)
