# FreeCAD-Reinforcement

### Installation

1. Run the below command to download the repository.
<pre>$ git clone https://github.com/amrit3701/FreeCAD-Reinforcement.git</pre>
2.  After download, open the TaskPanelStraightRebar.py file and set the path of the UI file in line number 6.
3. Create the structural element. Copy and paste the below code to create structure element.
<pre>
import Arch 
s = Arch.makeStructure(length=1000.0,width=800.0,height=200.0) 
s.Placement.Base = FreeCAD.Vector(0.0,0.0,0.0) FreeCAD.ActiveDocument.recompute()
</pre>
4. Select any face of the structural element.
5. Copy and paste the code present in the ```TaskPanelStraightRebar.py``` file.
