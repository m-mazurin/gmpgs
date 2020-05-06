#!/usr/bin/env python3

import sys
import os
import math

from PyQt5 import QtWidgets

import gmpgs_gui

def isOutputCif(cifPath):
    """Check file for conatining magic string"""
    with open(cifPath,"r") as f:
        for line in f:
            if '# On the following loop you will have:' in line:
                return True
        return False

def processLst(lstPath):
    """Read lst-file and return list of ticks"""
    isReflectionList = False
    peaks = []
    local_peaks = []
    with open(lstPath,"r") as f:
        for line in f:
            if "Reflection list" in line:
                isReflectionList = True
                f.readline()
                continue
            if isReflectionList:
                if line == "\n":
                    peaks.append(local_peaks.copy())
                    local_peaks.clear()
                    isReflectionList = False
                else:
                    line_data = line.split()
                    t = 2*math.asin(1.5405929/2/float(line_data[5]))/math.pi*180
                    local_peaks.append(t)
        return peaks

def processCif(cifPath):
    """Return list of points angle-intensity"""
    points = []
    with open(cifPath,"r") as f:
        isList = False
        line = f.readline()
        while line:
            if "loop_" in line:
                line = f.readline()
                while line[0] == '_':
                    line = f.readline()
                isList = True
            if isList:
                point = line.split()
                if len(point) > 2:
                    points.append(point)
                else:
                    isList = False
            line = f.readline()
        return points

def writeOutFiles(peaks, points, lstDirPath, prefix):
    # Define maximum values of difference and intesity values
    maxdif = float(points[0][1])-float(points[0][2])
    maxval = float(points[0][1])
    for p in points:
        diff = float(p[1])-float(p[2])
        if diff > maxdif:
            maxdif = diff
        if float(p[1]) > maxval:
            maxval = float(p[1])
    #Scale ticks step proportional to maximal instensity and calculate shift
    tick_step = maxval / 40
    diff_shift = maxdif + tick_step*(len(peaks)+1)
    
    with open(os.path.join(lstDirPath, prefix + "_points.dat"),"w") as f:
        f.write("2T\tYobs\tYcalc\tYobs-Ycalc\n")
        for p in points:
            f.write(str(p[0])+"\t"+str(p[1])+"\t"+str(p[2])+"\t"+str(float(p[1])-float(p[2])-diff_shift)+"\n")

    with open(os.path.join(lstDirPath, prefix + "_peaks.dat"),"w") as f:
        f.write("2T\tBragg's positions\n")
        for i in range(len(peaks)):
            for j in range(len(peaks[i])):
                if peaks[i][j] < float(points[len(points)-1][0]):
                    f.write(str(peaks[i][j])+"\t"+str(-1*tick_step*(i+1))+"\n")

class gmpgs_guiApp(QtWidgets.QMainWindow, gmpgs_gui.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        # Connect to buttons
        self.addFolderButton.clicked.connect(self.addFolder)
        self.delFolderButton.clicked.connect(self.remFolder)
        self.procButton.clicked.connect(self.startProcessing)
        self.actionAbout.triggered.connect(self.showAbout)
        self.actionHow_to.triggered.connect(self.showHowto)

    def showAbout(self):
        QtWidgets.QMessageBox.information(self,"About GMPGS","GMPGS\nGUI for MAUD Plot Generating Script\nMaxim Mazurin\nmaksim.mazurin@urfu.ru\n\nIcons by : https://www.flaticon.com/authors/pixel-perfect",QtWidgets.QMessageBox.Ok)

    def showHowto(self):
        QtWidgets.QMessageBox.information(self,"How to use it?","lst-file is normally created near the .par file. To generate appropriate plot .cif-file:\n1.Open your analysis in MAUD and iterate refinement procedure\n2.Go to \"Graphic\"->\"Plot selected dataset\"->\"Tools\"->\"Export experimental\\computed data\"\n3.Save plot to .cif file",QtWidgets.QMessageBox.Ok)

    def addFolder(self):
        dir = QtWidgets.QFileDialog.getExistingDirectory(self,"Add folder to list...")
        if dir:
            self.listWidget.addItem(dir)

    def remFolder(self):
        self.listWidget.takeItem(self.listWidget.currentRow())

    def startProcessing(self):
        self.textEdit.clear()
        for i in range(self.listWidget.count()):
            #Process folders
            path = self.listWidget.item(i).text()
            par_lst_path = ""
            cif_path = ""
            prefix = ""
            self.textEdit.append("===========================\nFolder #" + str(i+1) + " ::\n" + path)
            #Search par.lst and cif files
            for dir_item in os.scandir(path):
                if dir_item.is_file() and ".par.lst" in dir_item.name:
                    par_lst_path = dir_item.path
                    prefix = dir_item.name[:dir_item.name.find(".")]
                    self.textEdit.append(dir_item.name + " found. ")
                elif dir_item.is_file() and ".cif" in dir_item.name:
                    if isOutputCif(dir_item.path):
                        cif_path = dir_item.path
                        self.textEdit.append(dir_item.name + " found.")
            if par_lst_path == "" or cif_path == "":
                self.textEdit.append("One or more files not found in this folder... Skip folder.")
                continue
            #Gettings phases count and ticks in lst file
            self.textEdit.append(".par.lst processing...")
            peaks = processLst(par_lst_path)
            self.textEdit.append(str(len(peaks)) + " phases")
            #Process cif file
            self.textEdit.append(".cif processing...")
            points = processCif(cif_path)
            self.textEdit.append(str(len(points)) + " points read")

            writeOutFiles(peaks,points,path,prefix)

            #Generate gnuplot files (on russian by defalut)
            template_filename = "ru_gtemplate"
            plot_filename = os.path.join(path, prefix + "_plot.plt")
            with open(template_filename,"r",encoding="koi8-r") as tpl_f, open(plot_filename,"w",encoding="koi8-r") as plot_f:
                for line in tpl_f:
                    tmp = line.replace("NAMESTRING",prefix)
                    tmp = tmp.replace("FF1STRING",prefix+"_points.dat")
                    tmp = tmp.replace("FF2STRING",prefix+"_peaks.dat")
                    tmp.encode("koi8-r")
                    plot_f.write(tmp)

            self.textEdit.append("OK!")

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = gmpgs_guiApp()
    window.show()
    app.exec_()

if __name__ == "__main__":
    main()
