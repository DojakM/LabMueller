import glob
import re

import openpyxl as excel
import plotly.graph_objects as go

urlCrosses = glob.glob("/Volumes/MN001122/Material Listen/Cross*")[0]
class Crossing_base:
    def __init__(self, code):
        self.code = code
        self.uniques = []
        wb = excel.load_workbook(urlCrosses)
        self.pokWorksheet = wb["POK crosses"]
        self.sinkSourceMatrix = [[], [], []]
        self.worksheetDictionary = {}
        self.pokCrosses = [[], []]
        #self.colorListNodes = []
        #self.colorListEdges = []


    def start(self):
        self.update()
        self.sort()
        # self.colorOrder()
        self.createNetwork()

    def update(self):
        for i in range(1, 1000, 1):
            source = False
            sinke = False
            crossMale = "B" + str(i)
            crossFemale = "C" + str(i)
            crossNumberM = "D" + str(i)
            crossNumberF = "E" + str(i)
            if self.pokWorksheet[crossMale].value is not None and self.pokWorksheet[crossFemale].value is not None:
                if re.match(self.code,self.pokWorksheet[crossMale].value):
                    self.pokCrosses[0].append(self.pokWorksheet[crossMale].value)
                    self.pokCrosses[1].append(self.pokWorksheet[crossFemale].value)
                    if self.pokWorksheet[crossNumberM].value == None:
                        crossM = "NA"
                    else:
                        crossM = str(self.pokWorksheet[crossNumberM].value)
                    if self.pokWorksheet[crossNumberF].value == None:
                        crossF = "NA"
                    else:
                        crossF = str(self.pokWorksheet[crossNumberF].value)

                    self.sinkSourceMatrix[2].append(crossM + " x " + crossF)

    def sort(self):
        for elem in self.pokCrosses:
            self.uniques.extend(elem)
        uniques = list(set(self.uniques))
        for i in self.pokCrosses[0]:
            self.sinkSourceMatrix[0].append(uniques.index(i))
        for i in self.pokCrosses[1]:
            self.sinkSourceMatrix[1].append(uniques.index(i))

    def colorOrder(self):
        for i in self.uniques:
            if re.match(".*POK1.*", i):
                self.colorListNodes.append("coral")
            elif re.match(".*pok1.*", i):
                self.colorListNodes.append("red")
            elif re.match(".*POK2.*", i):
                self.colorListNodes.append("blue")
            elif re.match(".*pok2.*", i):
                self.colorListNodes.append("cyan")
            else:
                self.colorListNodes.append("grey")
        for i in self.sinkSourceMatrix[0]:
            self.colorListEdges.append(self.colorListNodes[i])

    def createNetwork(self):
        fig = go.Figure(data=go.Sankey(
            node=dict(
                pad=5,
                thickness=5,
                line=dict(color="black", width=1),
                label = self.uniques,
                #color = self.colorListNodes
            ),
            link=dict(
                source=self.sinkSourceMatrix[0],
                target=self.sinkSourceMatrix[1],
                value=[3] * len(self.sinkSourceMatrix[0]),
                label= self.sinkSourceMatrix[2],
                #color = self.colorListEdges
            )
        ))
        fig.show()

if __name__ == '__main__':
    print("I am alive")
    Crossing_base(".*POK1.*").start()
    print("I am dead")

def Start(Name):
    Crossing_base(".*" + Name + ".*").start()