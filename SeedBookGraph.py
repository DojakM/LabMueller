### MISSION STATEMENT
# This file turns the digitized seedlist into a html showing the child-parent relationship in the form of a
# directed acyclic graph (DAG). As an input it needs the seedlist excel sheet.

### IMPORTS
import pandas as pd
from pyvis.network import Network
import networkx as nx
import streamlit as st
import re
from stvis import pv_static

### METHOD CALLS
# Creation of a panda dataframe, which encompasses all elements of the seed excel table
# @params:
# URL is the path to the excel file
#   It has to be a copy of the seed stock NZ excel sheet to work
# Outout: A 1:1 transfer of the excel table in a panda dataframe
def loadingFiles(URL):
    xpanda = pd.read_excel(URL, sheet_name="digital seed book")
    xpanda = xpanda.dropna(subset=["GENOTYPE"])  # all entries w/o genotype are dropped
    return xpanda


# Calculating the amount of Roots (Seedlines with no parent)
# @params:
# inputArr is an array with all unique Parents
# rootArr is an empty list in which all roots are sorted
# nonrootArr is an empty list in which all non roots are sorted
# dataframe is a panda graphDF frame with all entries
# Output: a filled rootArr and nonrootArr
def rooting(inputArr, rootArr, nonrootArr, dataframe):
    for i in inputArr:
        if len(dataframe["child"].where(lambda x: x == i).dropna()) == 0:
            rootArr.append(i)
        else:
            nonrootArr.append(i)
    return rootArr, nonrootArr


# Creation of a new graphDF frame which will be the basis of the graph and a written version of the graph
# @param:
# excelDF is the basic dataframe stemming from loadingFiles function call
# Output: a panda df called graphDF with parent as label, the cleanedParent and child and the genotype
def sortParents(excelDF):
    # creating empty dataframe
    graphDF = pd.DataFrame()

    # Generate two entries in F1 for each child-parent combination
    excelDF["# parent"] = excelDF["# parent"].apply(lambda x: x.split("x"))
    excelDF = excelDF.explode("# parent")

    # filling the graphDF with entries
    graphDF["genotype"] = excelDF["GENOTYPE"]
    graphDF["generation"] = excelDF["GENERATION"]
    graphDF["child"] = excelDF["#NEW"]
    graphDF["label"] = excelDF["# parent"]  # label to transfer it directly as a label to the html

    # deleting all entries with no correct child entry
    graphDF = graphDF.dropna(subset=["child"])

    # creating a new field with only the seed number
    graphDF["cleanParent"] = graphDF["label"].apply(lambda x: x.split("-")[0])

    # output is the newly described dataframe
    return graphDF


# Writing of a seedlineTree which shows a hierarchical structure of seeds from Bottom Up
# @param:
# graphDF is a dataFrame with parent-child relations, derived from sortParents function call
# Output: In terminal written tree with hierarchies shown through tabs
def writeSeedTree(graphDF):
    # Reducing calculation time by only looking at non-redundant parents
    uniqueParents = graphDF["cleanParent"].unique()

    # filled arrays of roots (gen = 1) and non_roots (gen > 1)
    roots = []
    non_roots = []
    roots, non_roots = rooting(uniqueParents, roots, non_roots, graphDF)

    # Sorting the children to the roots
    rootdict = []
    for val, root in enumerate(roots):
        rootdict.append([])
        rootdict[val].append(root)
        rootdict[val].append(graphDF[graphDF["cleanParent"] == root]["child"])

    # Ouput: printing the roots (gen=0) the children of the root (gen=1) and the grandchildren (gen = 2) all others are
    # ignored
    for i in rootdict:
        print("root:\t" + i[0] + "\n")
        for j in i[1]:
            if j in non_roots:
                print(j)
                child_sec = graphDF[graphDF["cleanParent"] == j]["child"]
                for k in child_sec:
                    print("\t" + k)
            else:
                print(j)


# Adds Shape and Color to the node depending on their generation indicator
# @param:
# nodes from the Network derived from the df
# df is the graphDF used for graph creation
# Output: Two arrays of colors and shapes corresponding to a node
def addFormColor(nodes, df):
    # Ouput arrays
    forms = []
    colors = []

    # Iteration through each node
    for node in nodes:
        # finding all generation values of a node. If a node has no entry (parent w/o entry)...
        gen = df[df["child"] == node.get("id")]["generation"].values
        gen = gen.any()
        # ... he will be filtered out here with everyone who has no generation entry
        if gen == "nan" or gen == ["nan"] or gen == []:
            forms.append("ellipse")
            colors.append("#0077C0")
        else:
            # selection of the shapes (pyvis shapes) and colors (hexformat)
            # Here can be added multiple different sets.
            # Transformant
            if gen == "T0":
                forms.append("triangle")
                colors.append("#F51720")
            elif gen == "T1":
                forms.append("triangle")
                colors.append("#FA26A0")
            elif gen == "T2":
                forms.append("triangle")
                colors.append("#FFB8BF")

            # Crossing
            elif gen == "F1":
                forms.append("diamond")
                colors.append("#BD2A33")
            elif gen == "F2":
                forms.append("diamond")
                colors.append("#FE0000")

            # Unexpected entry (e.g. M0)
            else:
                forms.append("ellipse")
                colors.append("#0077C0")

    # output are the filled outputArrays
    return forms, colors


