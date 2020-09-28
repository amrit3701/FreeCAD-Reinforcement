# -*- coding: utf-8 -*-
# ***************************************************************************
# *                                                                         *
# *   Copyright (c) 2020 - Suraj <dadralj18@gmail.com>                      *
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

__title__ = "Bill of Material Content Object"
__author__ = "Suraj"
__url__ = "https://www.freecadweb.org"


import re
from xml.etree import ElementTree
from PySide2.QtCore import QT_TRANSLATE_NOOP
import FreeCAD

from .BOMfunc import getStringWidth
from SVGfunc import getTechdrawViewScalingFactor


class BOMContent:
    """A Rebars Bill of Material SVG Content object."""

    def __init__(self, obj_name):
        """Initialize BOMContent object."""
        bom_content = FreeCAD.ActiveDocument.addObject(
            "TechDraw::DrawViewSymbolPython", obj_name
        )
        self.setProperties(bom_content)
        self.Object = bom_content
        bom_content.Proxy = self

    def setProperties(self, obj):
        """Add properties to BOMContent object."""
        self.Type = "BOMContent"

        if not hasattr(obj, "Font"):
            obj.addProperty(
                "App::PropertyFont",
                "Font",
                "BOMContent",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The font family of Bill of Material content",
                ),
            )
            obj.Font = "DejaVu Sans"

        if not hasattr(obj, "FontFilename"):
            obj.addProperty(
                "App::PropertyFile",
                "FontFilename",
                "BOMContent",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The font filename for font of Bill of Material content and"
                    " is required for working in pure console mode",
                ),
            )
            obj.FontFilename = "DejaVuSans.ttf"
        obj.setEditorMode("FontFilename", 2)

        if not hasattr(obj, "FontSize"):
            obj.addProperty(
                "App::PropertyLength",
                "FontSize",
                "BOMContent",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The font size of Bill of Material content",
                ),
            )
            obj.FontSize = 3

        if not hasattr(obj, "Template"):
            obj.addProperty(
                "App::PropertyLink",
                "Template",
                "BOMContent",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The template for Bill of Material content",
                ),
            )

        if not hasattr(obj, "Width"):
            obj.addProperty(
                "App::PropertyLength",
                "Width",
                "BOMContent",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The width of Bill of Material content",
                ),
            )
        obj.setEditorMode("Width", 2)

        if not hasattr(obj, "Height"):
            obj.addProperty(
                "App::PropertyLength",
                "Height",
                "BOMContent",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The height of Bill of Material content",
                ),
            )
        obj.setEditorMode("Height", 2)

        if not hasattr(obj, "LeftOffset"):
            obj.addProperty(
                "App::PropertyLength",
                "LeftOffset",
                "BOMContent",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The left offset of Bill of Material content",
                ),
            )
            obj.LeftOffset = 6

        if not hasattr(obj, "TopOffset"):
            obj.addProperty(
                "App::PropertyLength",
                "TopOffset",
                "BOMContent",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The top offset of Bill of Material content",
                ),
            )
            obj.TopOffset = 6

        if not hasattr(obj, "MinRightOffset"):
            obj.addProperty(
                "App::PropertyLength",
                "MinRightOffset",
                "BOMContent",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The minimum right offset of Bill of Material content",
                ),
            )
            obj.MinRightOffset = 6

        if not hasattr(obj, "MinBottomOffset"):
            obj.addProperty(
                "App::PropertyLength",
                "MinBottomOffset",
                "BOMContent",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The minimum bottom offset of Bill of Material content",
                ),
            )
            obj.MinBottomOffset = 6

        if not hasattr(obj, "MaxWidth"):
            obj.addProperty(
                "App::PropertyLength",
                "MaxWidth",
                "BOMContent",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The maximum width of Bill of Material content",
                ),
            )
            obj.MaxWidth = 190

        if not hasattr(obj, "MaxHeight"):
            obj.addProperty(
                "App::PropertyLength",
                "MaxHeight",
                "BOMContent",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The maximum height of Bill of Material content",
                ),
            )
            obj.MaxHeight = 250

        if not hasattr(obj, "PrefColumnWidth"):
            obj.addProperty(
                "App::PropertyLength",
                "PrefColumnWidth",
                "BOMContent",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The preferred column width of table of Bill of Material "
                    "content",
                ),
            )
            obj.PrefColumnWidth = 30

        if not hasattr(obj, "ColumnWidth"):
            obj.addProperty(
                "App::PropertyLength",
                "ColumnWidth",
                "BOMContent",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The column width of table of Bill of Material content",
                ),
            )
            obj.ColumnWidth = 30
        obj.setEditorMode("ColumnWidth", 2)

        if not hasattr(obj, "PrefRowHeight"):
            obj.addProperty(
                "App::PropertyLength",
                "PrefRowHeight",
                "BOMContent",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The preferred row height of table of Bill of Material "
                    "content",
                ),
            )
            obj.PrefRowHeight = 10

        if not hasattr(obj, "RowHeight"):
            obj.addProperty(
                "App::PropertyLength",
                "RowHeight",
                "BOMContent",
                QT_TRANSLATE_NOOP(
                    "App::Property",
                    "The row height of table of Bill of Material content",
                ),
            )
            obj.RowHeight = 10
        obj.setEditorMode("RowHeight", 2)

    def onDocumentRestored(self, obj):
        """Upgrade BOMContent object."""
        self.setProperties(obj)

    def execute(self, obj):
        """This function is executed to recompute BOMContent object."""
        if not obj.Symbol:
            return

        if obj.Font:
            obj.Symbol = re.sub(
                'font-family="([^"]+)"',
                'font-family="{}"'.format(obj.Font),
                obj.Symbol,
            )

        if obj.FontSize:
            obj.Symbol = re.sub(
                'font-size="([^"]+)"',
                'font-size="{}"'.format(obj.FontSize.Value),
                obj.Symbol,
            )

        self.setColumnWidth(obj)
        self.setRowHeight(obj)

        if obj.Width and obj.Height and obj.Template:
            scaling_factor = getTechdrawViewScalingFactor(
                obj.Width.Value,
                obj.Height.Value,
                obj.LeftOffset.Value,
                obj.TopOffset.Value,
                obj.Template.Width.Value,
                obj.Template.Height.Value,
                obj.MinRightOffset.Value,
                obj.MinBottomOffset.Value,
                obj.MaxWidth.Value,
                obj.MaxHeight.Value,
            )
            obj.X = obj.Width.Value * scaling_factor / 2 + obj.LeftOffset.Value
            obj.Y = (
                obj.Template.Height.Value
                - obj.Height.Value * scaling_factor / 2
                - obj.TopOffset.Value
            )
            obj.Scale = scaling_factor
        if FreeCAD.GuiUp:
            obj.ViewObject.update()

    @staticmethod
    def getColumnWidth(bom_content_obj):
        font_size = bom_content_obj.FontSize.Value
        font_family = bom_content_obj.Font
        font_filename = bom_content_obj.FontFilename
        min_column_width = 0

        namespace = {"xmlns": "http://www.w3.org/2000/svg"}
        bom_content = ElementTree.fromstring(bom_content_obj.Symbol)
        prev_column_width = bom_content_obj.ColumnWidth.Value

        column_count = int(bom_content_obj.Width.Value / prev_column_width)
        for col_seq in range(1, column_count + 1):
            text_elements = bom_content.findall(
                ".//*[@id='bom_table_cell_column_{}']/xmlns:text".format(
                    col_seq
                ),
                namespace,
            )
            for text_element in text_elements:
                text = text_element.text
                min_column_width = max(
                    min_column_width,
                    getStringWidth(text, font_size, font_family, font_filename),
                )

        multi_column_text_elements = bom_content.findall(
            ".//*[@id='bom_table_cell_column_multi_column']/xmlns:text",
            namespace,
        )
        multi_column_rect_elements = bom_content.findall(
            ".//*[@id='bom_table_cell_column_multi_column']/xmlns:rect",
            namespace,
        )
        for i, text_element in enumerate(multi_column_text_elements):
            text = text_element.text
            text_width = getStringWidth(
                text, font_size, font_family, font_filename
            )
            rect_width = float(multi_column_rect_elements[i].get("width"))
            col_span = int(rect_width / prev_column_width)
            available_width = col_span * bom_content_obj.PrefColumnWidth.Value
            if text_width > available_width:
                text_width_per_column = text_width / col_span
                min_column_width = max(min_column_width, text_width_per_column)
        return min_column_width

    def setColumnWidth(self, bom_content_obj):
        pref_column_width = bom_content_obj.PrefColumnWidth.Value
        column_width = self.getColumnWidth(bom_content_obj) + 4
        if column_width < pref_column_width:
            column_width = pref_column_width

        namespace = {"xmlns": "http://www.w3.org/2000/svg"}
        ElementTree.register_namespace("", "http://www.w3.org/2000/svg")
        bom_content = ElementTree.fromstring(bom_content_obj.Symbol)

        column_count = int(
            bom_content_obj.Width.Value / bom_content_obj.ColumnWidth.Value
        )
        for col_seq in range(1, column_count + 1):
            rectangle_elements = bom_content.findall(
                ".//*[@id='bom_table_cell_column_{}']/xmlns:rect".format(
                    col_seq
                ),
                namespace,
            )
            text_elements = bom_content.findall(
                ".//*[@id='bom_table_cell_column_{}']/xmlns:text".format(
                    col_seq
                ),
                namespace,
            )
            for row in range(len(rectangle_elements)):
                rectangle_elements[row].set("width", str(column_width))
                rectangle_elements[row].set(
                    "x", str(column_width * (col_seq - 1))
                )
                text_elements[row].set(
                    "x", str(column_width * (col_seq - 1) + column_width / 2)
                )
            cell_elements = bom_content.findall(
                ".//*xmlns:rect[@id='bom_table_cell_column_{}']".format(
                    col_seq
                ),
                namespace,
            )
            for cell in cell_elements:
                cell.set("width", str(column_width))
                cell.set("x", str(column_width * (col_seq - 1)))

        multi_column_rect_elements = bom_content.findall(
            ".//*[@id='bom_table_cell_column_multi_column']/xmlns:rect",
            namespace,
        )
        multi_column_text_elements = bom_content.findall(
            ".//*[@id='bom_table_cell_column_multi_column']/xmlns:text",
            namespace,
        )
        for i, rect_element in enumerate(multi_column_rect_elements):
            col_span = int(
                float(rect_element.get("width"))
                / bom_content_obj.ColumnWidth.Value
            )
            col_seq = (
                int(
                    float(rect_element.get("x"))
                    / bom_content_obj.ColumnWidth.Value
                )
                + 1
            )
            rect_element.set("width", str(column_width * col_span))
            rect_element.set("x", str(column_width * (col_seq - 1)))
            multi_column_text_elements[i].set(
                "x",
                str(column_width * (col_seq - 1) + column_width * col_span / 2),
            )

        total_separator = bom_content.find(
            ".//*[@id='bom_table_cell_column_separator']",
        )
        if total_separator is not None:
            total_separator.set("width", str(column_count * column_width))

        bom_content.set(
            "viewBox",
            "0 0 {} {}".format(
                column_count * column_width, bom_content_obj.Height.Value
            ),
        )
        bom_content.set("width", "{}mm".format(column_count * column_width))
        bom_content_obj.ColumnWidth = column_width
        bom_content_obj.Width = column_count * column_width
        bom_content_obj.Symbol = ElementTree.tostring(
            bom_content, encoding="unicode"
        )

    @staticmethod
    def getRowHeight(bom_content_obj):
        return max(
            bom_content_obj.PrefRowHeight.Value,
            bom_content_obj.FontSize.Value * 1.618,
        )

    def setRowHeight(self, bom_content_obj):
        row_height = self.getRowHeight(bom_content_obj)

        namespace = {"xmlns": "http://www.w3.org/2000/svg"}
        ElementTree.register_namespace("", "http://www.w3.org/2000/svg")
        bom_content = ElementTree.fromstring(bom_content_obj.Symbol)

        text_elements = bom_content.findall(".//xmlns:text", namespace)
        for text_element in text_elements:
            preceding_row_count = int(
                float(text_element.get("y")) / bom_content_obj.RowHeight.Value
            )
            offset = (
                float(text_element.get("y")) % bom_content_obj.RowHeight.Value
            )
            text_element.set(
                "y",
                str(
                    preceding_row_count * row_height
                    + offset * row_height / bom_content_obj.RowHeight.Value
                ),
            )

        rect_elements = bom_content.findall(".//xmlns:rect", namespace)
        for rect_element in rect_elements:
            preceding_row_count = int(
                float(rect_element.get("y")) / bom_content_obj.RowHeight.Value
            )
            rect_element.set("y", str(preceding_row_count * row_height))
            row_span = int(
                float(rect_element.get("height"))
                / bom_content_obj.RowHeight.Value
            )
            rect_element.set("height", str(row_span * row_height))

        row_count = int(
            bom_content_obj.Height.Value / bom_content_obj.RowHeight.Value
        )
        bom_content.set(
            "viewBox",
            "0 0 {} {}".format(
                bom_content_obj.Width.Value, row_count * row_height
            ),
        )
        bom_content.set("height", "{}mm".format(row_count * row_height))
        bom_content_obj.RowHeight = row_height
        bom_content_obj.Height = row_count * row_height
        bom_content_obj.Symbol = ElementTree.tostring(
            bom_content, encoding="unicode"
        )

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None


def makeBOMObject(template_file):
    """Create BillOfMaterial object to store BOM svg."""
    bom_object = FreeCAD.ActiveDocument.addObject(
        "TechDraw::DrawPage", "BOM_object"
    )
    template = FreeCAD.ActiveDocument.addObject(
        "TechDraw::DrawSVGTemplate", "Template"
    )
    template.Template = str(template_file)
    bom_object.Template = template
    bom_content = BOMContent("BOM_content").Object
    bom_object.addView(bom_content)
    FreeCAD.ActiveDocument.recompute()
    return bom_object
