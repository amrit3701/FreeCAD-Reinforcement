from PySide.QtCore import QT_TRANSLATE_NOOP
import FreeCADGui, FreeCAD
import os

class StraightRebarTool:

    def GetResources(self):
        return {'Pixmap'  : os.path.split(os.path.abspath(__file__))[0]+'/icons/StraightRebar.svg',
                'MenuText': QT_TRANSLATE_NOOP("Arch_Rebar_Straight", "Straight Rebar"),
                'ToolTip' : QT_TRANSLATE_NOOP("Arch_Rebar_Straight", "Creates a Striaght bar reinforcement from the selected face of the Structural element.")}

    def IsActive(self):
        if FreeCADGui.ActiveDocument:
            return True
        else:
            return False

    def Activated(self):
        import StraightRebar
        # Call to CommandStraightRebar() function
        StraightRebar.CommandStraightRebar()

class UShapeRebarTool:

    def GetResources(self):
        return {'Pixmap'  : os.path.split(os.path.abspath(__file__))[0]+'/icons/UShapeRebar.svg',
                'MenuText': QT_TRANSLATE_NOOP("Arch_Rebar_UShape", "U-Shape Rebar"),
                'ToolTip' : QT_TRANSLATE_NOOP("Arch_Rebar_UShape", "Creates a U-Shape bar reinforcement from the selected face of the Structural element.")}

    def IsActive(self):
        if FreeCADGui.ActiveDocument:
            return True
        else:
            return False

    def Activated(self):
        import UShapeRebar
        # Call to CommandUShaepRebar() function
        UShapeRebar.CommandUShapeRebar()

FreeCADGui.addCommand('Arch_Rebar_Straight', StraightRebarTool())
FreeCADGui.addCommand('Arch_Rebar_UShape', UShapeRebarTool())

# List of all rebar commands
RebarCommands = ["Arch_Rebar_Straight", "Arch_Rebar_UShape"]
