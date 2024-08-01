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
      A free Floating utility function fro layouting adn camera artists 
      Makes the tear off tool from default maya mroe usable by putting it into a function, 
      also automatically locks the camera aswell as turning on the film and resolution gate
          Reasoning for this  it forces the artist to make a concious decision to make the camera movable, in contrast to mayas default behaviour that encourages ruining your already setup shot
      these last aids can be turned of by changing furtherAids = True to furtherAids = False
    """
    def tearOffCopyOfSelectedCam(furtherAids = True):
        selected = cmds.ls(sl=True,long=True) or []
        if len(selected) > 0:
            for sel in selected:
               elementCleaned = sel[1:]
               cmds.lookThru( elementCleaned )
               viewport = cmds.playblast(ae=True)
               focus = cmds.getPanel(withFocus=True)
               tempPanel = cmds.modelPanel(tearOff=True)
               if furtherAids:
                   cmds.camera( sel, e=True, displayResolution = True, displayFilmGate = True, displayGateMask = True, lockTransform = True)
               cmds.lookThru( 'persp' )