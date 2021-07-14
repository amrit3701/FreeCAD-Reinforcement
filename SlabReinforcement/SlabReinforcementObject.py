# -*- coding: utf-8 -*-
# ***************************************************************************
# *                                                                         *
# *   Copyright (c) 2021 - Shiv Charan <shivcharanmt@gmail.com>             *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU Lesser General Public License (LGPL)    *
# *   as published by the Free Software Foundation; either version 2 of     *
# *   the License, or (at your option) any later version.                   *
# *   for detail see the LICENCE text file.                                 *
# *                                                                         *
# *   This program is distributed in the hope that it will be useful,       *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU Library General Public License for more details.                  *
# *                                                                         *
# *   You should have received a copy of the GNU Library General Public     *
# *   License along with this program; if not, write to the Free Software   *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *   USA                                                                   *
# *                                                                         *
# ***************************************************************************

__title__ = "Slab Reinforcement Group"
__author__ = "Shiv Charan"
__url__ = "https://www.freecadweb.org"

import FreeCAD
from RebarData import RebarTypes
from PySide2.QtCore import QT_TRANSLATE_NOOP
from Rebarfunc import (
    getFacenamesforBeamReinforcement,
    getParametersOfFace,
    get_rebar_amount_from_spacing,
)
from StraightRebar import makeStraightRebar, editStraightRebar
from UShapeRebar import makeUShapeRebar, editUShapeRebar
from BentShapeRebar import makeBentShapeRebar, editBentShapeRebar
from LShapeRebar import makeLShapeRebar, editLShapeRebar


