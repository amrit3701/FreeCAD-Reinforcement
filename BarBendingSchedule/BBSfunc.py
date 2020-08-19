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

__title__ = "Bar Bending Schedule Functions"
__author__ = "Suraj"
__url__ = "https://www.freecadweb.org"

from typing import Dict, Union, Tuple, List, Optional, Literal
from xml.etree import ElementTree

import FreeCAD
import WorkingPlane

from BillOfMaterial.BOMPreferences import BOMPreferences
from BillOfMaterial.BOMfunc import getReinforcementRebarObjects, fixColumnUnits
from BillOfMaterial.BillOfMaterial_SVG import makeBillOfMaterialSVG
from RebarShapeCutList.RebarShapeCutListfunc import (
    getBaseRebarsList,
    getRebarShapeCutList,
)
from SVGfunc import getSVGRootElement, getSVGRectangle, getSVGDataCell


def getBarBendingSchedule(
    rebar_objects: Optional[List] = None,
    column_headers: Optional[Dict[str, Tuple[str, int]]] = None,
    column_units: Optional[Dict[str, str]] = None,
    dia_weight_map: Optional[Dict[float, FreeCAD.Units.Quantity]] = None,
    rebar_length_type: Optional[
        Literal["RealLength", "LengthWithSharpEdges"]
    ] = None,
    font_family: Optional[str] = None,
    font_filename: Optional[str] = None,
    font_size: Optional[float] = None,
    column_width: float = 60,
    row_height: float = 30,
    rebar_shape_column_header: str = "Rebar Shape",
    rebar_shape_view_directions: Union[
        Union[FreeCAD.Vector, WorkingPlane.Plane],
        List[Union[FreeCAD.Vector, WorkingPlane.Plane]],
    ] = FreeCAD.Vector(0, 0, 0),
    rebar_shape_stirrup_extended_edge_offset: float = 2,
    rebar_shape_color_style: str = "shape color",
    rebar_shape_stroke_width: float = 0.35,
    rebar_shape_include_dimensions: bool = True,
    rebar_shape_edge_dimension_units: str = "mm",
    rebar_shape_edge_dimension_precision: int = 0,
    include_edge_dimension_units_in_dimension_label: bool = False,
    rebar_shape_bent_angle_dimension_exclude_list: Union[
        List[float], Tuple[float, ...]
    ] = (45, 90, 180),
    helical_rebar_dimension_label_format: str = "%L,r=%R,pitch=%P",
) -> ElementTree.Element:
    """Generate Bar Bending Schedule svg.

    Parameters
    ----------
    rebar_objects : list of <ArchRebar._Rebar> and <rebar2.BaseRebar>, optional
        Rebars list to generate bar bending schedule.
        If None, then all ArchRebars and rebar2.BaseRebar objects with unique
        Mark from ActiveDocument will be selected and rebars with no Mark
        assigned will be ignored.
        Default is None.
    column_headers : Dict[str, Tuple[str, int]], optional
        A dictionary with keys: "Mark", "RebarsCount", "Diameter",
        "RebarLength", "RebarsTotalLength" and values are tuple of column_header
        and its sequence number.
            e.g. {
                    "Mark": ("Mark", 1),
                    "RebarsCount": ("No. of Rebars", 2),
                    "Diameter": ("Diameter in mm", 3),
                    "RebarLength": ("Length in m/piece", 4),
                    "RebarsTotalLength": ("Total Length in m", 5),
                }
            set column sequence number to 0 to hide column.
        Default is None, to select from FreeCAD preferences.
    column_units : Dict[str, str], optional
        column_units is a dictionary with keys: "Diameter", "RebarLength",
        "RebarsTotalLength" and their corresponding units as value.
            e.g. {
                    "Diameter": "mm",
                    "RebarLength": "m",
                    "RebarsTotalLength": "m",
                }
        Default is None, to select from FreeCAD preferences.
    dia_weight_map : Dict[float, FreeCAD.Units.Quantity], optional
        A dictionary with diameter as key and corresponding weight (kg/m) as
        value.
            e.g. {
                    6: FreeCAD.Units.Quantity("0.222 kg/m"),
                    8: FreeCAD.Units.Quantity("0.395 kg/m"),
                    10: FreeCAD.Units.Quantity("0.617 kg/m"),
                    12: FreeCAD.Units.Quantity("0.888 kg/m"),
                    ...,
                }
        Default is None, to select from FreeCAD preferences.
    rebar_length_type : {"RealLength", "LengthWithSharpEdges"}, optional
        The rebar length calculations type.
        "RealLength": length of rebar considering rounded edges.
        "LengthWithSharpEdges": length of rebar assuming sharp edges of rebar.
        Default is None, to select from FreeCAD preferences.
    font_family : str, optional
        The font-family of text.
        Default is None, to select from FreeCAD preferences.
    font_filename : str, optional
        The font filename/full_path corresponding to font_family. This is
        required if you are working in pure console mode, without any gui.
        Default is None, to select from FreeCAD preferences.
    font_size : float, optional
        The font-size of text.
        Default is None, to select from FreeCAD preferences.
    column_width : float, optional
        The width of each column in bar shape cut list.
        Default is 60
    row_height : float, optional
        The height of each row in bar shape cut list.
        Default is 30
    rebar_shape_column_header : str, optional
        The column header for rebar shape column.
        Default is "Rebar Shape"
    rebar_shape_view_directions : FreeCAD.Vector or WorkingPlane.Plane
                                  OR their list, optional
        The view point directions for each rebar shape.
        Default is FreeCAD.Vector(0, 0, 0) to automatically choose
        view_directions.
    rebar_shape_stirrup_extended_edge_offset : float, optional
        The offset of extended end edges of stirrup, so that end edges of
        stirrup with 90 degree bent angle do not overlap with stirrup edges.
        Default is 2
    rebar_shape_color_style : {"shape color", "color_name",
                               "hex_value_of_color"}, optional
        The color style of rebars in rebar shape svg.
        "shape color" means select color of rebar shape.
    rebar_shape_stroke_width : float, optional
        The stroke-width of rebars in rebar shape svg.
        Default is 0.35
    rebar_shape_include_dimensions : bool, optional
        If True, then each rebar edge dimensions and bent angle dimensions will
        be included in rebar shape svg.
        Default is True.
    rebar_shape_edge_dimension_units : str, optional
        The units to be used for rebar length dimensions in rebar shape svg.
        Default is "mm".
    rebar_shape_edge_dimension_precision : int, optional
        The number of decimals that should be shown for rebar length as
        dimension label in rebar shape svg. Set it to None to use user preferred
        unit precision from FreeCAD unit preferences.
        Default is 0
    include_edge_dimension_units_in_dimension_label : bool, optional
        If it is True, then rebar length units will be shown in dimension label
        in rebar shape svg.
        Default is False.
    rebar_shape_bent_angle_dimension_exclude_list : list of float, optional
        The list of bent angles to not include their dimensions in rebar shape.
        Default is (45, 90, 180).
    helical_rebar_dimension_label_format : str, optional
        The format of helical rebar dimension label in rebar shape svg.
            %L -> Length of helical rebar
            %R -> Helix radius of helical rebar
            %P -> Helix pitch of helical rebar
        Default is "%L,r=%R,pitch=%P".

    Returns
    -------
    ElementTree.Element
        The generated bar bending schedule svg.
    """
    rebar_objects = getReinforcementRebarObjects(rebar_objects)
    bom_preferences = BOMPreferences()
    if not column_headers:
        column_headers = bom_preferences.getColumnHeaders()
    if not column_units:
        column_units = bom_preferences.getColumnUnits()
    column_units = fixColumnUnits(column_units or {})

    svg_pref = bom_preferences.getSVGPrefGroup()
    if not font_family:
        font_family = svg_pref.GetString("FontFamily")
    if not font_size:
        font_size = svg_pref.GetFloat("FontSize")

    svg = getSVGRootElement()

    bom_svg = makeBillOfMaterialSVG(
        column_headers,
        column_units,
        dia_weight_map,
        rebar_length_type,
        font_family,
        font_filename,
        font_size,
        column_width,
        row_height,
        rebar_objects=rebar_objects,
        return_svg_only=True,
    )
    bom_table_svg = bom_svg.find("./g[@id='BOM_table']")
    svg.append(bom_table_svg)

    bom_width = float(bom_svg.get("width").replace("mm", ""))
    column_header_height = row_height * (
        2 if "RebarsTotalLength" in column_headers else 1
    )
    # Add column header for rebar shape cut list
    rebar_shape_cut_list_header = getSVGDataCell(
        rebar_shape_column_header,
        bom_width,
        0,
        column_width,
        column_header_height,
        font_family,
        font_size,
    )
    svg.append(rebar_shape_cut_list_header)

    bar_cut_list_svg = getRebarShapeCutList(
        getBaseRebarsList(rebar_objects),
        rebar_shape_view_directions,
        False
        if "Mark" in column_headers and column_headers["Mark"][1] != 0
        else True,
        rebar_shape_stirrup_extended_edge_offset,
        rebar_shape_stroke_width,
        rebar_shape_color_style,
        rebar_shape_include_dimensions,
        rebar_shape_edge_dimension_units,
        rebar_shape_edge_dimension_precision,
        include_edge_dimension_units_in_dimension_label,
        rebar_shape_bent_angle_dimension_exclude_list,
        font_family,
        font_size,
        helical_rebar_dimension_label_format,
        row_height,
        column_width,
        horizontal_rebar_shape=True,
    ).find("./g[@id='RebarShapeCutList']")
    svg.append(bar_cut_list_svg)

    # Translate rebar shape cut list to last column and set top offset =
    # height of column headers
    bar_cut_list_svg.set(
        "transform", "translate({} {})".format(bom_width, column_header_height)
    )

    total_separator = bom_svg.find(
        ".//*[@id='bom_table_cell_column_separator']",
    )
    total_separator_width = float(total_separator.get("width"))
    total_separator.set("width", str(total_separator_width + column_width))
    total_separator_y = float(total_separator.get("y"))
    total_separator_height = float(total_separator.get("height"))
    for x in range(0, 3):
        svg.append(
            getSVGRectangle(
                bom_width,
                total_separator_y + total_separator_height + x * row_height,
                column_width,
                row_height,
            )
        )

    bom_height = float(bom_svg.get("height").replace("mm", ""))
    svg_width = bom_width + column_width
    svg.set("width", str(svg_width) + "mm")
    svg.set("height", str(bom_height) + "mm")
    svg.set("viewBox", "0 0 {} {}".format(svg_width, bom_height))

    return svg
