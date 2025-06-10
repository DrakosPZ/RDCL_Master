##########################################################
#   Written by PhilipW./Rauhm, usable under CCLicense-2024
#             just name me as Tech Support
##########################################################


##########################################################
# library import
##########################################################

import maya.cmds as cmds
import rdcl_utils as pwUtils;

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

class PW_BetterScenePlayblast(): 
    #constructor
    def __init__(self):
        self.defaultCams = ['|persp','|top','|side','|front',]
        self.shotSeperator = '_'
        self.addSceneName = True
        self.scenePlayBlast()     

    """
      A Function that playblasts all cameras in the scene, intended for Previs usage and rapid 
      placement and setting up of shots inside the same environment/ scene
        Note: 
            It expects the cameras to be named in a specific pattern => <Name>_<startFrame>_<endFrame> i.e. Shot1_0_230
            NO OTHER TRANSFORM OR OBJECT MUST BE NAMED WITH A _ CHARACTER

            It Further more handles multiple Shots in the same file by checking if the camera is located in a transform group with its name:
            ie: 
                Shot1 -> test -> test -> Shot1_0_230
            If this is the case it will additionally unhide this transform and hide it afterwards again.
            The intention is that objects that change inbetween shots, are hidden/placed within these groups to hide them from other shots
            Without having to switch between files and setting up the entire environment all over again
    """
    def scenePlayBlast(self):
        #prep cameras
        cameras = cmds.ls(type=('camera'), l=True) or []
        cleanedCameras = []
        for camera in cameras:
            cleanedCameras.append(pwUtils.removeShapeRef(camera))
        cleanedCameras = [camera for camera in cleanedCameras if camera not in self.defaultCams]
        #prep scene for Playblast
        for camera in cleanedCameras:
            pbInstruction = self.digestRef(camera)
            shotTransform = ''
            shotgroup = False
            fileName = pbInstruction[0][0]
            cameraName = pbInstruction[0][0] + '_' + pbInstruction[0][1] + '_' + pbInstruction[0][2]
            startFrame = pbInstruction[0][1]
            endFrame = pbInstruction[0][2]
                
            #check if right values otherwise skip
            if len(fileName) > 0 and startFrame.isdigit() and endFrame.isdigit() : 
                if len(pbInstruction[1]) > 0:
                    shotgroup = True
                    shotTransform = pbInstruction[1]
                if self.addSceneName == True:
                    mayaFileName = pwUtils.getMayaFile()
                    fileName = mayaFileName + '_' + fileName
                if shotgroup == True:
                    cmds.showHidden(shotTransform)
                cmds.lookThru(cameraName)
                pwUtils.playBlast(startFrame, endFrame, "movies\\", fileName)
                if shotgroup == True:
                    cmds.hide(shotTransform)
    
    def digestRef(self, ref):
        groupName = ''
        shotPrep = ()
        splitRef = ref.split('|')
        #check for empties
        if len(splitRef) > 1:
            shotPrep = self.prepCameraRef(splitRef[len(splitRef) - 1])
            for refCount in range(len(splitRef) - 1):
                refPath = splitRef[refCount]
                # Check if some transform above has the exact same name = my previs shot behaviour
                if shotPrep[0] in refPath:
                    groupName = refPath
        else:
            return ((), groupName) # something is wrong, remove camera from operation
        
        return (shotPrep, groupName)

    def prepCameraRef(self, ref):
        try:
            refData = ref.split(self.shotSeperator)
            name = refData[0]
            if(len(refData) > 1):
                startFrame = refData[1]
                endFrame = refData[2]
            return (name, startFrame, endFrame)
        except:
            print('Something went wrong, check the names of your cameras')