# generates the DAG in a html
# @params:
# graphDF is a DataFrame with a From (child) to (cleanParent) relationship derived from sortParents() function call
# All is a boolean check, whether the results are supposed to be filtered
# name is the name under which the file will be saved
# Output: html including all nodes in a DAG
def generateGraph(graphDF, filter = False, filterbyNR = False, filterBasis = "", name="test"):

    # dimensions of network
    nt = Network('800px', '1200px')

    # Filtering the data based on the filter args
    if filter and filterbyNR:
        graphDF = filterGraph(filterBasis, graphDF)
    elif filter and not filterbyNR:
        graphDF = graphDF[graphDF["genotype"] == filterBasis]


    # Generation of nx Network from pandaDF, edgeAttr allows labeling, Digraph for directional viewing
    seedGraph = nx.from_pandas_edgelist(graphDF, source="cleanParent", target="child", edge_attr=True,
                                        create_using=nx.DiGraph())

    # Reformatting it into a pyvis.Network
    Network.from_nx(nt, seedGraph)

    # Choosing which options are available during html
    Network.show_buttons(nt, filter_=["layout", "edges"])

    # adding shape and color of nodes
    forms, colors = addFormColor(nt.nodes, graphDF)
    for val, node in enumerate(nt.nodes):
        node["shape"] = forms[val]
        node["color"] = colors[val]

        # making genotype the hover information (called title in pyvis)
        id = node.get("id")
        title = graphDF[graphDF["child"] == id]["genotype"].values
        if len(title) > 0:
            node["title"] = title[0]

    # showing the parent as label and removing all bulk parents
    for edge in nt.edges:
        if re.match(".*-+[0-9]+-+.*", edge["label"]):
            temp_edge_label = edge["label"].split("-")
            edge["label"] = temp_edge_label[0]

    # creation of html file
    # nt.show("{}.html".format(name))
    return nt

# Prints and Returns all direct ancestors and offspring.
# IMPORTANT: ALL ENTRIES HAVE TO BE RELATED DIRECTLY TO THE SEEDNUMBER!
# @params:
# SeedNumber is the search term
# graphDF is the table of child-cleanParent relationships and their additional data
def printSeedHistory(SeedNumber, graphDF):
    #generation of the nx network
    network = nx.from_pandas_edgelist(graphDF, source="cleanParent", target="child", edge_attr=True,
                                        create_using=nx.DiGraph())

    # Finding all predecessors
    PredQ = []
    PredList = []
    for predecessor in network.predecessors(SeedNumber):
        PredQ.append(predecessor)

    # Adding all predecessors until hitting a root
    while not len(PredQ) == 0:
        if len(list(network.predecessors(PredQ[0])))>0:
            for predecessor in network.predecessors(PredQ[0]):
                PredQ.append(predecessor)
            temp = PredQ.pop(0)
            PredList.append(temp)
        else:
            temp = PredQ.pop(0)
            PredList.append(temp)

    # Finding all successors
    SuccQ = []
    SuccList = []
    for successor in network.successors(SeedNumber):
        SuccQ.append(successor)

    # Looping until all successors are found
    while not len(SuccQ) == 0:
        if len(list(network.successors(SuccQ[0])))>0:
            for successor in network.successors(SuccQ[0]):
                SuccQ.append(successor)
            temp = SuccQ.pop(0)
            SuccList.append(temp)
        else:
            temp = SuccQ.pop(0)
            SuccList.append(temp)

    # printing the lists of predecessors and successors
    print("predeccessors: " + str(PredList))
    print("successors: " + str(SuccList))

    # returning these lists
    return PredList, SuccList


# Basic filter function of the graph
# @param:
# filter is the Seednumber by which is filtered
# graphDF is the panda data frame with a child-parent relationship derived from sortParents() function call
# Output: filtered Dataframe
def filterGraph(filter, graphDF):
    predList, succList = printSeedHistory(filter, graphDF)
    newList = predList + succList + [filter]
    booleanSeries = graphDF.child.isin(newList)
    filteredDF = graphDF[booleanSeries]
    return filteredDF

def generateInterface(graphdf):
    button = st.sidebar.checkbox("Filter on/off")
    filterSelect = st.sidebar.checkbox("Filter by Seednumber")
    option = ""
    if button == True:
        if filterSelect:
            filtering = graphdf["child"]
            filtering = filtering.append(graphdf["cleanParent"])
            option = st.sidebar.selectbox("Filter:", filtering.unique())
        else:
            option = st.sidebar.selectbox("Filter:", graphdf["genotype"].unique())
    graph = generateGraph(graphdf, filter=button, filterbyNR=filterSelect, filterBasis=option, name="test")
    st.title("AG Müller digital seed book")
    pv_static(graph)
    st.dataframe(graphdf)

### MAIN FUNCTION
# this is what happens when the program runs
if __name__ == '__main__':
    excelDF = loadingFiles("test.xlsx") #SeedBook enter here the path
    graphdf = sortParents(excelDF)
    generateInterface(graphdf)
