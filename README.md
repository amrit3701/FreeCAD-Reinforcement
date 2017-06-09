# FreeCAD-Reinforcement

### Installation

1. Run the below command to download the repository.
<pre>$ git clone https://github.com/amrit3701/FreeCAD-Reinforcement.git</pre>
2. Create the structural element. Copy and paste the below code to create structure element.
<pre>
import Arch 
s = Arch.makeStructure(length=1000.0,width=800.0,height=200.0) 
s.Placement.Base = FreeCAD.Vector(0.0,0.0,0.0) FreeCAD.ActiveDocument.recompute()
</pre>
3. Select any face of the structural element.
4. Go to Macro menu and select Macros.
5. Then change the location of macros to the FreeCAD-Reinforcement.
6. Select the StraightRebar.py and execute. 
