###################################################
# Copyright 2024 by Philip Wersonig. All Rights Reserved.
###################################################


"""
 Drag and drop for Maya 2018+
"""

"""
 Base Imports
"""
import os
import sys
from src.RDCL_Master_Module.scripts import rdcl_utils


"""
 Check if execution environment is Maya
"""
try:
    import maya.mel as mel
    import maya.cmds as cmds
    isMaya = True
except ImportError:
    isMaya = False

"""
 Execute on drag and drop python
"""
def onMayaDroppedPythonFile(*args, **kwargs):
    """ This function is only supported since Maya 2017 Update 3 """
    pass
"""
 Execute on drag and drop 
"""
def _onMayaDropped():
    """
     Initalize Path referencing
    """
    userDirPath = mel.eval('getenv MAYA_APP_DIR')
    srcPath = os.path.join(os.path.dirname(__file__), 'src')
    shelfPath = os.path.join(srcPath, 'RDCL_Master_Module', 'resource', 'shelves').replace('\\', '/')
    mayaModulePath = os.path.join(userDirPath,'modules').replace('\\', '/')
    rdclModulePath = os.path.join(srcPath, 'RDCL_Master_Module').replace('\\', '/')
    supportLibraryPath = os.path.join(srcPath, 'RDCL_Master_Module', 'resource', 'libraries').replace('\\', '/')
    
    if not os.path.exists(shelfPath):
        raise IOError('Cannot find ' + shelfPath)

    for path in sys.path:
        if os.path.exists(path + '/RDCL_Master/__init__.py'):
            maya.cmds.warning('The to be installed library is already installed at ' + path)
    """
     Setup Library Referencing
    """
    version = rdcl_utils.version()
    if not os.path.exists(mayaModulePath):
        os.makedirs(mayaModulePath)
    modPath = mayaModulePath + "/rdcl_master.mod"
    with open(modPath, 'wt') as output:
        output.write('+ rdcl_master ' + version + ' ' + rdclModulePath)
        output.write('\n+ rdcl_master_libraries ' + version + ' ' + supportLibraryPath)
    """
     Setup Library Shelf
    """
    if os.path.isdir(shelfPath) and not cmds.about(batch=True):
        for shelf in os.listdir(shelfPath):
            path = os.path.join(shelfPath, shelf).replace('\\', '/')
            if not os.path.isfile(path): continue
            name = os.path.splitext(shelf)[0].replace('shelf_', '')
            # Delete existing shelf before loading
            if cmds.shelfLayout(name, exists=True):
                cmds.deleteUI(name)
                mel.eval('loadNewShelf("{}")'.format(path))
            else:
                mel.eval('loadNewShelf("{}")'.format(path))
    
    cmds.confirmDialog(
        title='RDCL_Master',
        message='Shelf and Buttons setup, Please restart Maya to see the shelf.',
    )
    print('Shelf and Buttons setup, Please restart Maya to see the shelf.')


"""
 Execute
"""
if isMaya:
    _onMayaDropped()
