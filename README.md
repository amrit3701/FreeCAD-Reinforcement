# Rebar Addon for FreeCAD

Started as a Google Summer of Code ([GSoC](https://en.wikipedia.org/wiki/Google_Summer_of_Code) 2016) [project](https://summerofcode.withgoogle.com/archive/2017/projects/6536382147198976).

![screenshot](http://i.imgur.com/r9b5l7K.jpg)

## Documentation
This project is aimed at easing up the process of rebaring in [FreeCAD](https://www.freecadweb.org). In this project, list of rebars will be provided to user under Rebar tools in the form of dropdown. This project covers six different rebar shapes as given below:

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

## Video Tutorial
[![IMAGE ALT TEXT HERE](http://i.imgur.com/ZQGCQoe.png)](https://www.youtube.com/watch?v=BYQQjEKmx5E&t=1435s)


## Installation

### Pre-requisites
- FreeCAD (version >= 0.17): [Installation guide](https://www.freecadweb.org/wiki/Installing)
 
### Steps to install Rebar Addon in FreeCAD
1. Open the FreeCAD Addon Manager (```Tool -> Addon manager```).
2. When an addon manager will open, select ```Reinforcement``` from a list of workbenches shown by an addon manager.
3. After selecting, click on ```Install/Update``` button.
4. Restart FreeCAD.
5. Now you will see different rebars in a drop-down list of rebar tools (```Arch -> Rebar tools -> Different rebars```).

## How it works
Each rebar tool has two files, one is ```Python``` file and second is there respective name ```UI``` file like ```StraightRebar.py``` and ```StraightRebar.ui``` file). Let's take a straight rebar tool. In ```StraightRebar.py``` file, there are two functions. One is ```makeStraightRebar()``` function. This function creates straight rebar and adds new properties to the default ```Rebar``` object. Second function is ```editStraightRebar```. This function is used when we want to change a new properties(which is created by ```makeStraightRebar``` function) of the rebar object and it will take ```Rebar``` object as input which is created by ```makeStraightRebar``` function. In ```StraightRebar.py```, ```_StraightRebarTaskPanel``` class is present. This class loads UI(present in ```StriaghtRebar.ui``` file) in the task panel of FreeCAD. First time when a user clicks on ```Apply``` or ```Ok``` button, then ```makeStraightRebar``` function is executed and after that when user want to change the properties of Straight rebar then ```editStraightRebar``` function is excuted. 

## Extras
- [FreeCAD forum thread](https://forum.freecadweb.org/viewtopic.php?f=8&t=22760)
- [GSoC proposal](https://brlcad.org/wiki/User:Amritpal_singh/gsoc_proposal)
- [Development logs](brlcad.org/wiki/User:Amritpal_singh/GSoC17/logs)
