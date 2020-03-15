# Rebar Addon for FreeCAD
This project aims to facilitate flexible implementation and usage of Rebaring in FreeCAD. In this project, a list of rebars will be provided in the user interface under the Rebar tools in the form of a dropdown list. This endeavor started as a [Google Summer of Code](https://en.wikipedia.org/wiki/Google_Summer_of_Code) (GSOC 2017) [project](https://summerofcode.withgoogle.com/archive/2017/projects/6536382147198976).

Added new features of beam and column reinforcement as Google Summer of Code ([GSOC](https://en.wikipedia.org/wiki/Google_Summer_of_Code) 2019) [project](https://summerofcode.withgoogle.com/projects/#4615685316018176)

![screenshot](http://i.imgur.com/r9b5l7K.jpg)

## Documentation
### Developer
* [Web](https://amrit3701.github.io/FreeCAD-Reinforcement/html/index.html)
* [PDF](https://amrit3701.github.io/FreeCAD-Reinforcement/latex/refman.pdf)

### User
This project currently covers six different rebar shapes as given below:

- ![icon](https://www.freecadweb.org/wiki/images/thumb/6/69/Arch_Rebar_Straight.png/32px-Arch_Rebar_Straight.png) **Straight Rebar**: [wiki](https://www.freecadweb.org/wiki/Arch_Rebar_Straight)
![screenshot](https://www.freecadweb.org/wiki/images/f/fd/StraightRebar.png)

- ![icon](https://www.freecadweb.org/wiki/images/thumb/4/4d/Arch_Rebar_UShape.png/32px-Arch_Rebar_UShape.png) **UShape Rebar**: [wiki](https://www.freecadweb.org/wiki/Arch_Rebar_UShape)
![screenshot](https://www.freecadweb.org/wiki/images/3/35/Footing_UShapeRebar.png)

- ![icon](https://www.freecadweb.org/wiki/images/thumb/3/38/Arch_Rebar_LShape.png/32px-Arch_Rebar_LShape.png) **LShape Rebar**: [wiki](https://www.freecadweb.org/wiki/Arch_Rebar_LShape)
![screenshot](https://www.freecadweb.org/wiki/images/1/10/LShapeRebarNew.png)

- ![icon](https://www.freecadweb.org/wiki/images/thumb/0/0b/Arch_Rebar_BentShape.png/32px-Arch_Rebar_BentShape.png) **BentShpae Rebar**: [wiki](https://www.freecadweb.org/wiki/Arch_Rebar_BentShape)
![screenshot](https://www.freecadweb.org/wiki/images/e/e3/BentShapeRebar.png)

- ![icon](https://www.freecadweb.org/wiki/images/thumb/e/ef/Arch_Rebar_Stirrup.png/32px-Arch_Rebar_Stirrup.png) **Stirrup Rebar**: [wiki](https://www.freecadweb.org/wiki/Arch_Rebar_Stirrup)
![screenshot](https://www.freecadweb.org/wiki/images/9/9b/Stirrup.png)

- ![icon](https://www.freecadweb.org/wiki/images/thumb/c/c9/Arch_Rebar_Helical.png/32px-Arch_Rebar_Helical.png) **Helical Rebar**: [wiki](https://www.freecadweb.org/wiki/Arch_Rebar_Helical)
![screenshot](https://www.freecadweb.org/wiki/images/2/2f/HelicalRebar.png)

- ![icon](https://www.freecadweb.org/wiki/images/thumb/3/3b/Arch_Rebar_ColumnReinforcement.png/20px-Arch_Rebar_ColumnReinforcement.png) **Column Reinforcement**: [wiki](https://www.freecadweb.org/wiki/Arch_Rebar_ColumnReinforcement)

<kbd>![screenshot](https://www.freecadweb.org/wiki/images/3/3f/Arch_Rebar_ColumnReinforcement_example.png)</kbd>

- ![icon](https://www.freecadweb.org/wiki/images/thumb/3/3b/Arch_Rebar_ColumnReinforcement.png/20px-Arch_Rebar_ColumnReinforcement.png) **TwoTiesSixRebars Column Reinforcement**: [wiki](https://www.freecadweb.org/wiki/Arch_Rebar_ColumnReinforcement_TwoTiesSixRebars)

<kbd>![screenshot](https://www.freecadweb.org/wiki/images/c/ce/Arch_Rebar_ColumnReinforcement_TwoTies_example.png)</kbd>

- ![icon](https://www.freecadweb.org/wiki/images/thumb/0/02/Arch_Rebar_BeamReinforcement.png/30px-Arch_Rebar_BeamReinforcement.png) **Beam Reinforcement**: [wiki](https://www.freecadweb.org/wiki/Arch_Rebar_BeamReinforcement)

<kbd>![screenshot](https://www.freecadweb.org/wiki/images/4/42/Arch_Rebar_BeamReinforcement_example.png)</kbd>

## Video Tutorial
[![IMAGE ALT TEXT HERE](http://i.imgur.com/ZQGCQoe.png)](https://www.youtube.com/watch?v=BYQQjEKmx5E&t=1435s)


## Installation

### Pre-requisites
- FreeCAD (version >= 0.17): [Installation guide](https://www.freecadweb.org/wiki/Installing)
 
### Steps to install Rebar Addon in FreeCAD
1. Open the FreeCAD Addon Manager (`Tool -> Addon manager`).
2. Within the Addon Manager select `Reinforcement` from a list of the workbenches shown.
3. After selecting, click on the `Install/Update` button.
4. Restart FreeCAD.
5. Now you will see different rebars in a drop-down list of rebar tools (`Arch -> Rebar tools -> Different rebars`).

## How it works
Each rebar tool has two files, one is a `python` (AKA `.py`) file and the second is its respective `UI` (AKA `.ui`) file. For example: ```StraightRebar.py``` and `StraightRebar.ui`. 

Let's continue with the straight rebar tool as the example. In the `StraightRebar.py` file, there are two functions:   
1. The `makeStraightRebar()` function, this function creates straight rebar and adds new properties to the default `Rebar` object. 
2. The `editStraightRebar()` function, this function is used when we want to change new properties of the rebar object to take a `Rebar` object as input (which is created by `makeStraightRebar` function). 

Within the `StraightRebar.py` file we find the `_StraightRebarTaskPanel` class present. This class loads the UI (within the `StriaghtRebar.ui` file) in to a FreeCAD task panel. When a user clicks on the `Apply` or the `Ok` button, the `makeStraightRebar` function is executed and after that when the user wants to change the properties of Straight rebar then the `editStraightRebar()` function is executed.


## Extras (GSoC 2017)
- [FreeCAD forum thread](https://forum.freecadweb.org/viewtopic.php?f=8&t=22760)
- [GSoC proposal](https://brlcad.org/wiki/User:Amritpal_singh/gsoc_proposal)
- [Development logs](https://brlcad.org/wiki/User:Amritpal_singh/GSoC17/logs)

## Extras (GSoC 2019)
- [FreeCAD forum thread](https://forum.freecadweb.org/viewtopic.php?f=8&t=35077)
- [GSoC proposal](https://www.freecadweb.org/wiki/User:Suraj_Dadral/gsoc_proposal)
- [Development logs](https://www.freecadweb.org/wiki/User:Suraj_Dadral/GSoC19/logs)
