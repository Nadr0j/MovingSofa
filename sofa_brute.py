import numpy as np
from math import cos, sin, pi, atan2,tan,exp
from sympy import cot, csc,sqrt
import sys,select,os
from shapely.ops import linemerge
from shapely.ops import polygonize_full
from shapely.ops import Polygon
from shapely.affinity import rotate,translate #use affinity for affine transforms
from shapely.geometry import box,Point #use to create hallways
from matplotlib import pyplot as plt #to plot polygons
from descartes import PolygonPatch #to help matplotlib plot polygons
from shapely.geometry.polygon import LinearRing
from shapely.geometry import LineString
from numpy.random import randint
import matplotlib.animation as animation
import matplotlib
matplotlib.use("GTK3Agg")
import random
import copy
import time
from scipy import interpolate

def generate_hallway(t,a):
    """Generates a hallway of angle a at x(t) where x is the rotation path"""

    intersection_pt = -cos(a*pi/180)/sin(a*pi/180) * 2*sin(a*pi/360)**2+sin(a*pi/180)

    #points for l_vert
    v1 = xt(t) + np.array(list(rotate(Point(0,0),t,origin=(0,0)).coords)[0])
    v2 = xt(t) + np.array(list(rotate(Point(1,intersection_pt),t,origin=(0,0)).coords)[0])
    v3 = xt(t) + np.array(list(rotate(Point(1,-10),t,origin=(0,0)).coords)[0])
    v4 = xt(t) + np.array(list(rotate(Point(0,-10),t,origin=(0,0)).coords)[0])

    #points for l_horiz
    h1 = xt(t) + np.array(list(rotate(Point(0,0),t,origin=(0,0)).coords)[0])
    h2 = xt(t) + np.array(list(rotate(Point(1,intersection_pt),t,origin=(0,0)).coords)[0])
    h3 = xt(t) + np.array(list(rotate(Point(cos(a*pi/180)-10*sin(a*pi/180),sin(a*pi/180)+10*cos(a*pi/180)),t,origin=(0,0)).coords)[0])
    h4 = xt(t) + np.array(list(rotate(Point(-10*sin(a*pi/180),10*cos(a*pi/180)),t,origin=(0,0)).coords)[0])

    hallway = Polygon([h1,h2,h3,h4]).union(Polygon([v1,v2,v3,v4]))

    return hallway

def hallway_intersector(N,a,at):
    """Takes N hallways of angle a and intersects them
    Returns a shapely polygon
    Variable at is a remnant of an old feature which might come back.
    For now, at=a and is meaningless"""
    hallways = []
    hallways.append(Polygon([(-10,0),(-10,1),(10,1),(10,0)]))
    hallways[0] = rotate(hallways[0], a-90,origin=(0,0))
    #<- angle subdivisions
    for i in range(0, N):
        t =  at * i/N
        hallways.append(generate_hallway(t,a))

    final_shape = hallways[0]
    for i in hallways:
        final_shape = final_shape.intersection(i)

    house = box(-10,-20,10,20)

    final_shape = final_shape.intersection(house)

    return final_shape

def hallway_list(N,a,at):
    """Takes int N and returns array of rotated hallways of angle a
    at is a remnant of an old feature which might come back
    Currently at=a and is meaningless"""
    hallways = []
    hallways.append(Polygon([(-10,0),(-10,1),(10,1),(10,0)]))
    hallways[0] = rotate(hallways[0], a-90,origin=(0,0))
    #<- angle subdivisions
    for i in range(0, N+1):
        t = at * i/N
        hallways.append(generate_hallway(t,a))

    #min_x = xt(90) + np.array(list(rotate(Point(1,1),90,origin=(0,0)).coords)[0])
    house = box(-10,-20,10,20)
    hallways.append(house)

    return hallways

def xt(t):
    """Define rotation path"""
    
    a = .605514 #2/pi #hammersley val
    b = .667834 #2/pi #hammersley val
    k1 = 2
    k2 = 2
    x = np.array([a*cos(k1*t*pi/180)-a,b*sin(k2*t*pi/180)])

    return x

