from PySide import QtCore
from PySide import QtGui
from PySide import QtSvg
import FreeCADGui
import os
class PopUpImage(QtGui.QDialog):
   def __init__(self, img):
	QtGui.QDialog.__init__(self)
	self.image = QtSvg.QSvgWidget(img)
        self.setWindowTitle(QtGui.QApplication.translate("RebarTool", "Detailed description", None))
	self.verticalLayout = QtGui.QVBoxLayout(self)
	self.verticalLayout.addWidget(self.image)

def showPopUpImageDialog(img):
    ui = PopUpImage(img)
    ui.exec_()
