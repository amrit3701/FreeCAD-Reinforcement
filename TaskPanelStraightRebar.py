from PySide import QtCore, QtGui

class _StraightRebarTaskPanel:
    def __init__(self):
        self.form = FreeCADGui.PySideUic.loadUi("<path_of_StraightRebar.ui_file>")
        self.form.amount_radio.clicked.connect(self.amount_radio_clicked)
        self.form.spacing_radio.clicked.connect(self.spacing_radio_clicked)
        QtCore.QObject.connect(self.form.submit, QtCore.SIGNAL("clicked()"), self.accept)

    def getStandardButtons(self):
        return int(QtGui.QDialogButtonBox.Close)

    def accept(self):
        FreeCAD.Console.PrintMessage("Terminate!\n")

    def amount_radio_clicked(self):
        self.form.spacing.setEnabled(False)
        self.form.amount.setEnabled(True)

    def spacing_radio_clicked(self):
        self.form.amount.setEnabled(False)
        self.form.spacing.setEnabled(True)


if FreeCAD.GuiUp:
    FreeCADGui.Control.showDialog(_StraightRebarTaskPanel())