def set_to_poly(s):
    '''takes set of hallway polygons (type: geom). Intersects them and returns final polygon'''
    final_shape = s[0]

    for hallway in s:
        try:
            final_shape = final_shape.intersection(hallway)
        except:
            print("errderr")
            return 'er' #return error string

    return final_shape

def get_carver(hallway_set):
    '''Takes hallway_set and returns polygon object used to smooth inside of sofa'''

    center_points_x = []
    center_points_y = []

    for k in range(1,len(hallway_set)-2): #make -2 to -1 if errors occur. modified june 14 2020
        hway_len = len(hallway_set[k].exterior.xy[0])
        center_points_x.append(hallway_set[k].exterior.xy[0][0])
        center_points_y.append(hallway_set[k].exterior.xy[1][0])

    if False: #polynomial interp
        tpts = [n/N * 90 for n in range(0,N)]

        xtck = interpolate.splrep(tpts,center_points_x,s=0)
        ytck = interpolate.splrep(tpts,center_points_y,s=0)

        tpts = np.linspace(1/N*90, (N-1)/N*90, 100)

        xcp = list(interpolate.splev(tpts,xtck,der=0))
        ycp = list(interpolate.splev(tpts,ytck,der=0))

        xcp.append(center_points_x[round(len(center_points_x)/2)-1])
        ycp.append(-.4)

        carver = Polygon([(xcp[i],ycp[i]) for i in range(len(xcp))])

    if True: #piecewise lin carver
        center_points_x.append(center_points_x[round(len(center_points_x)/2)-1])
        center_points_y.append(-.4)
        carver = Polygon([(center_points_x[i],center_points_y[i]) for i in range(len(center_points_x))])


    #center_points_x.append(center_points_x[round(len(center_points_x)/2)-1])
    #center_points_y.append(-.4)
    #carver = Polygon([(center_points_x[i],center_points_y[i]) for i in range(len(center_points_x))])

    return carver

def balance(a,N,iterations,hallway,hallway_set):
    for i in range(iterations):
        tol = 1/1000 #larger number == larger perturbations
        repeat_area_count = 0
        for k in range(len(hallway_set)):
                hallway = set_to_poly(hallway_set)
                theta_p = k*a/N*(pi/180)
                theta_s = (theta_p + a)*(pi/180)
                sofa_area = hallway.area

                slp = np.array([cos(theta_s),sin(theta_s)])
                sln = np.array([-cos(theta_s),-sin(theta_s)])
                plp = np.array([-sin(theta_p),cos(theta_p)])
                pln = np.array([sin(theta_p),-cos(theta_p)])

                track_list = [slp,sln,plp,pln]

                flag = 0 #if turned to four area did not increase after
                         #<=4^N movements.
                         #decrease tolerence and try again

                for track in track_list:
                    hallway_set_temp = hallway_set[:] #shallow copy 
                    hallway_set_temp[k] = translate(hallway_set_temp[k],tol * track[0],tol * track[1])
                    sofa_temp = set_to_poly(hallway_set_temp)
                    if str(sofa_temp.geom_type) == "Polygon" or "polygon":
                        sofa_temp_area = sofa_temp.area
                        if sofa_temp_area > sofa_area:
                            hallway_set = hallway_set_temp
                        if sofa_temp_area < sofa_area:
                            flag += 1

                if flag == 4:
                    repeat_area_count +=1
                    tol *= 9/10


        if sys.stdin in select.select([sys.stdin],[],[],0)[0]:
            line = input()
            return hallway, hallway_set,i

        if repeat_area_count == len(hallway_set)-1:
            #if program was unable to increase area
            #hallway is at max so return it
            return hallway,hallway_set,i

        print(i,":",hallway.area)

    return hallway, hallway_set, i


