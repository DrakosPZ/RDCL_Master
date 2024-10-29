import maya.cmds as cmds
import mtoa.aovs as aovs;
import pymel.core as pmc;
from functools import partial;
import maya.app.renderSetup.views.overrideUtils as utils;
import maya.app.renderSetup.model.renderSetup as renderSetup;
import mtoa.ui.arnoldmenu;
import pyperclip
import rdcl_utils as pwUtils;

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