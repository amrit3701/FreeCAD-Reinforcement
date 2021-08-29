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

__title__ = "Footing Reinforcement Group"
__author__ = "Shiv Charan"
__url__ = "https://www.freecadweb.org"


import FreeCAD
from DraftGui import todo
from PySide2.QtCore import QT_TRANSLATE_NOOP
from SlabReinforcement.SlabReinforcement import (
    makeSlabReinforcement,
    editSlabReinforcement,
)
from ColumnReinforcement.SingleTieMultipleRebars import (
    makeSingleTieMultipleRebars,
    makeSingleTieFourRebars,
    editSingleTieFourRebars,
    editSingleTieMultipleRebars,
)
from Rebarfunc import (
    getFacenamesforFootingReinforcement,
    getParametersOfFace,
    showWarning,
)


class FootingReinforcementGroup:
    """A Footing Reinforcement Group object."""

    def __init__(self, obj_name="FootingReinforcement"):
        """intialize group for Footing Reinforcement Group object"""
        rebar_group = FreeCAD.ActiveDocument.addObject(
            "App::DocumentObjectGroupPython", obj_name
        )
        slabs_rebar_group = rebar_group.newObject(
            "App::DocumentObjectGroupPython", "SlabReinforcements"
        )
        columns_rebar_group = rebar_group.newObject(
            "App::DocumentObjectGroupPython", "ColumnReinforcements"
        )

        self.setFootingProperties(rebar_group)
        self.setColumnsGroupProperties(columns_rebar_group)
        self.setSlabsGroupProperties(slabs_rebar_group)
        rebar_group.ReinforcementGroups = [
            slabs_rebar_group,
            columns_rebar_group,
        ]
        self.Object = rebar_group
        rebar_group.Proxy = self

    def setColumnsGroupProperties(self, obj):
        """Add properties to Column Reinforcement group object"""
        if not hasattr(obj, "RowObjectList"):
            obj.addProperty(
                "App::PropertyLinkList",
                "RowObjectList",
                "ColumnsReinforcementGroup",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "List of reinforcement groups",
                ),
            )

    def setSlabsGroupProperties(self, obj):
        """Add properties to Slab Reinforcement group object"""
        if not hasattr(obj, "SlabsReinforcementList"):
            obj.addProperty(
                "App::PropertyLinkList",
                "SlabsReinforcementList",
                "SlabsReinforcementGroup",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "List of reinforcement groups",
                ),
            )

    def setFootingProperties(self, obj):
        """Add properties to Footing Reinforcement object"""
        self.Type = "FootingReinforcementGroup"
        if not hasattr(obj, "IsMakeOrEditRequired"):
            obj.addProperty(
                "App::PropertyBool",
                "IsMakeOrEditRequired",
                "FootingReinforcementGroup",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Check if make or update required for slab reinforcement",
                ),
            )
            obj.IsMakeOrEditRequired = False
            obj.setEditorMode("IsMakeOrEditRequired", 2)

        if not hasattr(obj, "ReinforcementGroups"):
            obj.addProperty(
                "App::PropertyLinkList",
                "ReinforcementGroups",
                "FootingReinforcementGroup",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "List of reinforcement groups",
                ),
            )

        if not hasattr(obj, "MeshCoverAlong"):
            obj.addProperty(
                "App::PropertyEnumeration",
                "MeshCoverAlong",
                "FootingReinforcementGroup",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Mesh Cover Along for slab reinforcement",
                ),
            ).MeshCoverAlong = ["Bottom", "Top", "Both"]
            obj.MeshCoverAlong = "Bottom"

        if not hasattr(obj, "Facename"):
            obj.addProperty(
                "App::PropertyString",
                "Facename",
                "FootingReinforcementGroup",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Facename",
                ),
            )

        if not hasattr(obj, "Structure"):
            obj.addProperty(
                "App::PropertyLink",
                "Structure",
                "FootingReinforcementGroup",
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

        # Properties for Columns
        if not hasattr(obj, "ColumnFrontCover"):
            obj.addProperty(
                "App::PropertyDistance",
                "ColumnFrontCover",
                "ColumnReinforcements",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Column Front Cover",
                ),
            )
            obj.ColumnFrontCover = 400

        if not hasattr(obj, "ColumnLeftCover"):
            obj.addProperty(
                "App::PropertyDistance",
                "ColumnLeftCover",
                "ColumnReinforcements",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Column Left Cover",
                ),
            )
            obj.ColumnLeftCover = 400

        if not hasattr(obj, "ColumnRightCover"):
            obj.addProperty(
                "App::PropertyDistance",
                "ColumnRightCover",
                "ColumnReinforcements",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Column Right Cover",
                ),
            )
            obj.ColumnRightCover = 400

        if not hasattr(obj, "ColumnRearCover"):
            obj.addProperty(
                "App::PropertyDistance",
                "ColumnRearCover",
                "ColumnReinforcements",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Column Rear Cover",
                ),
            )
            obj.ColumnRearCover = 400

        if not hasattr(obj, "TieTopCover"):
            obj.addProperty(
                "App::PropertyDistance",
                "TieTopCover",
                "ColumnReinforcements",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Tie Top Cover",
                ),
            )
            obj.TieTopCover = 400

        if not hasattr(obj, "TieBottomCover"):
            obj.addProperty(
                "App::PropertyDistance",
                "TieBottomCover",
                "ColumnReinforcements",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Tie Bottom Cover",
                ),
            )
            obj.TieBottomCover = 10

        if not hasattr(obj, "TieBentAngle"):
            obj.addProperty(
                "App::PropertyInteger",
                "TieBentAngle",
                "ColumnReinforcements",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Tie Bent Angle",
                ),
            )
            obj.TieBentAngle = 135

        if not hasattr(obj, "TieExtensionFactor"):
            obj.addProperty(
                "App::PropertyInteger",
                "TieExtensionFactor",
                "ColumnReinforcements",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Tie Extension Factor",
                ),
            )
            obj.TieExtensionFactor = 2

        if not hasattr(obj, "TieDiameter"):
            obj.addProperty(
                "App::PropertyDistance",
                "TieDiameter",
                "ColumnReinforcements",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Tie Diameter",
                ),
            )
            obj.TieDiameter = 8

        if not hasattr(obj, "TieNumberSpacingCheck"):
            obj.addProperty(
                "App::PropertyBool",
                "TieNumberSpacingCheck",
                "ColumnReinforcements",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Tie Number Spacing Check",
                ),
            )
            obj.TieNumberSpacingCheck = True

        if not hasattr(obj, "TieAmountValue"):
            obj.addProperty(
                "App::PropertyInteger",
                "TieAmountValue",
                "ColumnReinforcements",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Tie Amount Value",
                ),
            )
            obj.TieAmountValue = 3

        if not hasattr(obj, "TieSpacingValue"):
            obj.addProperty(
                "App::PropertyDistance",
                "TieSpacingValue",
                "ColumnReinforcements",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Tie Spacing Value",
                ),
            )
            obj.TieSpacingValue = 50

        if not hasattr(obj, "ColumnMainRebarsDiameter"):
            obj.addProperty(
                "App::PropertyDistance",
                "ColumnMainRebarsDiameter",
                "ColumnReinforcements",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Column Main Rebar's Diameter",
                ),
            )
            obj.ColumnMainRebarsDiameter = 8

        if not hasattr(obj, "ColumnMainRebarsTopOffset"):
            obj.addProperty(
                "App::PropertyDistance",
                "ColumnMainRebarsTopOffset",
                "ColumnReinforcements",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Column Main Rebars TopOffset",
                ),
            )
            obj.ColumnMainRebarsTopOffset = 400

        if not hasattr(obj, "ColumnWidth"):
            obj.addProperty(
                "App::PropertyDistance",
                "ColumnWidth",
                "ColumnReinforcements",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Column Width",
                ),
            )
            obj.ColumnWidth = 200

        if not hasattr(obj, "ColumnLength"):
            obj.addProperty(
                "App::PropertyDistance",
                "ColumnLength",
                "ColumnReinforcements",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Column Length",
                ),
            )
            obj.ColumnLength = 200

        if not hasattr(obj, "XDirColumnNumberSpacingCheck"):
            obj.addProperty(
                "App::PropertyBool",
                "XDirColumnNumberSpacingCheck",
                "ColumnReinforcements",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "X Direction Column Number Spacing Check",
                ),
            )
            obj.XDirColumnNumberSpacingCheck = True

        if not hasattr(obj, "XDirColumnAmountValue"):
            obj.addProperty(
                "App::PropertyInteger",
                "XDirColumnAmountValue",
                "ColumnReinforcements",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "X Direction Column Amount Value",
                ),
            )
            obj.XDirColumnAmountValue = 1

        if not hasattr(obj, "XDirColumnSpacingValue"):
            obj.addProperty(
                "App::PropertyDistance",
                "XDirColumnSpacingValue",
                "ColumnReinforcements",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "X Direction Column Spacing Value",
                ),
            )
            obj.XDirColumnSpacingValue = 200

        if not hasattr(obj, "YDirColumnNumberSpacingCheck"):
            obj.addProperty(
                "App::PropertyDistance",
                "YDirColumnNumberSpacingCheck",
                "ColumnReinforcements",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Y Direction Column Number Spacing Check",
                ),
            )
            obj.YDirColumnNumberSpacingCheck = True

        if not hasattr(obj, "YDirColumnAmountValue"):
            obj.addProperty(
                "App::PropertyInteger",
                "YDirColumnAmountValue",
                "ColumnReinforcements",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Y Direction Column Amount Value",
                ),
            )
            obj.YDirColumnAmountValue = 1

        if not hasattr(obj, "YDirColumnSpacingValue"):
            obj.addProperty(
                "App::PropertyDistance",
                "YDirColumnSpacingValue",
                "ColumnReinforcements",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Y Direction Column Spacing Value",
                ),
            )
            obj.YDirColumnSpacingValue = 200

        if not hasattr(obj, "ColumnMainRebarType"):
            obj.addProperty(
                "App::PropertyEnumeration",
                "ColumnMainRebarType",
                "ColumnReinforcements",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Main Rebars Types",
                ),
            ).ColumnMainRebarType = [
                "StraightRebar",
                "LShapeRebar",
            ]
            obj.ColumnMainRebarType = "LShapeRebar"

        if not hasattr(obj, "ColumnMainHookOrientation"):
            obj.addProperty(
                "App::PropertyEnumeration",
                "ColumnMainHookOrientation",
                "ColumnReinforcements",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Main L-shape Rebars Hook Orientation",
                ),
            ).ColumnMainHookOrientation = [
                "Top Inside",
                "Top Outside",
                "Bottom Inside",
                "Bottom Outside",
                "Top Left",
                "Top Right",
                "Bottom Left",
                "Bottom Right",
            ]
            obj.ColumnMainHookOrientation = "Bottom Outside"

        if not hasattr(obj, "ColumnMainHookExtendAlong"):
            obj.addProperty(
                "App::PropertyEnumeration",
                "ColumnMainHookExtendAlong",
                "ColumnReinforcements",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Main L-shape Rebars Hook Extend Along",
                ),
            ).ColumnMainHookExtendAlong = ["x-axis", "y-axis"]
            obj.ColumnMainHookExtendAlong = "x-axis"

        if not hasattr(obj, "ColumnMainLRebarRounding"):
            obj.addProperty(
                "App::PropertyInteger",
                "ColumnMainLRebarRounding",
                "ColumnReinforcements",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Main L-shape Rebars Rounding ",
                ),
            )
            obj.ColumnMainLRebarRounding = 2

        if not hasattr(obj, "ColumnMainHookExtension"):
            obj.addProperty(
                "App::PropertyDistance",
                "ColumnMainHookExtension",
                "ColumnReinforcements",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Main L-shape Rebars Hook Extension",
                ),
            )
            obj.ColumnMainHookExtension = 40

        if not hasattr(obj, "ColumnSecRebarsCheck"):
            obj.addProperty(
                "App::PropertyBool",
                "ColumnSecRebarsCheck",
                "ColumnReinforcements",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Secoundery Rebars Check",
                ),
            )
            obj.ColumnSecRebarsCheck = False

        if not hasattr(obj, "ColumnSecRebarsTopOffset"):
            obj.addProperty(
                "App::PropertyFloatList",
                "ColumnSecRebarsTopOffset",
                "ColumnReinforcements",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Secoundery Rebars Top Offset",
                ),
            )
            obj.ColumnSecRebarsTopOffset = (400, 400)

        if not hasattr(obj, "ColumnSecRebarsNumberDiameter"):
            obj.addProperty(
                "App::PropertyStringList",
                "ColumnSecRebarsNumberDiameter",
                "ColumnReinforcements",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Secoundery Rebars Number Diameter",
                ),
            )
            obj.ColumnSecRebarsNumberDiameter = (
                "1#6mm+1#6mm+1#6mm",
                "1#6mm+1#6mm+1#6mm",
            )

        if not hasattr(obj, "ColumnSecRebarsType"):
            obj.addProperty(
                "App::PropertyStringList",
                "ColumnSecRebarsType",
                "ColumnReinforcements",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Secoundery Rebars type",
                ),
            )
            obj.ColumnSecRebarsType = (
                "LShapeRebar",
                "LShapeRebar",
            )

        if not hasattr(obj, "ColumnSecHookOrientation"):
            obj.addProperty(
                "App::PropertyStringList",
                "ColumnSecHookOrientation",
                "ColumnReinforcements",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Secoundery L-Shape Rebar Hook Orientation",
                ),
            )
            obj.ColumnSecHookOrientation = (
                "Bottom Outside",
                "Bottom Outside",
            )

        if not hasattr(obj, "ColumnSecLRebarRounding"):
            obj.addProperty(
                "App::PropertyIntegerList",
                "ColumnSecLRebarRounding",
                "ColumnReinforcements",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Secoundery L-Shape Rebar Hook Rounding",
                ),
            )
            obj.ColumnSecLRebarRounding = (2, 2)

        if not hasattr(obj, "ColumnSecHookExtension"):
            obj.addProperty(
                "App::PropertyFloatList",
                "ColumnSecHookExtension",
                "ColumnReinforcements",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "Secoundery L-Shape Rebar Hook Extension",
                ),
            )
            obj.ColumnSecHookExtension = (80, 80)

    def onChanged(self, obj, prop):
        if prop != "IsMakeOrEditRequired" and obj.IsMakeOrEditRequired:
            obj.IsMakeOrEditRequired = False
            self.makeOrEditFootingReinforcement(obj)
            obj.IsMakeOrEditRequired = True

    def execute(self, obj):
        pass

    def makeOrEditFootingReinforcement(self, obj):
        """Create or update Footing Reinforcement"""
        obj.IsMakeOrEditRequired = False
        mesh_cover_along = obj.MeshCoverAlong
        facename = obj.Facename
        structure = obj.Structure
        parallel_rebar_type = obj.ParallelRebarType
        parallel_front_cover = FreeCAD.Units.Quantity(
            obj.ParallelFrontCover
        ).Value
        parallel_rear_cover = FreeCAD.Units.Quantity(
            obj.ParallelRearCover
        ).Value
        parallel_left_cover = FreeCAD.Units.Quantity(
            obj.ParallelLeftCover
        ).Value
        parallel_right_cover = FreeCAD.Units.Quantity(
            obj.ParallelRightCover
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
        parallel_l_shape_hook_orintation = obj.ParallelLShapeHookOrintation
        cross_rebar_type = obj.CrossRebarType
        cross_front_cover = FreeCAD.Units.Quantity(obj.CrossFrontCover).Value
        cross_rear_cover = FreeCAD.Units.Quantity(obj.CrossRearCover).Value
        cross_left_cover = FreeCAD.Units.Quantity(obj.CrossLeftCover).Value
        cross_right_cover = FreeCAD.Units.Quantity(obj.CrossRightCover).Value
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
        cross_l_shape_hook_orintation = obj.CrossLShapeHookOrintation
        column_front_cover = FreeCAD.Units.Quantity(obj.ColumnFrontCover).Value
        column_left_cover = FreeCAD.Units.Quantity(obj.ColumnLeftCover).Value
        column_right_cover = FreeCAD.Units.Quantity(obj.ColumnRightCover).Value
        column_rear_cover = FreeCAD.Units.Quantity(obj.ColumnRearCover).Value
        tie_top_cover = FreeCAD.Units.Quantity(obj.TieTopCover).Value
        tie_bottom_cover = FreeCAD.Units.Quantity(obj.TieBottomCover).Value
        tie_bent_angle = obj.TieBentAngle
        tie_extension_factor = obj.TieExtensionFactor
        tie_diameter = FreeCAD.Units.Quantity(obj.TieDiameter).Value
        tie_number_spacing_check = obj.TieNumberSpacingCheck
        if tie_number_spacing_check:
            tie_number_spacing_value = obj.TieAmountValue
        else:
            tie_number_spacing_value = FreeCAD.Units.Quantity(
                obj.TieSpacingValue
            ).Value
        column_main_rebar_diameter = FreeCAD.Units.Quantity(
            obj.ColumnMainRebarsDiameter
        ).Value
        column_main_rebars_t_offset = FreeCAD.Units.Quantity(
            obj.ColumnMainRebarsTopOffset
        ).Value
        column_width = FreeCAD.Units.Quantity(obj.ColumnWidth).Value
        column_length = FreeCAD.Units.Quantity(obj.ColumnLength).Value
        xdir_column_amount_spacing_check = obj.XDirColumnNumberSpacingCheck
        if xdir_column_amount_spacing_check:
            xdir_column_amount_spacing_value = obj.XDirColumnAmountValue
        else:
            xdir_column_amount_spacing_value = FreeCAD.Units.Quantity(
                obj.XDirColumnSpacingValue
            ).Value
        ydir_column_amount_spacing_check = obj.YDirColumnNumberSpacingCheck
        if ydir_column_amount_spacing_check:
            ydir_column_amount_spacing_value = obj.YDirColumnAmountValue
        else:
            ydir_column_amount_spacing_value = FreeCAD.Units.Quantity(
                obj.YDirColumnSpacingValue
            ).Value
        column_main_rebars_type = obj.ColumnMainRebarType
        column_main_hook_orientation = obj.ColumnMainHookOrientation
        column_main_hook_extend_along = obj.ColumnMainHookExtendAlong
        column_l_main_rebar_rounding = obj.ColumnMainLRebarRounding
        column_main_hook_extension = FreeCAD.Units.Quantity(
            obj.ColumnMainHookExtension
        ).Value
        column_sec_rebar_check = obj.ColumnSecRebarsCheck
        column_sec_rebars_t_offset = obj.ColumnSecRebarsTopOffset
        column_sec_rebars_number_diameter = obj.ColumnSecRebarsNumberDiameter
        column_sec_rebars_type = obj.ColumnSecRebarsType
        column_sec_hook_orientation = obj.ColumnSecHookOrientation
        column_l_sec_rebar_rounding = obj.ColumnSecLRebarRounding
        column_sec_hook_extension = obj.ColumnSecHookExtension
        selected_face_hight = getParametersOfFace(structure, facename)[0][1]

        top_facename = getFacenamesforFootingReinforcement(facename, structure)[
            1
        ]
        column_b_offset = (
            parallel_bottom_cover + parallel_diameter + cross_diameter
        )
        top_face_width, top_face_length = getParametersOfFace(
            structure, top_facename
        )[0]

        # Calculate tie offset as per main rebars length
        calculated_tie_offset = (
            column_main_rebars_t_offset
            + selected_face_hight
            - tie_diameter
            - tie_top_cover
        )
        # remove cover length from face lengths
        top_face_width = top_face_width - column_left_cover
        top_face_length = top_face_length - column_front_cover
        # Calculate spacing value from column amount in y-axis direction
        if ydir_column_amount_spacing_check:
            ydir_column_amount_value = ydir_column_amount_spacing_value
            empty_space_length = (
                top_face_length
                - column_rear_cover
                - (ydir_column_amount_spacing_value) * column_length
            )
            if empty_space_length < 0:
                # Space between front and rear cover less to add given column amount
                showWarning(
                    "Error: Space between front and rear cover less to add given column amount"
                )
                return None
            if ydir_column_amount_spacing_value > 1:
                ydir_column_spacing_value = empty_space_length / (
                    ydir_column_amount_spacing_value - 1
                )
            else:
                ydir_column_spacing_value = empty_space_length

        else:
            ydir_column_spacing_value = ydir_column_amount_spacing_value
            ydir_column_amount_value = 1
            empty_space_length = (
                top_face_length - column_rear_cover - column_length
            )
            while empty_space_length > 0:
                empty_space_length = (
                    empty_space_length
                    - column_length
                    - ydir_column_spacing_value
                )
                ydir_column_amount_value = ydir_column_amount_value + 1
        # Calculate spacing value from column amount in x-axis direction
        if xdir_column_amount_spacing_check:
            xdir_column_amount_value = xdir_column_amount_spacing_value
            empty_space_length = (
                top_face_width
                - column_right_cover
                - (xdir_column_amount_spacing_value) * column_width
            )
            if empty_space_length < 0:
                # Space between left and rigth cover less to add given column amount
                showWarning(
                    "Error: Space between left and rigth cover less to add given column amount"
                )
                return None
            if xdir_column_amount_spacing_value > 1:
                xdir_column_spacing_value = empty_space_length / (
                    xdir_column_amount_spacing_value - 1
                )
            else:
                xdir_column_spacing_value = empty_space_length
        else:
            xdir_column_spacing_value = xdir_column_amount_spacing_value
            xdir_column_amount_value = 1
            empty_space_length = (
                top_face_width - column_right_cover - column_width
            )
            while empty_space_length > 0:
                empty_space_length = (
                    empty_space_length
                    - column_width
                    - xdir_column_spacing_value
                )
                xdir_column_amount_value = xdir_column_amount_value + 1

        slabs_reinforcements = obj.ReinforcementGroups[0].SlabsReinforcementList
        if mesh_cover_along != "Both" and len(slabs_reinforcements) > 1:
            self.removeSlabReinforcement(slabs_reinforcements[1])
            del slabs_reinforcements[1]

        if not slabs_reinforcements:
            slabReinforcementGroup = makeSlabReinforcement(
                parallel_rebar_type=parallel_rebar_type,
                parallel_front_cover=parallel_front_cover,
                parallel_rear_cover=parallel_rear_cover,
                parallel_left_cover=parallel_left_cover,
                parallel_right_cover=parallel_right_cover,
                parallel_top_cover=parallel_top_cover
                if mesh_cover_along != "Both"
                else parallel_top_cover + selected_face_hight / 2,
                parallel_bottom_cover=parallel_bottom_cover,
                parallel_diameter=parallel_diameter,
                parallel_amount_spacing_check=parallel_amount_spacing_check,
                parallel_amount_spacing_value=parallel_amount_spacing_value,
                cross_rebar_type=cross_rebar_type,
                cross_front_cover=cross_front_cover,
                cross_rear_cover=cross_rear_cover,
                cross_left_cover=cross_left_cover,
                cross_right_cover=cross_right_cover,
                cross_top_cover=cross_top_cover
                if mesh_cover_along != "Both"
                else cross_top_cover + selected_face_hight / 2,
                cross_bottom_cover=cross_bottom_cover,
                cross_diameter=cross_diameter,
                cross_amount_spacing_check=cross_amount_spacing_check,
                cross_amount_spacing_value=cross_amount_spacing_value,
                cross_rounding=cross_rounding,
                cross_l_shape_hook_orintation=cross_l_shape_hook_orintation,
                cross_distribution_rebars_check=False,
                parallel_rounding=parallel_rounding,
                parallel_l_shape_hook_orintation=parallel_l_shape_hook_orintation,
                parallel_distribution_rebars_check=False,
                mesh_cover_along=mesh_cover_along
                if mesh_cover_along != "Both"
                else "Bottom",
                structure=structure,
                facename=facename,
            )
            slabs_reinforcements.append(slabReinforcementGroup)
        else:
            slabs_reinforcements[0] = editSlabReinforcement(
                slabReinforcementGroup=slabs_reinforcements[0],
                parallel_rebar_type=parallel_rebar_type,
                parallel_front_cover=parallel_front_cover,
                parallel_rear_cover=parallel_rear_cover,
                parallel_left_cover=parallel_left_cover,
                parallel_right_cover=parallel_right_cover,
                parallel_top_cover=parallel_top_cover
                if mesh_cover_along != "Both"
                else parallel_top_cover + selected_face_hight / 2,
                parallel_bottom_cover=parallel_bottom_cover,
                parallel_diameter=parallel_diameter,
                parallel_amount_spacing_check=parallel_amount_spacing_check,
                parallel_amount_spacing_value=parallel_amount_spacing_value,
                cross_rebar_type=cross_rebar_type,
                cross_front_cover=cross_front_cover,
                cross_rear_cover=cross_rear_cover,
                cross_left_cover=cross_left_cover,
                cross_right_cover=cross_right_cover,
                cross_top_cover=cross_top_cover
                if mesh_cover_along != "Both"
                else cross_top_cover + selected_face_hight / 2,
                cross_bottom_cover=cross_bottom_cover,
                cross_diameter=cross_diameter,
                cross_amount_spacing_check=cross_amount_spacing_check,
                cross_amount_spacing_value=cross_amount_spacing_value,
                cross_rounding=cross_rounding,
                cross_l_shape_hook_orintation=cross_l_shape_hook_orintation,
                cross_distribution_rebars_check=False,
                parallel_rounding=parallel_rounding,
                parallel_l_shape_hook_orintation=parallel_l_shape_hook_orintation,
                parallel_distribution_rebars_check=False,
                mesh_cover_along=mesh_cover_along
                if mesh_cover_along != "Both"
                else "Bottom",
                structure=structure,
                facename=facename,
            )

        if mesh_cover_along == "Both":
            if len(slabs_reinforcements) < 2:
                topSlabReinforcementGroup = makeSlabReinforcement(
                    parallel_rebar_type=parallel_rebar_type,
                    parallel_front_cover=parallel_front_cover,
                    parallel_rear_cover=parallel_rear_cover,
                    parallel_left_cover=parallel_left_cover,
                    parallel_right_cover=parallel_right_cover,
                    parallel_top_cover=parallel_top_cover,
                    parallel_bottom_cover=parallel_bottom_cover
                    + selected_face_hight / 2,
                    parallel_diameter=parallel_diameter,
                    parallel_amount_spacing_check=parallel_amount_spacing_check,
                    parallel_amount_spacing_value=parallel_amount_spacing_value,
                    cross_rebar_type=cross_rebar_type,
                    cross_front_cover=cross_front_cover,
                    cross_rear_cover=cross_rear_cover,
                    cross_left_cover=cross_left_cover,
                    cross_right_cover=cross_right_cover,
                    cross_top_cover=cross_top_cover,
                    cross_bottom_cover=cross_bottom_cover
                    + selected_face_hight / 2,
                    cross_diameter=cross_diameter,
                    cross_amount_spacing_check=cross_amount_spacing_check,
                    cross_amount_spacing_value=cross_amount_spacing_value,
                    cross_rounding=cross_rounding,
                    cross_l_shape_hook_orintation=cross_l_shape_hook_orintation,
                    cross_distribution_rebars_check=False,
                    parallel_rounding=parallel_rounding,
                    parallel_l_shape_hook_orintation=parallel_l_shape_hook_orintation,
                    parallel_distribution_rebars_check=False,
                    mesh_cover_along="Top",
                    structure=structure,
                    facename=facename,
                )
                slabs_reinforcements.append(topSlabReinforcementGroup)
            else:
                slabs_reinforcements[1] = editSlabReinforcement(
                    slabReinforcementGroup=slabs_reinforcements[1],
                    parallel_rebar_type=parallel_rebar_type,
                    parallel_front_cover=parallel_front_cover,
                    parallel_rear_cover=parallel_rear_cover,
                    parallel_left_cover=parallel_left_cover,
                    parallel_right_cover=parallel_right_cover,
                    parallel_top_cover=parallel_top_cover,
                    parallel_bottom_cover=parallel_bottom_cover
                    + selected_face_hight / 2,
                    parallel_diameter=parallel_diameter,
                    parallel_amount_spacing_check=parallel_amount_spacing_check,
                    parallel_amount_spacing_value=parallel_amount_spacing_value,
                    cross_rebar_type=cross_rebar_type,
                    cross_front_cover=cross_front_cover,
                    cross_rear_cover=cross_rear_cover,
                    cross_left_cover=cross_left_cover,
                    cross_right_cover=cross_right_cover,
                    cross_top_cover=cross_top_cover,
                    cross_bottom_cover=cross_bottom_cover
                    + selected_face_hight / 2,
                    cross_diameter=cross_diameter,
                    cross_amount_spacing_check=cross_amount_spacing_check,
                    cross_amount_spacing_value=cross_amount_spacing_value,
                    cross_rounding=cross_rounding,
                    cross_l_shape_hook_orintation=cross_l_shape_hook_orintation,
                    cross_distribution_rebars_check=False,
                    parallel_rounding=parallel_rounding,
                    parallel_l_shape_hook_orintation=parallel_l_shape_hook_orintation,
                    parallel_distribution_rebars_check=False,
                    mesh_cover_along="Top",
                    structure=structure,
                    facename=facename,
                )
        obj.ReinforcementGroups[0].SlabsReinforcementList = slabs_reinforcements
        obj.ReinforcementGroups[0].addObjects(slabs_reinforcements)

        if (
            not obj.ColumnSecRebarsCheck
            and len(obj.ReinforcementGroups[1].RowObjectList) > 0
            and len(obj.ReinforcementGroups[1].RowObjectList[0].ColumnList) > 0
            and len(
                obj.ReinforcementGroups[1]
                .RowObjectList[0]
                .ColumnList[0]
                .RebarGroups
            )
            > 2
        ) or (
            obj.ColumnSecRebarsCheck
            and len(obj.ReinforcementGroups[1].RowObjectList) > 0
            and len(obj.ReinforcementGroups[1].RowObjectList[0].ColumnList) > 0
            and len(
                obj.ReinforcementGroups[1]
                .RowObjectList[0]
                .ColumnList[0]
                .RebarGroups
            )
            <= 2
        ):
            for cx in obj.ReinforcementGroups[1].RowObjectList:
                for column in cx.ColumnList:
                    if column:
                        self.removeColumnReinforcement(column)

        columns_container = self.getColumnsMatrix(obj.ReinforcementGroups[1])
        for cx in range(len(columns_container)):
            if cx + 1 > xdir_column_amount_value:
                for cy, column in enumerate(columns_container[cx]):
                    if column:
                        self.removeColumnReinforcement(column)
            else:
                for cy in range(len(columns_container[cx])):
                    if cy + 1 > ydir_column_amount_value:
                        column = columns_container[cx][cy]
                        if column:
                            self.removeColumnReinforcement(column)

        columns_container = self.getColumnsMatrix(obj.ReinforcementGroups[1])

        # Set given column metrix size based on input of x and y direction column count
        for x in range(xdir_column_amount_value):
            if x + 1 > len(columns_container):
                columns_container.append([])
            for y in range(ydir_column_amount_value):
                if y + 1 > len(columns_container[x]):
                    columns_container[x].append(None)

        if column_sec_rebar_check:
            for row in range(xdir_column_amount_value):
                for column in range(ydir_column_amount_value):
                    modified_l_cover_of_tie = column_left_cover + (row) * (
                        column_width + xdir_column_spacing_value
                    )
                    modified_r_cover_of_tie = (
                        top_face_width
                        - (row + 1) * (column_width)
                        - (row) * (xdir_column_spacing_value)
                    )
                    modified_t_cover_of_tie = (
                        top_face_length
                        - (column + 1) * (column_length)
                        - (column) * (ydir_column_spacing_value)
                    )
                    modified_b_cover_of_tie = column_front_cover + (column) * (
                        column_length + ydir_column_spacing_value
                    )
                    if not columns_container[row][column]:
                        columnReinforcementGroup = makeSingleTieMultipleRebars(
                            l_cover_of_tie=modified_l_cover_of_tie,
                            r_cover_of_tie=modified_r_cover_of_tie,
                            t_cover_of_tie=modified_t_cover_of_tie,
                            b_cover_of_tie=modified_b_cover_of_tie,
                            offset_of_tie=calculated_tie_offset,
                            bent_angle=tie_bent_angle,
                            extension_factor=tie_extension_factor,
                            dia_of_tie=tie_diameter,
                            number_spacing_check=tie_number_spacing_check,
                            number_spacing_value=tie_number_spacing_value,
                            dia_of_main_rebars=column_main_rebar_diameter,
                            main_rebars_t_offset=-column_main_rebars_t_offset,
                            main_rebars_b_offset=column_b_offset,
                            main_rebars_type=column_main_rebars_type,
                            main_hook_orientation=column_main_hook_orientation,
                            main_hook_extend_along=column_main_hook_extend_along,
                            l_main_rebar_rounding=column_l_main_rebar_rounding,
                            main_hook_extension=column_main_hook_extension,
                            sec_rebars_t_offset=tuple(
                                -x for x in column_sec_rebars_t_offset
                            ),
                            sec_rebars_b_offset=(
                                column_b_offset,
                                column_b_offset,
                            ),
                            sec_rebars_number_diameter=column_sec_rebars_number_diameter,
                            sec_rebars_type=column_sec_rebars_type,
                            sec_hook_orientation=column_sec_hook_orientation,
                            l_sec_rebar_rounding=column_l_sec_rebar_rounding,
                            sec_hook_extension=column_sec_hook_extension,
                            structure=structure,
                            facename=top_facename,
                        )
                        columnReinforcementGroup.RebarGroups[0].Ties[
                            0
                        ].OffsetStart = (
                            selected_face_hight
                            - column_b_offset
                            - tie_diameter
                            - tie_bottom_cover
                        )
                    else:
                        columnReinforcementGroup = editSingleTieMultipleRebars(
                            rebar_group=columns_container[row][column],
                            l_cover_of_tie=modified_l_cover_of_tie,
                            r_cover_of_tie=modified_r_cover_of_tie,
                            t_cover_of_tie=modified_t_cover_of_tie,
                            b_cover_of_tie=modified_b_cover_of_tie,
                            offset_of_tie=calculated_tie_offset,
                            bent_angle=tie_bent_angle,
                            extension_factor=tie_extension_factor,
                            dia_of_tie=tie_diameter,
                            number_spacing_check=tie_number_spacing_check,
                            number_spacing_value=tie_number_spacing_value,
                            dia_of_main_rebars=column_main_rebar_diameter,
                            main_rebars_t_offset=-column_main_rebars_t_offset,
                            main_rebars_b_offset=column_b_offset,
                            main_rebars_type=column_main_rebars_type,
                            main_hook_orientation=column_main_hook_orientation,
                            main_hook_extend_along=column_main_hook_extend_along,
                            l_main_rebar_rounding=column_l_main_rebar_rounding,
                            main_hook_extension=column_main_hook_extension,
                            sec_rebars_t_offset=tuple(
                                -x for x in column_sec_rebars_t_offset
                            ),
                            sec_rebars_b_offset=(
                                column_b_offset,
                                column_b_offset,
                            ),
                            sec_rebars_number_diameter=column_sec_rebars_number_diameter,
                            sec_rebars_type=column_sec_rebars_type,
                            sec_hook_orientation=column_sec_hook_orientation,
                            l_sec_rebar_rounding=column_l_sec_rebar_rounding,
                            sec_hook_extension=column_sec_hook_extension,
                            structure=structure,
                            facename=top_facename,
                        )
                        columnReinforcementGroup.RebarGroups[0].Ties[
                            0
                        ].OffsetStart = (
                            selected_face_hight
                            - column_b_offset
                            - tie_diameter
                            - tie_bottom_cover
                        )
                    columns_container[row][column] = columnReinforcementGroup
        else:
            for row in range(xdir_column_amount_value):
                for column in range(ydir_column_amount_value):
                    modified_l_cover_of_tie = column_left_cover + (row) * (
                        column_width + xdir_column_spacing_value
                    )
                    modified_r_cover_of_tie = (
                        top_face_width
                        - (row + 1) * (column_width)
                        - (row) * (xdir_column_spacing_value)
                    )
                    modified_t_cover_of_tie = (
                        top_face_length
                        - (column + 1) * (column_length)
                        - (column) * (ydir_column_spacing_value)
                    )
                    modified_b_cover_of_tie = column_front_cover + (column) * (
                        column_length + ydir_column_spacing_value
                    )
                    if not columns_container[row][column]:
                        columnReinforcementGroup = makeSingleTieFourRebars(
                            l_cover_of_tie=modified_l_cover_of_tie,
                            r_cover_of_tie=modified_r_cover_of_tie,
                            t_cover_of_tie=modified_t_cover_of_tie,
                            b_cover_of_tie=modified_b_cover_of_tie,
                            offset_of_tie=calculated_tie_offset,
                            bent_angle=tie_bent_angle,
                            extension_factor=tie_extension_factor,
                            dia_of_tie=tie_diameter,
                            number_spacing_check=tie_number_spacing_check,
                            number_spacing_value=tie_number_spacing_value,
                            dia_of_rebars=column_main_rebar_diameter,
                            t_offset_of_rebars=-column_main_rebars_t_offset,
                            b_offset_of_rebars=column_b_offset,
                            rebar_type=column_main_rebars_type,
                            hook_orientation=column_main_hook_orientation,
                            hook_extend_along=column_main_hook_extend_along,
                            l_rebar_rounding=column_l_main_rebar_rounding,
                            hook_extension=column_main_hook_extension,
                            structure=structure,
                            facename=top_facename,
                        ).Object
                        columnReinforcementGroup.RebarGroups[0].Ties[
                            0
                        ].OffsetStart = (
                            selected_face_hight
                            - column_b_offset
                            - tie_diameter
                            - tie_bottom_cover
                        )
                    else:
                        columnReinforcementGroup = editSingleTieFourRebars(
                            rebar_group=columns_container[row][column],
                            l_cover_of_tie=modified_l_cover_of_tie,
                            r_cover_of_tie=modified_r_cover_of_tie,
                            t_cover_of_tie=modified_t_cover_of_tie,
                            b_cover_of_tie=modified_b_cover_of_tie,
                            offset_of_tie=calculated_tie_offset,
                            bent_angle=tie_bent_angle,
                            extension_factor=tie_extension_factor,
                            dia_of_tie=tie_diameter,
                            number_spacing_check=tie_number_spacing_check,
                            number_spacing_value=tie_number_spacing_value,
                            dia_of_rebars=column_main_rebar_diameter,
                            t_offset_of_rebars=-column_main_rebars_t_offset,
                            b_offset_of_rebars=column_b_offset,
                            rebar_type=column_main_rebars_type,
                            hook_orientation=column_main_hook_orientation,
                            hook_extend_along=column_main_hook_extend_along,
                            l_rebar_rounding=column_l_main_rebar_rounding,
                            hook_extension=column_main_hook_extension,
                            structure=structure,
                            facename=top_facename,
                        )
                        columnReinforcementGroup.RebarGroups[0].Ties[
                            0
                        ].OffsetStart = (
                            selected_face_hight
                            - column_b_offset
                            - tie_diameter
                            - tie_bottom_cover
                        )
                    columns_container[row][column] = columnReinforcementGroup

        self.addColumnsGroups(obj.ReinforcementGroups[1], columns_container)
        FreeCAD.ActiveDocument.recompute()
        obj.IsMakeOrEditRequired = True

    def removeColumnReinforcement(self, column):
        """Remove column reinforcement from footing"""
        for i in range(len(column.RebarGroups)):
            for rebar_group in column.RebarGroups[i].Group:
                if i != 2:
                    base_name = rebar_group.Base.Name
                    FreeCAD.ActiveDocument.removeObject(rebar_group.Name)
                    FreeCAD.ActiveDocument.removeObject(base_name)
                else:
                    for sec_rebars_groups in rebar_group.Group:
                        base_name = sec_rebars_groups.Base.Name
                        FreeCAD.ActiveDocument.removeObject(
                            sec_rebars_groups.Name
                        )
                        FreeCAD.ActiveDocument.removeObject(base_name)
        FreeCAD.ActiveDocument.getObject(
            column.Name
        ).removeObjectsFromDocument()
        FreeCAD.ActiveDocument.removeObject(column.Name)

    def removeSlabReinforcement(self, slab):
        """Remove slab reinforcement from footing"""
        slab.IsMakeOrEditRequired = False
        for rebar in slab.Group:
            base_name = rebar.Base.Name
            FreeCAD.ActiveDocument.removeObject(rebar.Name)
            FreeCAD.ActiveDocument.removeObject(base_name)
        FreeCAD.ActiveDocument.getObject(slab.Name).removeObjectsFromDocument()
        FreeCAD.ActiveDocument.removeObject(slab.Name)

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None

    def addColumnsGroups(self, columns_obj, column_matrix):
        """Add columns groups for columns"""
        row_obj_list = []
        if len(columns_obj.Group) > 0:
            for old_row_object_group in columns_obj.Group:
                old_row_object_group.ColumnList = []
                old_row_object_group.Group = []
                if FreeCAD.GuiUp:
                    todo.delay(
                        FreeCAD.ActiveDocument.removeObject,
                        old_row_object_group.Name,
                    )
                else:
                    FreeCAD.ActiveDocument.removeObject(
                        old_row_object_group.Name
                    )

        for row in column_matrix:
            row_obj = FreeCAD.ActiveDocument.addObject(
                "App::DocumentObjectGroup", "row"
            )
            row_obj_list.append(row_obj)
            if not hasattr(row_obj, "ColumnList"):
                row_obj.addProperty(
                    "App::PropertyLinkList",
                    "ColumnList",
                    "ColumnReinforcement",
                    QT_TRANSLATE_NOOP(
                        "App::Property",
                        "List of reinforcement groups",
                    ),
                )
            row_obj.addObjects(row)
            row_obj.ColumnList = row
        columns_obj.addObjects(row_obj_list)
        columns_obj.RowObjectList = row_obj_list

    def getColumnsMatrix(self, columns_obj):
        """Get Coulumn matrix from Column Reinforcement Document object"""
        column_matrix = []
        for row_obj in columns_obj.RowObjectList:
            if len(row_obj.ColumnList) > 0:
                column_matrix.append(row_obj.ColumnList)
        return column_matrix


class _FootingReinforcementViewProviderGroup:
    """A View Provider for the Rebar Group object."""

    def __init__(self, vobj):
        vobj.Proxy = self
        self.Object = vobj.Object

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None

    def doubleClicked(self, vobj):
        """Handle double click on Footing Reinforcement object"""
        from FootingReinforcement import MainFootingReinforcement

        MainFootingReinforcement.editDialog(vobj)
