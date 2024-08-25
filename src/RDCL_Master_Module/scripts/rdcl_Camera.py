##########################################################
#   Written by PhilipW./Rauhm, usable under CCLicense-2024
#             just name me as Tech Support
##########################################################


##########################################################
# library import
##########################################################

import maya.cmds as cmds

##########################################################
# Camera master Class
##########################################################
class PW_TearOffCopyOfSelectedCam(): 
    #constructor
    def __init__(self):
        self.tearOffCopyOfSelectedCam()     

    """
      A free Floating utility function for layout and camera artists 
      Makes the tear off tool from default maya more usable by putting it into a function, 
      also automatically locks the camera aswell as turning on the film and resolution gate
          Reasoning for this  it forces the artist to make a concious decision to make the camera movable, in contrast to mayas default behaviour that encourages ruining your already setup shot
      these last aids can be turned off by changing furtherAids = True to furtherAids = False
      TODO currently only works if the main viewport is selected when executing the script
    """
    def tearOffCopyOfSelectedCam(furtherAids = True):
        selected = cmds.ls(sl=True,long=True) or []
        if len(selected) > 0:
            for sel in selected:
                elementCleaned = sel[1:];
                cmds.lookThru( elementCleaned );
                viewport = cmds.playblast(ae=True);
                activePanel = viewport.split('|')[-1];
                #cmds.setFocus(activePanel)
                tempPanel = cmds.modelPanel(tearOffCopy=activePanel);
                if furtherAids:
                    cmds.camera( sel, e=True, displayResolution = True, displayFilmGate = True, displayGateMask = True, lockTransform = True);
                cmds.lookThru( 'persp' );