def plot_saver(hallway,hallway_set,theta,N,i,smooth=True):
    plt.cla() #clear axis in the case they had already been opened
    hallway = rotate(hallway, 90-a, origin=(0,0))
    for k in range(len(hallway_set)):
        hallway_set[k] = rotate(hallway_set[k],90-a,origin=(0,0))

    carver = get_carver(hallway_set)

    if smooth==True:
        try:
            hallway = hallway.difference(carver)
        except:
            print("failed to carve")

    mp = round(len(hallway_set)/2)

    #hallway = rotate(hallway, 90-a, origin=(0,0))
    #hallway_set[0] = rotate(hallway_set[0], 90-a, origin=(0,0))

    minx, miny, maxx, maxy = hallway.bounds


    plt.style.use('ggplot')
    fig = plt.figure(dpi=200,figsize=(5,3))
    ax=fig.add_subplot(111)
    ax.grid(True)
    ax.set_xlim([minx-.5,maxx+.5])
    ax.set_ylim([miny-.3,maxy+.5])
    ax.set_aspect(1)

    #uncomment for writeframe display
    #for i in range(1,len(hallway_set),):
    #    #hallway_set[i] = rotate(hallway_set[i], 90-a, origin=(0,0))
    #    x,y = hallway_set[i].exterior.xy
    #    plt.plot(x,y,linewidth=.4)

    x,y = hallway_set[1].exterior.xy
    plt.plot(x,y,linewidth=.2,color='grey')

    #plot one hallway

    ax.add_patch(PolygonPatch(hallway))
    plt.title(str(hallway.area)+ "N:" + str(N))
    #fig.savefig("a:"+str(theta)+"_N:"+str(N)+"_Smth:"+str(smooth)+"_i:"+str(i)+".png",dpi=900)
    plt.show()
    plt.close()



def plot_mover(hallway,hallway_set,theta,N,i,hway_num,smooth=True):
    plt.cla() #clear axis in the case they had already been opened
    #hallway = rotate(hallway, 90-a, origin=(0,0))
    #for k in range(len(hallway_set)):
    #    hallway_set[k] = rotate(hallway_set[k],90-a,origin=(0,0))


    if smooth==True:
        try:
            carver = get_carver(hallway_set)
            print("smoothing rotation path")
            hallway = hallway.difference(carver)
        except:
            print("failed to carve")

    mp = round(len(hallway_set)/2)

    #hallway = rotate(hallway, 90-a, origin=(0,0))
    #hallway_set[0] = rotate(hallway_set[0], 90-a, origin=(0,0))

    minx, miny, maxx, maxy = hallway.bounds


    plt.style.use('ggplot')
    fig = plt.figure(dpi=200,figsize=(5,3))
    ax=fig.add_subplot(111)
    ax.grid(False)
    ax.set_xlim([minx-.5,maxx+.5])
    ax.set_ylim([miny-.3,maxy+.5])
    ax.set_aspect(1)

    #uncomment for wireframe display
    #for i in range(1,len(hallway_set)):
    #    hallway_set[i] = rotate(hallway_set[i], 90-a, origin=(0,0))
    #    x,y = hallway_set[i].exterior.xy
    #    plt.plot(x,y,linewidth=.4)

    x,y = hallway_set[hway_num].exterior.xy
    plt.plot(x,y,linewidth=.2,color='grey')

    #plot one hallway

    ax.add_patch(PolygonPatch(hallway,ec="none"))
    plt.title(str(hallway.area)+ "N:" + str(N))
    fig.savefig("a:"+str(theta)+"_N:"+str(N)+"_Smth:"+str(smooth)+"_j:"+str(hway_num)+".png",dpi=900)
    #plt.show()
    plt.close()

a = 90
N = 12
iterations = 50000


#init vars
ang_val = [float(x) for x in input("Enter angle val: ").split()]
N = int(input("Enter num of anchor points (5+): "))
smth = int(input("Enter 1 for smoothing 0 for none: "))
mover = int(input("1 to save moving plot set (local folder) 0 otherwise: "))


for a in ang_val:
    hallway = hallway_intersector(N,a,a)
    hallway_set = hallway_list(N,a,a)
    hallway, hallway_set, i = balance(a,N,iterations,hallway,hallway_set)
    if not mover:
        plot_saver(hallway,hallway_set,a,N,i,smooth=smth)
    if mover:
        for j in range(1,N+1):
            plot_mover(hallway,hallway_set,a,N,i,j,smooth=smth)







