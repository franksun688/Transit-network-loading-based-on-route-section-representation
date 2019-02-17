#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 13 14:08:32 2019

@author: Ran Sun
"""

"""
Readme

testnetwork: szeto 2018, SF modified

#all of the csv are treated as pd.dataframe
#node.csv
#nodeid, lat, lon

#link.csv
#link
#linkid,from, to, travel time, route , frequency, capacity

#demand.csv
#from, to, demand

#modified linkp.csv
#linkp
#linkpid, from, to, travel time, route, headway, capacity

#input: node, link
#routes.csv
#route,headway,stop_tol,stop_node

#units: 
frequency: veh/hour
headway: minutes
waitingtime: minutes
traveltime: minutes
capacity: passenger/h

#output: gamma, delta, M, num_link, num_od, num_path


"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os 
import networkx as nx
#os.chdir("C:\Dropbox\COMMON_MAC_DELL\TransitDemandEstimation\SUE_estimation_01312019\SUEDemandEstimationCodeDeceaNetwork")
#os.chdir("/Users/frank/Documents/Dropbox/COMMON_MAC_DELL/TransitDemandEstimation/SUE_estimation_01312019/SUEDemandEstimationCodeDeceaNetwork")


route = pd.read_csv('routes_4.csv') #note that nodeid have already been recorded
linkattribute = pd.read_csv("linkattribute_4.csv")
node = pd.read_csv("node_4.csv")

node_tol = len(node)
route_tol = len(route)

#number of link is given
link_tol = 50


#set up a new dataframe for linka
#original transit links
link = pd.DataFrame(np.zeros((link_tol,9)),columns=['linkid','fromnode', 'tonode', 'routeid','traveltime','waitingtime','headway','frequency','capacity'])

#record the node id loaded
linkno = 0

#start to load data to linka mainly from route.csv
for i in np.arange(route_tol):
    routeid = i+1
    headway = route.iat[i,1] #mins
    stop_tol = route.iat[i,2]
    waitingtime = 0
    frequency = 1*60/headway #bus/hour
    #trace stops from route data
    for j in np.arange(stop_tol-1):
        for k in np.arange(j+1,stop_tol):
            #record from mode and to node
            fromnode = route.iat[i,j+3]
            tonode = route.iat[i,k+3]
            
            #here need further info
#            traveltime = linkattribute.iat[linkno,1]
#            capacity = linkattribute.iat[linkno,2]
            traveltime = linkattribute.loc[j:k-1,['traveltime']]['traveltime'].sum()
            capacity = 100

            #add one row into the linke datafrmane
            link.loc[linkno] = [linkno+1,fromnode,tonode,routeid,traveltime,waitingtime,headway,frequency,capacity]
            linkno = linkno+1
       
#have original link and all the auxillary recorded on csv
link.to_csv("link_4.csv") #there are 160 links include parallel links
link = link.astype('object')

#then we combine parallel links, generates a new dataframe named linkp
linkp = link
#linkp = linkp.astype('object')
#obtain the unique values of link: from, to
linkp = linkp.drop_duplicates( subset = ['fromnode','tonode']) #this has 124 links

linkpno = len(linkp)
for i in np.arange(linkpno):
    #select from, to node
    fromnodep = linkp.iat[i,1]
    tonodep = linkp.iat[i,2]
    
    #select duplicate from, to nodes from link set
    linkparallel = link.loc[(link['fromnode'] == fromnodep )&\
                             (link['tonode'] == tonodep )]
    
    #if there are multiple lines, then we combine the information
    if (len(linkparallel)>1):
        #construct a list of route id
        routeparallel = list(linkparallel['routeid'])
        frequencylist = list(linkparallel['frequency'])
        frequencysum = sum(linkparallel['frequency'])
        frequencyratio = list(linkparallel['frequency']/frequencysum)
        #weighted mean of travel time
        traveltimemean = sum(frequencyratio*linkparallel['traveltime'])
        capacity = sum(linkparallel['capacity'])
        
#        
#        linkp.loc[i,'routeid'] = routeparallel
#        linkp.loc[i,'traveltime'] = traveltimemean
#        linkp.loc[i,'frequency'] = frequencylist
#        linkp.loc[i,'capacity'] = capacity
        linkp.iat[i,3] = routeparallel
        linkp.iat[i,4] = traveltimemean
        linkp.iat[i,7] = frequencylist
        linkp.iat[i,8] = capacity

    linkp.iat[i,6] = 'NA'


linkp.to_csv("linkp_4.csv")



#then we can perform network transformation, get dataframe linka
#gamma = OD*Path
#delta = link*path
