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

from typing import (
    Dict,
    List,
    Literal,
    Optional,
    OrderedDict as OrderedDictType,
    Tuple,
    Union,
)
from xml.dom import minidom
from xml.etree import ElementTree

import FreeCAD
import WorkingPlane

from BillOfMaterial.BOMPreferences import BOMPreferences
from BillOfMaterial.BOMfunc import (
    getReinforcementRebarObjects,
    getHostReinforcementsDict,
    fixColumnUnits,
)
from BillOfMaterial.BillOfMaterial_SVG import makeBillOfMaterialSVG
from RebarShapeCutList.RebarShapeCutListfunc import (
    getBaseRebarsList,
    getRebarShapeCutList,
)
from SVGfunc import getSVGRootElement, getSVGRectangle, getSVGDataCell


def getBarBendingSchedule(
    rebar_objects: Optional[List] = None,
    column_headers: Optional[
        OrderedDictType[
            Literal[
                "Host",
                "Mark",
                "RebarsCount",
                "Diameter",
                "RebarLength",
                "RebarsTotalLength",
            ],
            str,
        ]
    ] = None,
    column_units: Optional[
        Dict[Literal["Diameter", "RebarLength", "RebarsTotalLength"], str]
    ] = None,
    dia_weight_map: Optional[Dict[float, FreeCAD.Units.Quantity]] = None,
    rebar_length_type: Optional[
        Literal["RealLength", "LengthWithSharpEdges"]
    ] = None,
    reinforcement_group_by: Optional[Literal["Mark", "Host"]] = None,
    font_family: Optional[str] = None,
    font_size: float = 5,
    column_width: float = 60,
    row_height: float = 30,
    rebar_shape_column_header: str = "Rebar Shape (mm)",
    rebar_shape_view_directions: Union[
        Union[FreeCAD.Vector, WorkingPlane.Plane],
        List[Union[FreeCAD.Vector, WorkingPlane.Plane]],
    ] = FreeCAD.Vector(0, 0, 0),
    rebar_shape_stirrup_extended_edge_offset: float = 2,
    rebar_shape_color_style: str = "shape color",
    rebar_shape_stroke_width: float = 0.35,
    rebar_shape_include_dimensions: bool = True,
    rebar_shape_dimension_font_size: float = 3,
    rebar_shape_edge_dimension_units: str = "mm",
    rebar_shape_edge_dimension_precision: int = 0,
    include_edge_dimension_units_in_dimension_label: bool = False,
    rebar_shape_bent_angle_dimension_exclude_list: Union[
        List[float], Tuple[float, ...]
    ] = (45, 90, 180),
    helical_rebar_dimension_label_format: str = "%L,r=%R,pitch=%P",
    output_file: Optional[str] = None,
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
    column_headers : OrderedDict[{"Host", "Mark", "RebarsCount", "Diameter",
                        "RebarLength", "RebarsTotalLength"}, str], optional
        An ordered dictionary with keys: "Mark", "RebarsCount", "Diameter",
        "RebarLength", "RebarsTotalLength" and values column display headers.
            e.g. {
                    "Host": "Member",
                    "Mark": "Mark",
                    "RebarsCount": "No. of Rebars",
                    "Diameter": "Diameter in mm",
                    "RebarLength": "Length in m/piece",
                    "RebarsTotalLength": "Total Length in m",
                }
        Default is None, to select from FreeCAD Reinforcement BOM preferences.
    column_units : dict of ({"Diameter", "RebarLength", "RebarsTotalLength"},
                    str), optional
        column_units is a dictionary with keys: "Diameter", "RebarLength",
        "RebarsTotalLength" and their corresponding units as value.
            e.g. {
                    "Diameter": "mm",
                    "RebarLength": "m",
                    "RebarsTotalLength": "m",
                }
        Default is None, to select from FreeCAD Reinforcement BOM preferences.
    dia_weight_map : dict of (float, FreeCAD.Units.Quantity), optional
        A dictionary with diameter as key and corresponding weight (kg/m) as
        value.
            e.g. {
                    6: FreeCAD.Units.Quantity("0.222 kg/m"),
                    8: FreeCAD.Units.Quantity("0.395 kg/m"),
                    10: FreeCAD.Units.Quantity("0.617 kg/m"),
                    12: FreeCAD.Units.Quantity("0.888 kg/m"),
                    ...,
                }
        Default is None, to select from FreeCAD Reinforcement BOM preferences.
    rebar_length_type : {"RealLength", "LengthWithSharpEdges"}, optional
        The rebar length calculations type.
        "RealLength": length of rebar considering rounded edges.
        "LengthWithSharpEdges": length of rebar assuming sharp edges of rebar.
        Default is None, to select from FreeCAD Reinforcement BOM preferences.
    reinforcement_group_by: {"Mark", "Host"}, optional
        Specifies how reinforcement objects should be grouped.
        Default is None, to select from FreeCAD Reinforcement BOM preferences.
    font_family : str, optional
        The font-family of text.
        Default is None, to select from FreeCAD Reinforcement BOM preferences.
    font_size : float
        The font-size of text.
        Default is 5
    column_width : float
        The width of each column in bar shape cut list.
        Default is 60
    row_height : float
        The height of each row in bar shape cut list.
        Default is 30
    rebar_shape_column_header : str
        The column header for rebar shape column.
        Default is "Rebar Shape (mm)"
    rebar_shape_view_directions : FreeCAD.Vector or WorkingPlane.Plane
                                  OR their list
        The view point directions for each rebar shape.
        Default is FreeCAD.Vector(0, 0, 0) to automatically choose
        view_directions.
    rebar_shape_stirrup_extended_edge_offset : float
        The offset of extended end edges of stirrup, so that end edges of
        stirrup with 90 degree bent angle do not overlap with stirrup edges.
        Default is 2
    rebar_shape_color_style : {"shape color", "color_name","hex_value_of_color"}
        The color style of rebars in rebar shape svg.
        "shape color" means select color of rebar shape.
    rebar_shape_stroke_width : float
        The stroke-width of rebars in rebar shape svg.
        Default is 0.35
    rebar_shape_include_dimensions : bool
        If True, then each rebar edge dimensions and bent angle dimensions will
        be included in rebar shape svg.
        Default is True.
    rebar_shape_dimension_font_size: float
        The font size of dimension text in rebar shape svg.
        Default is 3
    rebar_shape_edge_dimension_units : str
        The units to be used for rebar length dimensions in rebar shape svg.
        Default is "mm".
    rebar_shape_edge_dimension_precision : int
        The number of decimals that should be shown for rebar length as
        dimension label in rebar shape svg. Set it to None to use user preferred
        unit precision from FreeCAD unit preferences.
        Default is 0
    include_edge_dimension_units_in_dimension_label : bool
        If it is True, then rebar length units will be shown in dimension label
        in rebar shape svg.
        Default is False.
    rebar_shape_bent_angle_dimension_exclude_list : tuple of float
        The tuple of bent angles to not include their dimensions in rebar shape.
        Default is (45, 90, 180).
    helical_rebar_dimension_label_format : str
        The format of helical rebar dimension label in rebar shape svg.
            %L -> Length of helical rebar
            %R -> Helix radius of helical rebar
            %P -> Helix pitch of helical rebar
        Default is "%L,r=%R,pitch=%P".
    output_file: str, optional
        The output file to write generated svg.

    Returns
    -------
    ElementTree.Element
        The generated bar bending schedule svg.
    """
    rebar_objects = getReinforcementRebarObjects(rebar_objects)
    bom_preferences = BOMPreferences()
    column_headers = column_headers or bom_preferences.getColumnHeaders()
    column_units = column_units or bom_preferences.getColumnUnits()
    column_units = fixColumnUnits(column_units)
    reinforcement_group_by = (
        reinforcement_group_by or bom_preferences.getReinforcementGroupBy()
    )

    svg_pref = bom_preferences.getSVGPrefGroup()
    font_family = font_family or svg_pref.GetString("FontFamily")
    font_size = font_size or svg_pref.GetFloat("FontSize")

    svg = getSVGRootElement()
    bbs_svg = ElementTree.Element("g", attrib={"id": "BBS"})
    svg.append(bbs_svg)

    bom_svg = makeBillOfMaterialSVG(
        column_headers,
        column_units,
        dia_weight_map,
        rebar_length_type,
        font_family,
        font_size=font_size,
        column_width=column_width,
        row_height=row_height,
        rebar_objects=rebar_objects,
        reinforcement_group_by=reinforcement_group_by,
        return_svg_only=True,
    )
    bom_table_svg = bom_svg.find("./g[@id='BOM_table']")
    bbs_svg.append(bom_table_svg)

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
        font_weight="bold",
    )
    bbs_svg.append(rebar_shape_cut_list_header)

    base_rebars_list = []
    if reinforcement_group_by == "Mark":
        base_rebars_list = getBaseRebarsList(rebar_objects)
    else:
        host_reinforcement_dict = getHostReinforcementsDict(rebar_objects)
        for reinforcement_list in host_reinforcement_dict.values():
            base_rebars_list.extend(getBaseRebarsList(reinforcement_list))

    bar_cut_list_svg = getRebarShapeCutList(
        base_rebars_list,
        rebar_shape_view_directions,
        False if "Mark" in column_headers else True,
        rebar_shape_stirrup_extended_edge_offset,
        rebar_shape_stroke_width,
        rebar_shape_color_style,
        rebar_shape_include_dimensions,
        rebar_shape_edge_dimension_units,
        rebar_shape_edge_dimension_precision,
        include_edge_dimension_units_in_dimension_label,
        rebar_shape_bent_angle_dimension_exclude_list,
        font_family,
        rebar_shape_dimension_font_size,
        helical_rebar_dimension_label_format,
        row_height,
        column_width,
        column_count=1,
        horizontal_rebar_shape=True,
    ).find("./g[@id='RebarShapeCutList']")
    bbs_svg.append(bar_cut_list_svg)

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
        bbs_svg.append(
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

    if output_file:
        svg_sheet = minidom.parseString(
            ElementTree.tostring(svg, encoding="unicode")
        ).toprettyxml(indent="  ")
        try:
            with open(output_file, "w", encoding="utf-8") as svg_output_file:
                svg_output_file.write(svg_sheet)
        except OSError:
            FreeCAD.Console.PrintError(
                "Error writing svg to file " + str(svg_output_file) + "\n"
            )

    return svg