class SlabReinforcementGroup:
    """A Slab Reinforcement Group object."""

    def __init__(self, obj_name="SlabReinforcement"):
        rebar_group = FreeCAD.ActiveDocument.addObject(
            "App::DocumentObjectGroupPython", obj_name
        )
        self.setProperties(rebar_group)
        self.Object = rebar_group
        rebar_group.Proxy = self

    def setProperties(self, obj):
        """Add properties to SlabReinforcementGroup object."""
        self.Type = "SlabReinforcementGroup"

        if not hasattr(obj, "MeshCoverAlong"):
            obj.addProperty(
                "App::PropertyEnumeration",
                "MeshCoverAlong",
                "SlabReinforcementGroup",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Mesh Cover Along for slab reinforcement",
                ),
            ).MeshCoverAlong = ["Bottom", "Top"]
            obj.MeshCoverAlong = "Bottom"

        if not hasattr(obj, "Facename"):
            obj.addProperty(
                "App::PropertyString",
                "Facename",
                "SlabReinforcementGroup",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Facename",
                ),
            )

        if not hasattr(obj, "Structure"):
            obj.addProperty(
                "App::PropertyLink",
                "Structure",
                "SlabReinforcementGroup",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Structure",
                ),
            )

        if not hasattr(obj, "ParallelRebars"):
            obj.addProperty(
                "App::PropertyLinkList",
                "ParallelRebars",
                "ParallelRebars",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Parallel Rebars",
                ),
            )
            obj.ParallelRebars = []
        obj.setEditorMode("ParallelRebars", 2)

        if not hasattr(obj, "ParallelDistributionRebars"):
            obj.addProperty(
                "App::PropertyLinkList",
                "ParallelDistributionRebars",
                "ParallelRebars",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Parallel Distribution Rebars",
                ),
            )
            obj.ParallelDistributionRebars = []
        obj.setEditorMode("ParallelDistributionRebars", 2)

        if not hasattr(obj, "CrossDistributionRebars"):
            obj.addProperty(
                "App::PropertyLinkList",
                "CrossDistributionRebars",
                "CrossRebars",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Cross Distribution Rebars",
                ),
            )
            obj.CrossDistributionRebars = []
        obj.setEditorMode("CrossDistributionRebars", 2)

        if not hasattr(obj, "CrossRebars"):
            obj.addProperty(
                "App::PropertyLinkList",
                "CrossRebars",
                "CrossRebars",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Cross Rebars",
                ),
            )
            obj.CrossRebars = []
        obj.setEditorMode("CrossRebars", 2)

        # parallel rebars properties
        if not hasattr(obj, "ParallelRebarType"):
            obj.addProperty(
                "App::PropertyEnumeration",
                "ParallelRebarType",
                "ParallelRebars",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Rebar Type for parallel rebars",
                ),
            ).ParallelRebarType = [
                "StraightRebar",
                "LShapeRebar",
                "UShapeRebar",
                "BentShapeRebar",
            ]
            obj.ParallelRebarType = "StraightRebar"

        if not hasattr(obj, "ParallelFrontCover"):
            obj.addProperty(
                "App::PropertyDistance",
                "ParallelFrontCover",
                "ParallelRebars",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Front Cover for parallel rebars",
                ),
            )
            obj.ParallelFrontCover = 20

        if not hasattr(obj, "ParallelRearCover"):
            obj.addProperty(
                "App::PropertyDistance",
                "ParallelRearCover",
                "ParallelRebars",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Rear Cover for parallel rebars",
                ),
            )
            obj.ParallelRearCover = 20

        if not hasattr(obj, "ParallelLeftCover"):
            obj.addProperty(
                "App::PropertyDistance",
                "ParallelLeftCover",
                "ParallelRebars",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Left Cover for parallel rebars",
                ),
            )
            obj.ParallelLeftCover = 20

        if not hasattr(obj, "ParallelRightCover"):
            obj.addProperty(
                "App::PropertyDistance",
                "ParallelRightCover",
                "ParallelRebars",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Right Cover for parallel rebars",
                ),
            )
            obj.ParallelRightCover = 20

        if not hasattr(obj, "ParallelTopCover"):
            obj.addProperty(
                "App::PropertyDistance",
                "ParallelTopCover",
                "ParallelRebars",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Top Cover for parallel rebars",
                ),
            )
            obj.ParallelTopCover = 20

        if not hasattr(obj, "ParallelBottomCover"):
            obj.addProperty(
                "App::PropertyDistance",
                "ParallelBottomCover",
                "ParallelRebars",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Bottom Cover for parallel rebars",
                ),
            )
            obj.ParallelBottomCover = 20

        if not hasattr(obj, "ParallelDiameter"):
            obj.addProperty(
                "App::PropertyDistance",
                "ParallelDiameter",
                "ParallelRebars",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Diameter for parallel rebars",
                ),
            )
            obj.ParallelDiameter = 8

        if not hasattr(obj, "ParallelAmountSpacingCheck"):
            obj.addProperty(
                "App::PropertyBool",
                "ParallelAmountSpacingCheck",
                "ParallelRebars",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Amount or Spacing Check for parallel rebars",
                ),
            )
            obj.ParallelAmountSpacingCheck = True

        if not hasattr(obj, "ParallelAmountValue"):
            obj.addProperty(
                "App::PropertyInteger",
                "ParallelAmountValue",
                "ParallelRebars",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Rebar's Amount Value for parallel rebars",
                ),
            )
            obj.ParallelAmountValue = 3

        if not hasattr(obj, "ParallelSpacingValue"):
            obj.addProperty(
                "App::PropertyDistance",
                "ParallelSpacingValue",
                "ParallelRebars",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Spacing Value for parallel rebars",
                ),
            )
            obj.ParallelSpacingValue = 50

        if not hasattr(obj, "ParallelRounding"):
            obj.addProperty(
                "App::PropertyInteger",
                "ParallelRounding",
                "ParallelRebars",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Rounding for parallel rebars",
                ),
            )
            obj.ParallelRounding = 2

        if not hasattr(obj, "ParallelBentBarLength"):
            obj.addProperty(
                "App::PropertyDistance",
                "ParallelBentBarLength",
                "ParallelRebars",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Bent Bar Length for parallel bent shape rebars",
                ),
            )
            obj.ParallelBentBarLength = 50

        if not hasattr(obj, "ParallelBentBarAngle"):
            obj.addProperty(
                "App::PropertyInteger",
                "ParallelBentBarAngle",
                "ParallelRebars",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Bent Bar Angle for parallel bent shape rebars",
                ),
            )
            obj.ParallelBentBarAngle = 135

        if not hasattr(obj, "ParallelLShapeHookOrintation"):
            obj.addProperty(
                "App::PropertyEnumeration",
                "ParallelLShapeHookOrintation",
                "ParallelRebars",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "L-Shape Hook Orintation for parallel L-Shape rebars",
                ),
            ).ParallelLShapeHookOrintation = ["Left", "Right", "Alternate"]
            obj.ParallelLShapeHookOrintation = "Left"

        if not hasattr(obj, "ParallelDistributionRebarsCheck"):
            obj.addProperty(
                "App::PropertyBool",
                "ParallelDistributionRebarsCheck",
                "ParallelRebars",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Distribution Rebars Check for parallel distribution rebars",
                ),
            )
            obj.ParallelDistributionRebarsCheck = False

        if not hasattr(obj, "ParallelDistributionRebarsDiameter"):
            obj.addProperty(
                "App::PropertyDistance",
                "ParallelDistributionRebarsDiameter",
                "ParallelRebars",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Diameter for parallel distribution rebars",
                ),
            )
            obj.ParallelDistributionRebarsDiameter = 8

        if not hasattr(obj, "ParallelDistributionRebarsAmountSpacingCheck"):
            obj.addProperty(
                "App::PropertyBool",
                "ParallelDistributionRebarsAmountSpacingCheck",
                "ParallelRebars",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Amount or Spacing Check for parallel distribution rebars",
                ),
            )
            obj.ParallelDistributionRebarsAmountSpacingCheck = True

        if not hasattr(obj, "ParallelDistributionRebarsAmount"):
            obj.addProperty(
                "App::PropertyInteger",
                "ParallelDistributionRebarsAmount",
                "ParallelRebars",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Rebar's amount for parallel distribution rebars",
                ),
            )
            obj.ParallelDistributionRebarsAmount = 2

        if not hasattr(obj, "ParallelDistributionRebarsSpacing"):
            obj.addProperty(
                "App::PropertyDistance",
                "ParallelDistributionRebarsSpacing",
                "ParallelRebars",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Rebars Spacing for parallel distribution rebars",
                ),
            )
            obj.ParallelDistributionRebarsSpacing = 20

        # cross rebars properties
        if not hasattr(obj, "CrossRebarType"):
            obj.addProperty(
                "App::PropertyEnumeration",
                "CrossRebarType",
                "CrossRebars",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Rebar Type for cross rebars",
                ),
            ).CrossRebarType = [
                "StraightRebar",
                "LShapeRebar",
                "UShapeRebar",
                "BentShapeRebar",
            ]
            obj.CrossRebarType = "StraightRebar"

        if not hasattr(obj, "CrossFrontCover"):
            obj.addProperty(
                "App::PropertyDistance",
                "CrossFrontCover",
                "CrossRebars",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Front Cover for cross rebars",
                ),
            )
            obj.CrossFrontCover = 20

        if not hasattr(obj, "CrossRearCover"):
            obj.addProperty(
                "App::PropertyDistance",
                "CrossRearCover",
                "CrossRebars",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Rear Cover for cross rebars",
                ),
            )
            obj.CrossRearCover = 20

        if not hasattr(obj, "CrossLeftCover"):
            obj.addProperty(
                "App::PropertyDistance",
                "CrossLeftCover",
                "CrossRebars",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Left Cover for cross rebars",
                ),
            )
            obj.CrossLeftCover = 20

        if not hasattr(obj, "CrossRightCover"):
            obj.addProperty(
                "App::PropertyDistance",
                "CrossRightCover",
                "CrossRebars",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Right Cover for cross rebars",
                ),
            )
            obj.CrossRightCover = 20

        if not hasattr(obj, "CrossTopCover"):
            obj.addProperty(
                "App::PropertyDistance",
                "CrossTopCover",
                "CrossRebars",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Top Cover for cross rebars",
                ),
            )
            obj.CrossTopCover = 20

        if not hasattr(obj, "CrossBottomCover"):
            obj.addProperty(
                "App::PropertyDistance",
                "CrossBottomCover",
                "CrossRebars",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Bottom Cover for cross rebars",
                ),
            )
            obj.CrossBottomCover = 20

        if not hasattr(obj, "CrossDiameter"):
            obj.addProperty(
                "App::PropertyDistance",
                "CrossDiameter",
                "CrossRebars",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Diameter for cross rebars",
                ),
            )
            obj.CrossDiameter = 8

        if not hasattr(obj, "CrossAmountSpacingCheck"):
            obj.addProperty(
                "App::PropertyBool",
                "CrossAmountSpacingCheck",
                "CrossRebars",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Amount or Spacing Check for cross rebars",
                ),
            )
            obj.CrossAmountSpacingCheck = True

        if not hasattr(obj, "CrossAmountValue"):
            obj.addProperty(
                "App::PropertyInteger",
                "CrossAmountValue",
                "CrossRebars",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Rebar's Amount Value for cross rebars",
                ),
            )
            obj.CrossAmountValue = 3

        if not hasattr(obj, "CrossSpacingValue"):
            obj.addProperty(
                "App::PropertyDistance",
                "CrossSpacingValue",
                "CrossRebars",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Spacing Value for cross rebars",
                ),
            )
            obj.CrossSpacingValue = 50

        if not hasattr(obj, "CrossRounding"):
            obj.addProperty(
                "App::PropertyInteger",
                "CrossRounding",
                "CrossRebars",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Rounding for cross rebars",
                ),
            )
            obj.CrossRounding = 2

        if not hasattr(obj, "CrossBentBarLength"):
            obj.addProperty(
                "App::PropertyDistance",
                "CrossBentBarLength",
                "CrossRebars",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Bent Bar Length for cross bent shape rebars",
                ),
            )
            obj.CrossBentBarLength = 50

        if not hasattr(obj, "CrossBentBarAngle"):
            obj.addProperty(
                "App::PropertyInteger",
                "CrossBentBarAngle",
                "CrossRebars",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Bent Bar Angle for cross bent shape rebars",
                ),
            )
            obj.CrossBentBarAngle = 135

        if not hasattr(obj, "CrossLShapeHookOrintation"):
            obj.addProperty(
                "App::PropertyEnumeration",
                "CrossLShapeHookOrintation",
                "CrossRebars",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "L-Shape Hook Orintation for cross L-Shape rebars",
                ),
            ).CrossLShapeHookOrintation = ["Left", "Right", "Alternate"]
            obj.CrossLShapeHookOrintation = "Left"

        if not hasattr(obj, "CrossDistributionRebarsCheck"):
            obj.addProperty(
                "App::PropertyBool",
                "CrossDistributionRebarsCheck",
                "CrossRebars",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Distribution Rebars check for cross distribution rebars",
                ),
            )
            obj.CrossDistributionRebarsCheck = False

        if not hasattr(obj, "CrossDistributionRebarsDiameter"):
            obj.addProperty(
                "App::PropertyDistance",
                "CrossDistributionRebarsDiameter",
                "CrossRebars",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Rebars Diameter for cross distribution rebars",
                ),
            )
            obj.CrossDistributionRebarsDiameter = 8

        if not hasattr(obj, "CrossDistributionRebarsAmountSpacingCheck"):
            obj.addProperty(
                "App::PropertyBool",
                "CrossDistributionRebarsAmountSpacingCheck",
                "CrossRebars",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Amount or Spacing check for cross distribution rebars",
                ),
            )
            obj.CrossDistributionRebarsAmountSpacingCheck = True

        if not hasattr(obj, "CrossDistributionRebarsAmount"):
            obj.addProperty(
                "App::PropertyInteger",
                "CrossDistributionRebarsAmount",
                "CrossRebars",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Rebars amount for cross distribution rebars",
                ),
            )
            obj.CrossDistributionRebarsAmount = 2

        if not hasattr(obj, "CrossDistributionRebarsSpacing"):
            obj.addProperty(
                "App::PropertyDistance",
                "CrossDistributionRebarsSpacing",
                "CrossRebars",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Spacing value for cross distribution rebars",
                ),
            )
            obj.CrossDistributionRebarsSpacing = 20

        if not hasattr(obj, "IsMakeOrEditRequired"):
            obj.addProperty(
                "App::PropertyBool",
                "IsMakeOrEditRequired",
                "SlabReinforcementGroup",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Check if make or update required for slab reinforcement",
                ),
            )
            obj.IsMakeOrEditRequired = False
            obj.setEditorMode("IsMakeOrEditRequired", 2)

    def onChanged(self, obj, prop):
        """
        This will update editor mode of properties
        based on rebar type and/or trigger create/update
        Slab Reinforcement
        """
        if (
            prop == "ParallelRebarType"
            or prop == "ParallelDistributionRebarsCheck"
        ):
            if obj.ParallelRebarType == RebarTypes.straight:
                obj.setEditorMode("ParallelRounding", 2)
                obj.setEditorMode("ParallelBentBarLength", 2)
                obj.setEditorMode("ParallelBentBarAngle", 2)
                obj.setEditorMode("ParallelLShapeHookOrintation", 2)
                obj.setEditorMode("ParallelDistributionRebarsCheck", 2)
                obj.setEditorMode("ParallelDistributionRebarsDiameter", 2)
                obj.setEditorMode(
                    "ParallelDistributionRebarsAmountSpacingCheck", 2
                )
                obj.setEditorMode("ParallelDistributionRebarsAmount", 2)
                obj.setEditorMode("ParallelDistributionRebarsSpacing", 2)
            elif obj.ParallelRebarType == RebarTypes.lshape:
                obj.setEditorMode("ParallelLShapeHookOrintation", 0)
                obj.setEditorMode("ParallelRounding", 0)
                obj.setEditorMode("ParallelBentBarLength", 2)
                obj.setEditorMode("ParallelBentBarAngle", 2)
                obj.setEditorMode("ParallelDistributionRebarsCheck", 2)
                obj.setEditorMode("ParallelDistributionRebarsDiameter", 2)
                obj.setEditorMode(
                    "ParallelDistributionRebarsAmountSpacingCheck", 2
                )
                obj.setEditorMode("ParallelDistributionRebarsAmount", 2)
                obj.setEditorMode("ParallelDistributionRebarsSpacing", 2)
            elif obj.ParallelRebarType == RebarTypes.ushape:
                obj.setEditorMode("ParallelRounding", 0)
                obj.setEditorMode("ParallelBentBarLength", 2)
                obj.setEditorMode("ParallelLShapeHookOrintation", 2)
                obj.setEditorMode("ParallelBentBarAngle", 2)
                obj.setEditorMode("ParallelDistributionRebarsCheck", 2)
                obj.setEditorMode("ParallelDistributionRebarsDiameter", 2)
                obj.setEditorMode(
                    "ParallelDistributionRebarsAmountSpacingCheck", 2
                )
                obj.setEditorMode("ParallelDistributionRebarsAmount", 2)
                obj.setEditorMode("ParallelDistributionRebarsSpacing", 2)
            elif obj.ParallelRebarType == RebarTypes.bentshape:
                obj.setEditorMode("ParallelRounding", 0)
                obj.setEditorMode("ParallelBentBarLength", 0)
                obj.setEditorMode("ParallelBentBarAngle", 0)
                obj.setEditorMode("ParallelLShapeHookOrintation", 2)
                obj.setEditorMode("ParallelDistributionRebarsCheck", 0)
                if obj.ParallelDistributionRebarsCheck:
                    obj.setEditorMode("ParallelDistributionRebarsDiameter", 0)
                    obj.setEditorMode(
                        "ParallelDistributionRebarsAmountSpacingCheck", 0
                    )
                    obj.setEditorMode("ParallelDistributionRebarsAmount", 0)
                    obj.setEditorMode("ParallelDistributionRebarsSpacing", 0)
                else:
                    obj.setEditorMode("ParallelDistributionRebarsDiameter", 2)
                    obj.setEditorMode(
                        "ParallelDistributionRebarsAmountSpacingCheck", 2
                    )
                    obj.setEditorMode("ParallelDistributionRebarsAmount", 2)
                    obj.setEditorMode("ParallelDistributionRebarsSpacing", 2)

        if prop == "CrossRebarType" or prop == "CrossDistributionRebarsCheck":
            if obj.CrossRebarType == RebarTypes.straight:
                obj.setEditorMode("CrossRounding", 2)
                obj.setEditorMode("CrossBentBarLength", 2)
                obj.setEditorMode("CrossBentBarAngle", 2)
                obj.setEditorMode("CrossLShapeHookOrintation", 2)
                obj.setEditorMode("CrossDistributionRebarsCheck", 2)
                obj.setEditorMode("CrossDistributionRebarsDiameter", 2)
                obj.setEditorMode(
                    "CrossDistributionRebarsAmountSpacingCheck", 2
                )
                obj.setEditorMode("CrossDistributionRebarsAmount", 2)
                obj.setEditorMode("CrossDistributionRebarsSpacing", 2)
            elif obj.CrossRebarType == RebarTypes.lshape:
                obj.setEditorMode("CrossLShapeHookOrintation", 0)
                obj.setEditorMode("CrossRounding", 0)
                obj.setEditorMode("CrossBentBarLength", 2)
                obj.setEditorMode("CrossBentBarAngle", 2)
                obj.setEditorMode("CrossDistributionRebarsCheck", 2)
                obj.setEditorMode("CrossDistributionRebarsDiameter", 2)
                obj.setEditorMode(
                    "CrossDistributionRebarsAmountSpacingCheck", 2
                )
                obj.setEditorMode("CrossDistributionRebarsAmount", 2)
                obj.setEditorMode("CrossDistributionRebarsSpacing", 2)
            elif obj.CrossRebarType == RebarTypes.ushape:
                obj.setEditorMode("CrossRounding", 0)
                obj.setEditorMode("CrossBentBarLength", 2)
                obj.setEditorMode("CrossLShapeHookOrintation", 2)
                obj.setEditorMode("CrossBentBarAngle", 2)
                obj.setEditorMode("CrossDistributionRebarsCheck", 2)
                obj.setEditorMode("CrossDistributionRebarsDiameter", 2)
                obj.setEditorMode(
                    "CrossDistributionRebarsAmountSpacingCheck", 2
                )
                obj.setEditorMode("CrossDistributionRebarsAmount", 2)
                obj.setEditorMode("CrossDistributionRebarsSpacing", 2)
            elif obj.CrossRebarType == RebarTypes.bentshape:
                obj.setEditorMode("CrossRounding", 0)
                obj.setEditorMode("CrossBentBarLength", 0)
                obj.setEditorMode("CrossBentBarAngle", 0)
                obj.setEditorMode("CrossLShapeHookOrintation", 2)
                obj.setEditorMode("CrossDistributionRebarsCheck", 0)
                if obj.CrossDistributionRebarsCheck:
                    obj.setEditorMode("CrossDistributionRebarsDiameter", 0)
                    obj.setEditorMode(
                        "CrossDistributionRebarsAmountSpacingCheck", 0
                    )
                    obj.setEditorMode("CrossDistributionRebarsAmount", 0)
                    obj.setEditorMode("CrossDistributionRebarsSpacing", 0)
                else:
                    obj.setEditorMode("CrossDistributionRebarsDiameter", 2)
                    obj.setEditorMode(
                        "CrossDistributionRebarsAmountSpacingCheck", 2
                    )
                    obj.setEditorMode("CrossDistributionRebarsAmount", 2)
                    obj.setEditorMode("CrossDistributionRebarsSpacing", 2)

        if prop != "IsMakeOrEditRequired" and obj.IsMakeOrEditRequired:
            obj.IsMakeOrEditRequired = False
            self.makeOrEditSlabReinforcement(obj)
            obj.IsMakeOrEditRequired = True

    def execute(self, obj):
        pass

    def makeOrEditSlabReinforcement(self, obj):
        """Create or update Slab Reinforcement"""
        mesh_cover_along = obj.MeshCoverAlong
        structure = obj.Structure
        facename = obj.Facename
        parallel_rebar_type = obj.ParallelRebarType
        parallel_front_cover = FreeCAD.Units.Quantity(
            obj.ParallelFrontCover
        ).Value
        parallel_left_cover = FreeCAD.Units.Quantity(
            obj.ParallelLeftCover
        ).Value
        parallel_right_cover = FreeCAD.Units.Quantity(
            obj.ParallelRightCover
        ).Value
        parallel_rear_cover = FreeCAD.Units.Quantity(
            obj.ParallelRearCover
        ).Value
        parallel_top_cover = FreeCAD.Units.Quantity(obj.ParallelTopCover).Value
        parallel_bottom_cover = FreeCAD.Units.Quantity(
            obj.ParallelBottomCover
        ).Value
        parallel_diameter = FreeCAD.Units.Quantity(obj.ParallelDiameter).Value
        parallel_amount_spacing_check = obj.ParallelAmountSpacingCheck
        if parallel_amount_spacing_check:
            parallel_amount_spacing_value = obj.ParallelAmountValue
        else:
            parallel_amount_spacing_value = FreeCAD.Units.Quantity(
                obj.ParallelSpacingValue
            ).Value
        parallel_rounding = obj.ParallelRounding
        parallel_bent_bar_length = FreeCAD.Units.Quantity(
            obj.ParallelBentBarLength
        ).Value
        parallel_bent_bar_angle = obj.ParallelBentBarAngle
        parallel_l_shape_hook_orintation = obj.ParallelLShapeHookOrintation
        parallel_distribution_rebars_check = obj.ParallelDistributionRebarsCheck
        parallel_distribution_rebars_diameter = FreeCAD.Units.Quantity(
            obj.ParallelDistributionRebarsDiameter
        ).Value
        parallel_distribution_rebars_amount_spacing_check = (
            obj.ParallelDistributionRebarsAmountSpacingCheck
        )
        if parallel_distribution_rebars_amount_spacing_check:
            parallel_distribution_rebars_amount_spacing_value = (
                obj.ParallelDistributionRebarsAmount
            )
        else:
            parallel_distribution_rebars_amount_spacing_value = (
                FreeCAD.Units.Quantity(
                    obj.ParallelDistributionRebarsSpacing
                ).Value
            )

        cross_rebar_type = obj.CrossRebarType
        cross_front_cover = FreeCAD.Units.Quantity(obj.CrossFrontCover).Value
        cross_left_cover = FreeCAD.Units.Quantity(obj.CrossLeftCover).Value
        cross_right_cover = FreeCAD.Units.Quantity(obj.CrossRightCover).Value
        cross_rear_cover = FreeCAD.Units.Quantity(obj.CrossRearCover).Value
        cross_top_cover = FreeCAD.Units.Quantity(obj.CrossTopCover).Value
        cross_bottom_cover = FreeCAD.Units.Quantity(obj.CrossBottomCover).Value
        cross_diameter = FreeCAD.Units.Quantity(obj.CrossDiameter).Value
        cross_amount_spacing_check = obj.CrossAmountSpacingCheck
        if cross_amount_spacing_check:
            cross_amount_spacing_value = obj.CrossAmountValue
        else:
            cross_amount_spacing_value = FreeCAD.Units.Quantity(
                obj.CrossSpacingValue
            ).Value
        cross_rounding = obj.CrossRounding
        cross_bent_bar_length = FreeCAD.Units.Quantity(
            obj.CrossBentBarLength
        ).Value
        cross_bent_bar_angle = obj.CrossBentBarAngle
        cross_l_shape_hook_orintation = obj.CrossLShapeHookOrintation
        cross_distribution_rebars_check = obj.CrossDistributionRebarsCheck
        cross_distribution_rebars_diameter = FreeCAD.Units.Quantity(
            obj.CrossDistributionRebarsDiameter
        ).Value
        cross_distribution_rebars_amount_spacing_check = (
            obj.CrossDistributionRebarsAmountSpacingCheck
        )
        if cross_distribution_rebars_amount_spacing_check:
            cross_distribution_rebars_amount_spacing_value = (
                obj.CrossDistributionRebarsAmount
            )
        else:
            cross_distribution_rebars_amount_spacing_value = (
                FreeCAD.Units.Quantity(obj.CrossDistributionRebarsSpacing).Value
            )

        # Remove old rebars if rebar type changed or rebar amount is zero
        if obj.ParallelRebars and (
            parallel_rebar_type != obj.ParallelRebars[0].RebarShape
            or not parallel_amount_spacing_value
        ):
            # Delete previously created rebars
            for Rebar in obj.ParallelRebars:
                base_name = Rebar.Base.Name
                FreeCAD.ActiveDocument.removeObject(Rebar.Name)
                FreeCAD.ActiveDocument.removeObject(base_name)

        if obj.CrossRebars and (
            cross_rebar_type != obj.CrossRebars[0].RebarShape
            or not cross_amount_spacing_value
        ):
            # Delete previously created rebars
            for Rebar in obj.CrossRebars:
                base_name = Rebar.Base.Name
                FreeCAD.ActiveDocument.removeObject(Rebar.Name)
                FreeCAD.ActiveDocument.removeObject(base_name)

        if obj.ParallelDistributionRebars and (
            not parallel_distribution_rebars_check
            or parallel_rebar_type != RebarTypes.bentshape
            or not parallel_distribution_rebars_amount_spacing_value
            or not parallel_amount_spacing_value
        ):
            # Delete previously created rebars
            for Rebar in obj.ParallelDistributionRebars:
                base_name = Rebar.Base.Name
                FreeCAD.ActiveDocument.removeObject(Rebar.Name)
                FreeCAD.ActiveDocument.removeObject(base_name)

        if obj.CrossDistributionRebars and (
            not cross_distribution_rebars_check
            or cross_rebar_type != RebarTypes.bentshape
            or not cross_distribution_rebars_amount_spacing_value
            or not cross_amount_spacing_value
        ):
            # Delete previously created rebars
            for Rebar in obj.CrossDistributionRebars:
                base_name = Rebar.Base.Name
                FreeCAD.ActiveDocument.removeObject(Rebar.Name)
                FreeCAD.ActiveDocument.removeObject(base_name)

        if (
            obj.ParallelRebars
            and parallel_rebar_type == RebarTypes.lshape
            and parallel_l_shape_hook_orintation != "Alternate"
        ):
            # Delete previously created rebars
            for Rebar in obj.ParallelRebars[1:]:
                base_name = Rebar.Base.Name
                FreeCAD.ActiveDocument.removeObject(Rebar.Name)
                FreeCAD.ActiveDocument.removeObject(base_name)

        if (
            obj.CrossRebars
            and cross_rebar_type == RebarTypes.lshape
            and cross_l_shape_hook_orintation != "Alternate"
        ):
            # Delete previously created rebars
            for Rebar in obj.CrossRebars[1:]:
                base_name = Rebar.Base.Name
                FreeCAD.ActiveDocument.removeObject(Rebar.Name)
                FreeCAD.ActiveDocument.removeObject(base_name)

        parallel_rebars = []
        cross_rebars = []
        parallel_distribution_rebars = []
        cross_distribution_rebars = []
        cross_facename = getFacenamesforBeamReinforcement(facename, structure)[
            0
        ]
        if (
            parallel_rebar_type == RebarTypes.straight
            and parallel_amount_spacing_value
        ):
            if not obj.ParallelRebars:
                # Create parallel Straight Rebars
                parallel_rebars = makeStraightRebar(
                    parallel_front_cover,
                    (
                        f"{mesh_cover_along} Side",
                        parallel_top_cover
                        if mesh_cover_along == "Top"
                        else parallel_bottom_cover,
                    ),
                    parallel_right_cover,
                    parallel_left_cover,
                    parallel_diameter,
                    parallel_amount_spacing_check,
                    parallel_amount_spacing_value,
                    "Horizontal",
                    structure,
                    facename,
                )
            else:
                # Update parallel Straight Rebars
                parallel_rebars = editStraightRebar(
                    obj.ParallelRebars[0],
                    parallel_front_cover,
                    (
                        f"{mesh_cover_along} Side",
                        parallel_top_cover
                        if mesh_cover_along == "Top"
                        else parallel_bottom_cover,
                    ),
                    parallel_right_cover,
                    parallel_left_cover,
                    parallel_diameter,
                    parallel_amount_spacing_check,
                    parallel_amount_spacing_value,
                    "Horizontal",
                    structure,
                    facename,
                )
            parallel_rebars.OffsetEnd = (
                parallel_rear_cover + parallel_diameter / 2
            )

        elif (
            parallel_rebar_type == RebarTypes.ushape
            and parallel_amount_spacing_value
        ):
            if not obj.ParallelRebars:
                # Create parallel U-Shape Rebars
                parallel_rebars = makeUShapeRebar(
                    parallel_front_cover,
                    parallel_bottom_cover,
                    parallel_right_cover,
                    parallel_left_cover,
                    parallel_diameter,
                    parallel_top_cover,
                    parallel_rounding,
                    parallel_amount_spacing_check,
                    parallel_amount_spacing_value,
                    mesh_cover_along,
                    structure,
                    facename,
                )
            else:
                # Update parallel U-Shape Rebars
                parallel_rebars = editUShapeRebar(
                    obj.ParallelRebars[0],
                    parallel_front_cover,
                    parallel_bottom_cover,
                    parallel_right_cover,
                    parallel_left_cover,
                    parallel_diameter,
                    parallel_top_cover,
                    parallel_rounding,
                    parallel_amount_spacing_check,
                    parallel_amount_spacing_value,
                    mesh_cover_along,
                    structure,
                    facename,
                )
            parallel_rebars.OffsetEnd = (
                parallel_rear_cover + parallel_diameter / 2
            )

        elif (
            parallel_rebar_type == RebarTypes.bentshape
            and parallel_amount_spacing_value
        ):
            if not obj.ParallelRebars:
                # Create parallel Bent Shape Rebars
                parallel_rebars = makeBentShapeRebar(
                    parallel_front_cover,
                    parallel_bottom_cover,
                    parallel_left_cover,
                    parallel_right_cover,
                    parallel_diameter,
                    parallel_top_cover,
                    parallel_bent_bar_length,
                    parallel_bent_bar_angle,
                    parallel_rounding,
                    parallel_amount_spacing_check,
                    parallel_amount_spacing_value,
                    mesh_cover_along,
                    structure,
                    facename,
                )
            else:
                # Update parallel Bent Shape Rebars
                parallel_rebars = editBentShapeRebar(
                    obj.ParallelRebars[0],
                    parallel_front_cover,
                    parallel_bottom_cover,
                    parallel_left_cover,
                    parallel_right_cover,
                    parallel_diameter,
                    parallel_top_cover,
                    parallel_bent_bar_length,
                    parallel_bent_bar_angle,
                    parallel_rounding,
                    parallel_amount_spacing_check,
                    parallel_amount_spacing_value,
                    mesh_cover_along,
                    structure,
                    facename,
                )
            parallel_rebars.OffsetEnd = (
                parallel_rear_cover + parallel_diameter / 2
            )

            if (
                parallel_distribution_rebars_check
                and parallel_distribution_rebars_amount_spacing_value
            ):
                parallel_face_length = getParametersOfFace(structure, facename)[
                    0
                ][0]
                cover_along_length = parallel_diameter + (
                    parallel_bottom_cover
                    if mesh_cover_along == "Top"
                    else parallel_top_cover
                )
                cover_along = (
                    "Top Side"
                    if mesh_cover_along == "Bottom"
                    else "Bottom Side"
                )
                parallel_distribution_rebars_amount = (
                    parallel_distribution_rebars_amount_spacing_value
                )
                if not parallel_distribution_rebars_amount_spacing_check:
                    # calculate distribution rebars amount based on length of
                    # arm of bent shape rebar and covers for distribution rebars
                    parallel_distribution_rebars_amount = (
                        get_rebar_amount_from_spacing(
                            parallel_bent_bar_length
                            + parallel_left_cover
                            - cross_front_cover
                            - cross_diameter
                            - parallel_diameter,
                            parallel_distribution_rebars_diameter,
                            parallel_distribution_rebars_amount_spacing_value,
                        )
                    )
                if not obj.ParallelDistributionRebars:
                    # Create left distribution rebars for parallel Bent Shape Rebars
                    parallel_left_distribution_rebars = makeStraightRebar(
                        cross_front_cover + cross_diameter,
                        (
                            cover_along,
                            cover_along_length,
                        ),
                        cross_right_cover,
                        cross_left_cover,
                        parallel_distribution_rebars_diameter,
                        True,
                        parallel_distribution_rebars_amount,
                        "Horizontal",
                        structure,
                        cross_facename,
                    )
                else:
                    # Update left distribution rebars for parallel Bent Shape Rebars
                    parallel_left_distribution_rebars = editStraightRebar(
                        obj.ParallelDistributionRebars[0],
                        cross_front_cover + cross_diameter,
                        (
                            cover_along,
                            cover_along_length,
                        ),
                        cross_right_cover,
                        cross_left_cover,
                        parallel_distribution_rebars_diameter,
                        True,
                        parallel_distribution_rebars_amount,
                        "Horizontal",
                        structure,
                        cross_facename,
                    )
                parallel_left_distribution_rebars.OffsetEnd = (
                    parallel_face_length
                    - parallel_bent_bar_length
                    - parallel_left_cover
                    + parallel_diameter
                    + parallel_distribution_rebars_diameter / 2
                )
                # calculate front cover for right side distribution rebars
                parallel_right_front_cover = (
                    parallel_face_length
                    - parallel_right_cover
                    - parallel_bent_bar_length
                    + parallel_diameter
                )

                if len(obj.ParallelDistributionRebars) < 2:
                    # Create Right distribution rebars for parallel Bent Shape Rebars
                    parallel_right_distribution_rebars = makeStraightRebar(
                        parallel_right_front_cover,
                        (
                            cover_along,
                            cover_along_length,
                        ),
                        cross_right_cover,
                        cross_left_cover,
                        parallel_distribution_rebars_diameter,
                        True,
                        parallel_distribution_rebars_amount,
                        "Horizontal",
                        structure,
                        cross_facename,
                    )
                else:
                    # Update Right distribution rebars for parallel Bent Shape Rebars
                    parallel_right_distribution_rebars = editStraightRebar(
                        obj.ParallelDistributionRebars[1],
                        parallel_right_front_cover,
                        (
                            cover_along,
                            cover_along_length,
                        ),
                        cross_right_cover,
                        cross_left_cover,
                        parallel_distribution_rebars_diameter,
                        True,
                        parallel_distribution_rebars_amount,
                        "Horizontal",
                        structure,
                        cross_facename,
                    )
                parallel_right_distribution_rebars.OffsetEnd = (
                    cross_rear_cover
                    + cross_diameter
                    + cross_distribution_rebars_diameter / 2
                )
                parallel_distribution_rebars = [
                    parallel_left_distribution_rebars,
                    parallel_right_distribution_rebars,
                ]

        elif (
            parallel_rebar_type == RebarTypes.lshape
            and parallel_amount_spacing_value
        ):

            if parallel_l_shape_hook_orintation == "Alternate":
                cross_face_length = getParametersOfFace(
                    structure, cross_facename
                )[0][0]

                # Get Amount of rebars from spacing value
                if not parallel_amount_spacing_check:
                    parallel_rebars_amount = get_rebar_amount_from_spacing(
                        cross_face_length,
                        parallel_diameter,
                        parallel_amount_spacing_value,
                    )
                else:
                    parallel_rebars_amount = parallel_amount_spacing_value

                # Rebars amount of parallel L-Shape rebars having Right hook orientation
                parallel_modified_amount_spacing_value_2 = (
                    parallel_rebars_amount // 2
                )
                # Rebars amount of parallel L-Shape rebars having Left hook orientation
                parallel_modified_amount_spacing_value_1 = (
                    parallel_rebars_amount
                    - parallel_modified_amount_spacing_value_2
                )
                if parallel_rebars_amount == 1:
                    parallel_interval = parallel_front_cover
                else:
                    parallel_interval = (
                        cross_face_length
                        - parallel_front_cover
                        - parallel_rear_cover
                    ) / (parallel_rebars_amount - 1)
                parallel_modified_front_cover = (
                    parallel_front_cover + parallel_interval
                )
                parallel_rebars = []
                if parallel_modified_amount_spacing_value_1:
                    if not obj.ParallelRebars:
                        # Create parallel L-Shape rebars having left hook orientation
                        parallel_left_rebars = makeLShapeRebar(
                            parallel_front_cover,
                            parallel_bottom_cover,
                            parallel_left_cover,
                            parallel_right_cover,
                            parallel_diameter,
                            parallel_top_cover,
                            parallel_rounding,
                            True,
                            parallel_modified_amount_spacing_value_1,
                            f"{mesh_cover_along} Left",
                            structure,
                            facename,
                        )
                    else:
                        # Update parallel L-Shape rebars having left hook orientation
                        parallel_left_rebars = editLShapeRebar(
                            obj.ParallelRebars[0],
                            parallel_front_cover,
                            parallel_bottom_cover,
                            parallel_left_cover,
                            parallel_right_cover,
                            parallel_diameter,
                            parallel_top_cover,
                            parallel_rounding,
                            True,
                            parallel_modified_amount_spacing_value_1,
                            f"{mesh_cover_along} Left",
                            structure,
                            facename,
                        )
                    parallel_left_rebars.OffsetEnd = (
                        parallel_rear_cover
                        + parallel_diameter / 2
                        + (
                            parallel_interval
                            if parallel_modified_amount_spacing_value_1
                            == parallel_modified_amount_spacing_value_2
                            else 0
                        )
                    )
                    parallel_rebars.append(parallel_left_rebars)

                if parallel_modified_amount_spacing_value_2:
                    if len(obj.ParallelRebars) < 2:
                        # Create parallel L-Shape rebars having right hook orientation
                        parallel_right_rebars = makeLShapeRebar(
                            parallel_modified_front_cover,
                            parallel_bottom_cover,
                            parallel_left_cover,
                            parallel_right_cover,
                            parallel_diameter,
                            parallel_top_cover,
                            parallel_rounding,
                            True,
                            parallel_modified_amount_spacing_value_2,
                            f"{mesh_cover_along} Right",
                            structure,
                            facename,
                        )
                    else:
                        # Update parallel L-Shape rebars having right hook orientation
                        parallel_right_rebars = editLShapeRebar(
                            obj.ParallelRebars[1],
                            parallel_modified_front_cover,
                            parallel_bottom_cover,
                            parallel_left_cover,
                            parallel_right_cover,
                            parallel_diameter,
                            parallel_top_cover,
                            parallel_rounding,
                            True,
                            parallel_modified_amount_spacing_value_2,
                            f"{mesh_cover_along} Right",
                            structure,
                            facename,
                        )
                    parallel_right_rebars.OffsetEnd = (
                        parallel_rear_cover
                        + parallel_diameter / 2
                        + (
                            parallel_interval
                            if (
                                parallel_modified_amount_spacing_value_1
                                - parallel_modified_amount_spacing_value_2
                            )
                            == 1
                            else 0
                        )
                    )
                    parallel_rebars.append(parallel_right_rebars)
                elif len(obj.ParallelRebars) >= 2:
                    # Deleting extra L-Shaped Rebars
                    for Rebar in obj.ParallelRebars[1:]:
                        base_name = Rebar.Base.Name
                        FreeCAD.ActiveDocument.removeObject(Rebar.Name)
                        FreeCAD.ActiveDocument.removeObject(base_name)

            else:
                if not obj.ParallelRebars:
                    # Create parallel L-Shape rebars
                    parallel_rebars = makeLShapeRebar(
                        parallel_front_cover,
                        parallel_bottom_cover,
                        parallel_left_cover,
                        parallel_right_cover,
                        parallel_diameter,
                        parallel_top_cover,
                        parallel_rounding,
                        True,
                        parallel_amount_spacing_value,
                        f"{mesh_cover_along} {parallel_l_shape_hook_orintation}",
                        structure,
                        facename,
                    )
                else:
                    # Update L-Shape rebars
                    parallel_rebars = editLShapeRebar(
                        obj.ParallelRebars[0],
                        parallel_front_cover,
                        parallel_bottom_cover,
                        parallel_left_cover,
                        parallel_right_cover,
                        parallel_diameter,
                        parallel_top_cover,
                        parallel_rounding,
                        True,
                        parallel_amount_spacing_value,
                        f"{mesh_cover_along} {parallel_l_shape_hook_orintation}",
                        structure,
                        facename,
                    )
                parallel_rebars.OffsetEnd = (
                    parallel_rear_cover + parallel_diameter / 2
                )

        if (
            cross_rebar_type == RebarTypes.straight
            and cross_amount_spacing_value
        ):
            if not obj.CrossRebars:
                # Create cross Straght Rebars
                cross_rebars = makeStraightRebar(
                    cross_front_cover,
                    (
                        f"{mesh_cover_along} Side",
                        cross_top_cover - parallel_diameter
                        if mesh_cover_along == "Top"
                        else cross_bottom_cover + parallel_diameter,
                    ),
                    cross_right_cover,
                    cross_left_cover,
                    cross_diameter,
                    cross_amount_spacing_check,
                    cross_amount_spacing_value,
                    "Horizontal",
                    structure,
                    cross_facename,
                )
            else:
                # Update cross Straght Rebars
                cross_rebars = editStraightRebar(
                    obj.CrossRebars[0],
                    cross_front_cover,
                    (
                        f"{mesh_cover_along} Side",
                        cross_top_cover - parallel_diameter
                        if mesh_cover_along == "Top"
                        else cross_bottom_cover + parallel_diameter,
                    ),
                    cross_right_cover,
                    cross_left_cover,
                    cross_diameter,
                    cross_amount_spacing_check,
                    cross_amount_spacing_value,
                    "Horizontal",
                    structure,
                    cross_facename,
                )
            cross_rebars.OffsetEnd = cross_rear_cover + cross_diameter / 2

        elif (
            cross_rebar_type == RebarTypes.ushape and cross_amount_spacing_value
        ):
            if not obj.CrossRebars:
                # Create cross U-Shaped Rebars
                cross_rebars = makeUShapeRebar(
                    cross_front_cover,
                    cross_bottom_cover
                    + (
                        parallel_diameter if mesh_cover_along == "Bottom" else 0
                    ),
                    cross_right_cover,
                    cross_left_cover,
                    cross_diameter,
                    cross_top_cover
                    - (parallel_diameter if mesh_cover_along == "Top" else 0),
                    cross_rounding,
                    cross_amount_spacing_check,
                    cross_amount_spacing_value,
                    mesh_cover_along,
                    structure,
                    cross_facename,
                )
            else:
                # Update cross U-Shaped Rebars
                cross_rebars = editUShapeRebar(
                    obj.CrossRebars[0],
                    cross_front_cover,
                    cross_bottom_cover
                    + (
                        parallel_diameter if mesh_cover_along == "Bottom" else 0
                    ),
                    cross_right_cover,
                    cross_left_cover,
                    cross_diameter,
                    cross_top_cover
                    - (parallel_diameter if mesh_cover_along == "Top" else 0),
                    cross_rounding,
                    cross_amount_spacing_check,
                    cross_amount_spacing_value,
                    mesh_cover_along,
                    structure,
                    cross_facename,
                )
            cross_rebars.OffsetEnd = cross_rear_cover + cross_diameter / 2

        elif (
            cross_rebar_type == RebarTypes.bentshape
            and cross_amount_spacing_value
        ):
            cross_bottom_cover = cross_bottom_cover + (
                parallel_diameter if mesh_cover_along == "Bottom" else 0
            )
            cross_top_cover = cross_top_cover - (
                parallel_diameter if mesh_cover_along == "Top" else 0
            )
            # prevent overlaping of arms in BentShapeRebars
            if parallel_rebar_type == RebarTypes.bentshape:
                if mesh_cover_along == "Bottom":
                    required_rebar_axises_sepration = cross_diameter
                    if (
                        cross_distribution_rebars_check
                        and cross_top_cover < parallel_top_cover
                    ):
                        required_rebar_axises_sepration = (
                            required_rebar_axises_sepration
                            + cross_distribution_rebars_diameter
                        )
                    elif parallel_distribution_rebars_check:
                        required_rebar_axises_sepration = (
                            required_rebar_axises_sepration
                            + parallel_distribution_rebars_diameter
                        )
                    cross_top_cover = self.set_minimum_seperation_distance(
                        cross_top_cover,
                        parallel_top_cover,
                        required_rebar_axises_sepration,
                    )
                else:
                    required_rebar_axises_sepration = cross_diameter
                    if (
                        cross_distribution_rebars_check
                        and cross_bottom_cover < parallel_bottom_cover
                    ):
                        required_rebar_axises_sepration = (
                            required_rebar_axises_sepration
                            + cross_distribution_rebars_diameter
                        )
                    elif parallel_distribution_rebars_check:
                        required_rebar_axises_sepration = (
                            required_rebar_axises_sepration
                            + parallel_distribution_rebars_diameter
                        )
                    cross_bottom_cover = self.set_minimum_seperation_distance(
                        cross_bottom_cover,
                        parallel_bottom_cover,
                        required_rebar_axises_sepration,
                    )
            if not obj.CrossRebars:
                # Create cross bent shaped Rebars
                cross_rebars = makeBentShapeRebar(
                    cross_front_cover,
                    cross_bottom_cover,
                    cross_left_cover,
                    cross_right_cover,
                    cross_diameter,
                    cross_top_cover,
                    cross_bent_bar_length,
                    cross_bent_bar_angle,
                    cross_rounding,
                    cross_amount_spacing_check,
                    cross_amount_spacing_value,
                    mesh_cover_along,
                    structure,
                    cross_facename,
                )
            else:
                # Update cross bent shaped Rebars
                cross_rebars = editBentShapeRebar(
                    obj.CrossRebars[0],
                    cross_front_cover,
                    cross_bottom_cover,
                    cross_left_cover,
                    cross_right_cover,
                    cross_diameter,
                    cross_top_cover,
                    cross_bent_bar_length,
                    cross_bent_bar_angle,
                    cross_rounding,
                    cross_amount_spacing_check,
                    cross_amount_spacing_value,
                    mesh_cover_along,
                    structure,
                    cross_facename,
                )
            cross_rebars.OffsetEnd = cross_rear_cover + cross_diameter / 2

            if (
                cross_distribution_rebars_check
                and cross_distribution_rebars_amount_spacing_value
            ):
                cross_face_length = getParametersOfFace(
                    structure, cross_facename
                )[0][0]
                cover_along_length = cross_diameter + (
                    cross_bottom_cover
                    if mesh_cover_along == "Top"
                    else cross_top_cover
                )
                cover_along = (
                    "Top Side"
                    if mesh_cover_along == "Bottom"
                    else "Bottom Side"
                )
                cross_distribution_rebars_amount = (
                    cross_distribution_rebars_amount_spacing_value
                )
                if not cross_distribution_rebars_amount_spacing_check:
                    # calculate distribution rebars amount based on length of
                    # arm of bent shape rebar and covers for distribution rebars
                    cross_distribution_rebars_amount = (
                        get_rebar_amount_from_spacing(
                            cross_bent_bar_length
                            + cross_left_cover
                            - parallel_front_cover
                            - parallel_diameter
                            - cross_diameter,
                            cross_distribution_rebars_diameter,
                            cross_distribution_rebars_amount_spacing_value,
                        )
                    )

                if not obj.CrossDistributionRebars:
                    # Create left distribution rebars from cross bent shape rebars
                    cross_left_distribution_rebars = makeStraightRebar(
                        parallel_front_cover + parallel_diameter,
                        (
                            cover_along,
                            cover_along_length,
                        ),
                        parallel_right_cover,
                        parallel_left_cover,
                        cross_distribution_rebars_diameter,
                        True,
                        cross_distribution_rebars_amount,
                        "Horizontal",
                        structure,
                        facename,
                    )
                else:
                    # Update left distribution rebars from cross bent shape rebars
                    cross_left_distribution_rebars = editStraightRebar(
                        obj.CrossDistributionRebars[0],
                        parallel_front_cover + parallel_diameter,
                        (
                            cover_along,
                            cover_along_length,
                        ),
                        parallel_right_cover,
                        parallel_left_cover,
                        cross_distribution_rebars_diameter,
                        True,
                        cross_distribution_rebars_amount,
                        "Horizontal",
                        structure,
                        facename,
                    )
                cross_left_distribution_rebars.OffsetEnd = (
                    cross_face_length
                    - cross_bent_bar_length
                    - cross_left_cover
                    + cross_diameter
                    + cross_distribution_rebars_diameter / 2
                )
                # calculate front cover for right side distribution rebars
                cross_right_front_cover = (
                    cross_face_length
                    - cross_right_cover
                    - cross_bent_bar_length
                    + cross_diameter
                )

                if len(obj.CrossDistributionRebars) < 2:
                    # Create right distribution rebars from cross bent shape rebars
                    cross_right_distribution_rebars = makeStraightRebar(
                        cross_right_front_cover,
                        (
                            cover_along,
                            cover_along_length,
                        ),
                        parallel_right_cover,
                        parallel_left_cover,
                        cross_distribution_rebars_diameter,
                        True,
                        cross_distribution_rebars_amount,
                        "Horizontal",
                        structure,
                        facename,
                    )
                else:
                    # Update right distribution rebars from cross bent shape rebars
                    cross_right_distribution_rebars = editStraightRebar(
                        obj.CrossDistributionRebars[1],
                        cross_right_front_cover,
                        (
                            cover_along,
                            cover_along_length,
                        ),
                        parallel_right_cover,
                        parallel_left_cover,
                        cross_distribution_rebars_diameter,
                        True,
                        cross_distribution_rebars_amount,
                        "Horizontal",
                        structure,
                        facename,
                    )
                cross_right_distribution_rebars.OffsetEnd = (
                    parallel_rear_cover
                    + parallel_diameter
                    + cross_distribution_rebars_diameter / 2
                )
                cross_distribution_rebars = [
                    cross_left_distribution_rebars,
                    cross_right_distribution_rebars,
                ]

        elif (
            cross_rebar_type == RebarTypes.lshape and cross_amount_spacing_value
        ):
            if cross_l_shape_hook_orintation == "Alternate":
                parallel_face_length = getParametersOfFace(structure, facename)[
                    0
                ][0]
                if not cross_amount_spacing_check:
                    cross_rebars_amount = get_rebar_amount_from_spacing(
                        parallel_face_length,
                        cross_diameter,
                        cross_amount_spacing_value,
                    )
                else:
                    cross_rebars_amount = cross_amount_spacing_value

                # calculate amount of L-shaped rebars having right hook orientation
                cross_modified_amount_spacing_value_2 = cross_rebars_amount // 2
                # calculate amount of L-shaped rebars having left hook orientation
                cross_modified_amount_spacing_value_1 = (
                    cross_rebars_amount - cross_modified_amount_spacing_value_2
                )
                if cross_rebars_amount == 1:
                    cross_interval = cross_front_cover
                else:
                    cross_interval = (
                        parallel_face_length
                        - cross_front_cover
                        - cross_rear_cover
                    ) / (cross_rebars_amount - 1)
                cross_modified_front_cover = cross_front_cover + cross_interval
                cross_rebars = []
                if cross_modified_amount_spacing_value_1:
                    if not obj.CrossRebars:
                        # Create L-shaped rebars having left hook orientation
                        cross_left_rebars = makeLShapeRebar(
                            cross_front_cover,
                            cross_bottom_cover
                            + (
                                parallel_diameter
                                if mesh_cover_along == "Bottom"
                                else 0
                            ),
                            cross_left_cover,
                            cross_right_cover,
                            cross_diameter,
                            cross_top_cover
                            - (
                                parallel_diameter
                                if mesh_cover_along == "Top"
                                else 0
                            ),
                            cross_rounding,
                            True,
                            cross_modified_amount_spacing_value_1,
                            f"{mesh_cover_along} Left",
                            structure,
                            cross_facename,
                        )
                    else:
                        # Update L-shaped rebars having left hook orientation
                        cross_left_rebars = editLShapeRebar(
                            obj.CrossRebars[0],
                            cross_front_cover,
                            cross_bottom_cover
                            + (
                                parallel_diameter
                                if mesh_cover_along == "Bottom"
                                else 0
                            ),
                            cross_left_cover,
                            cross_right_cover,
                            cross_diameter,
                            cross_top_cover
                            - (
                                parallel_diameter
                                if mesh_cover_along == "Top"
                                else 0
                            ),
                            cross_rounding,
                            True,
                            cross_modified_amount_spacing_value_1,
                            f"{mesh_cover_along} Left",
                            structure,
                            cross_facename,
                        )
                    cross_left_rebars.OffsetEnd = (
                        cross_rear_cover
                        + cross_diameter / 2
                        + (
                            cross_interval
                            if cross_modified_amount_spacing_value_1
                            == cross_modified_amount_spacing_value_2
                            else 0
                        )
                    )
                    cross_rebars.append(cross_left_rebars)

                if cross_modified_amount_spacing_value_2:
                    if len(obj.CrossRebars) < 2:
                        # Create L-shaped rebars having right hook orientation
                        cross_right_rebars = makeLShapeRebar(
                            cross_modified_front_cover,
                            cross_bottom_cover
                            + (
                                parallel_diameter
                                if mesh_cover_along == "Bottom"
                                else 0
                            ),
                            cross_left_cover,
                            cross_right_cover,
                            cross_diameter,
                            cross_top_cover
                            - (
                                parallel_diameter
                                if mesh_cover_along == "Top"
                                else 0
                            ),
                            cross_rounding,
                            True,
                            cross_modified_amount_spacing_value_2,
                            f"{mesh_cover_along} Right",
                            structure,
                            cross_facename,
                        )
                    else:
                        # Update L-shaped rebars having right hook orientation
                        cross_right_rebars = editLShapeRebar(
                            obj.CrossRebars[1],
                            cross_modified_front_cover,
                            cross_bottom_cover
                            + (
                                parallel_diameter
                                if mesh_cover_along == "Bottom"
                                else 0
                            ),
                            cross_left_cover,
                            cross_right_cover,
                            cross_diameter,
                            cross_top_cover
                            - (
                                parallel_diameter
                                if mesh_cover_along == "Top"
                                else 0
                            ),
                            cross_rounding,
                            True,
                            cross_modified_amount_spacing_value_2,
                            f"{mesh_cover_along} Right",
                            structure,
                            cross_facename,
                        )
                    cross_right_rebars.OffsetEnd = (
                        cross_rear_cover
                        + cross_diameter / 2
                        + (
                            cross_interval
                            if (
                                cross_modified_amount_spacing_value_1
                                - cross_modified_amount_spacing_value_2
                            )
                            == 1
                            else 0
                        )
                    )
                    cross_rebars.append(cross_right_rebars)
                elif len(obj.CrossRebars) >= 2:
                    # Deleting extra L-Shaped Rebars
                    for Rebar in obj.CrossRebars[1:]:
                        base_name = Rebar.Base.Name
                        FreeCAD.ActiveDocument.removeObject(Rebar.Name)
                        FreeCAD.ActiveDocument.removeObject(base_name)

            else:
                if not obj.CrossRebars:
                    # Create L-shaped rebars
                    cross_rebars = makeLShapeRebar(
                        cross_front_cover,
                        cross_bottom_cover
                        + (
                            parallel_diameter
                            if mesh_cover_along == "Bottom"
                            else 0
                        ),
                        cross_left_cover,
                        cross_right_cover,
                        cross_diameter,
                        cross_top_cover
                        - (
                            parallel_diameter
                            if mesh_cover_along == "Top"
                            else 0
                        ),
                        cross_rounding,
                        True,
                        cross_amount_spacing_value,
                        f"{mesh_cover_along} {cross_l_shape_hook_orintation}",
                        structure,
                        cross_facename,
                    )
                else:
                    # Update L-shaped rebars
                    cross_rebars = editLShapeRebar(
                        obj.CrossRebars[0],
                        cross_front_cover,
                        cross_bottom_cover
                        + (
                            parallel_diameter
                            if mesh_cover_along == "Bottom"
                            else 0
                        ),
                        cross_left_cover,
                        cross_right_cover,
                        cross_diameter,
                        cross_top_cover
                        - (
                            parallel_diameter
                            if mesh_cover_along == "Top"
                            else 0
                        ),
                        cross_rounding,
                        True,
                        cross_amount_spacing_value,
                        f"{mesh_cover_along} {cross_l_shape_hook_orintation}",
                        structure,
                        cross_facename,
                    )
                cross_rebars.OffsetEnd = cross_rear_cover + cross_diameter / 2

        cross_rebars = cross_rebars if cross_rebars else []
        parallel_rebars = parallel_rebars if parallel_rebars else []
        parallel_rebars_list = (
            parallel_rebars
            if isinstance(parallel_rebars, list)
            else [parallel_rebars]
        )
        cross_rebars_list = (
            cross_rebars if isinstance(cross_rebars, list) else [cross_rebars]
        )

        # Assign new or updated rebar list to respective properties
        # of SlabReinforcementGroup
        obj.addObjects(parallel_rebars_list)
        obj.ParallelRebars = parallel_rebars_list
        obj.addObjects(cross_rebars_list)
        obj.CrossRebars = cross_rebars_list
        obj.addObjects(cross_distribution_rebars)
        obj.CrossDistributionRebars = cross_distribution_rebars
        obj.addObjects(parallel_distribution_rebars)
        obj.ParallelDistributionRebars = parallel_distribution_rebars

        FreeCAD.ActiveDocument.recompute()

    def set_minimum_seperation_distance(
        self, relative_distance, absolute_distance, min_seperation_distance
    ):
        """
        Get new relative distance having min_seperation_distance from
        absolute_distance
        """
        sepration_distance = relative_distance - absolute_distance
        if abs(sepration_distance) < min_seperation_distance:
            if sepration_distance < 0:
                relative_distance = absolute_distance - min_seperation_distance
            else:
                relative_distance = absolute_distance + min_seperation_distance
        return relative_distance

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None
