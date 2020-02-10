import numpy as np
from math import cos, sin, pi, atan2,tan
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

def rm(t): #MARK FOR DEL
    """Define a rotation matrix evaluated at angle 0<=t<=pi/2 and returned"""
    A = np.array([[cos(t),-sin(t)],[sin(t),cos(t)]])
    return A

def generate_hallway(t,a):
    """Generate hallway :)"""

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
    """WRITE THIS TOMORROW :)"""
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
    """Takes int N and returns array of rotated hallways"""
    hallways = []
    hallways.append(Polygon([(-10,0),(-10,1),(10,1),(10,0)]))
    hallways[0] = rotate(hallways[0], a-90,origin=(0,0))
    #<- angle subdivisions
    for i in range(1, N):
        t = at * i/N
        hallways.append(generate_hallway(t,a))

    #min_x = xt(90) + np.array(list(rotate(Point(1,1),90,origin=(0,0)).coords)[0])
    house = box(-10,-20,10,20)
    hallways.append(house)

    return hallways

def xt(t):
    """Define rotation path"""
    a = 2/pi
    b = 2/pi
    k1 = 2
    k2 = 2
    x = np.array([a*cos(k1*t*pi/180)-a,b*sin(k2*t*pi/180)])
    return x

def get_poly_points(hallway):
    '''Takes hallway and returns x,y coords of points defining polygon
    Returns [[x1,y1],[x2,y2],...,[xn,yn]]'''
    x_coords = [Point(i).xy[0][0] for i in hallway.exterior.coords]
    y_coords = [Point(i).xy[1][0] for i in hallway.exterior.coords]

    point_pairs = [[x_coords[i],y_coords[i]] for i in range(len(x_coords))]

    return point_pairs

def points_to_lines(points):
    '''Takes list of points of form [[x,y],[x,y],...]. Returns list of lines in form
    [[[x1,y1],[x2,y2]],[[x2,y2],[x3,y3],...,[[xn,yn],[x1,y1]]]'''
    lines = []
    for p in range(len(points)-1):
        lines.append([[points[p][0],points[p][1]],[points[p+1][0],points[p+1][1]]])
    #lines.append([[points[len(points)-1][0],points[len(points)-1][1]],[points[0][0],points[0][1]]])

    return lines

def lines_to_angles(lines,a):
    '''takes lines turns them into angles'''
    angles = []

    for line in lines:
        x1t,y1t = line[0][0],line[0][1]
        x2t,y2t = line[1][0],line[1][1]

        #translate to snap 'rightmost' point to origin
        if x1t > x2t:
            px = x2t-x1t
            py = y2t-y1t
        if x2t > x1t:
            px = x1t-x2t
            py = y1t-y2t

        #rotate -pi/2 deg
        x = py
        y = -px

        if y1t==y2t:
            theta = 0 #angle from pos x axis
        if x1t==x2t:
            theta = -pi/2 #angle from pos x axis
        else:
            theta = 180/pi*atan2(y,x)

        if theta < 0:
            theta = 180 + abs(-180-theta)

        angles.append(theta)

    return angles

def array_to_line(line):
    '''Takes [[a,b],[c,d]] and returns LineString w/ pt1 = (a,b) and pt2 = (c,d)'''
    a = line[0][0]
    b = line[0][1]
    c = line[1][0]
    d = line[1][1]

    return LineString([(a,b),(c,d)])

def distance_test(p1,p2,p0):
    x1,y1 = p1[0],p1[1]
    x2,y2 = p2[0],p2[1]
    x0,y0 = p0[0],p0[1]

    d = abs((y2-y1)*x0-(x2-x1)*y0+x2*y1-y2*x1)/((y2-y1)**2+(x2-x1)**2)**(1/2)

    return d

def balance_identifier(lines,angles,tolerance,a1):
    '''Takes lines and angles which define hallway. Searches for lines w/ same angle of rotation
    relative to y axis which are also one unit apart and returns. Tolerance determines how
    close line lengths need to be to be considered balanced'''

    for a2 in range(len(angles)):
        if a2 != a1: #don't check the same index number angles[1] == angles[1] not usefull
            if abs(angles[a1] - angles[a2]) <= 10**(-10): #lines are parallel
                l1 = array_to_line(lines[a1])
                l2 = array_to_line(lines[a2])
                line_dist = distance_test(lines[a1][0],lines[a1][1],lines[a2][0])
                l1_length = l1.length
                l2_length = l2.length
                if (angles[a1] - 90) <= 10**(-16):
                    if l1.xy[0][1] > l2.xy[0][1]:
                        l2_length = l2_length * 2
                    if l1.xy[0][1] < l2.xy[0][1]:
                        l1_length = l2_length * 2
                #check if lines unit apart and not equal in length
                #print("Distance for lines")
                #print("angles: ",angles[a1],angles[a2])
                #print("l1: ",lines[a1])
                #print("l2: ",lines[a2])
                #print("D(l1,l2): ",line_dist)
                if abs(line_dist-1) <= 10**(-10) and abs(l1_length-l2_length) > 10**(-20):
                    if abs(angles[a1]-90) <= 10**(-10): #if horizontal line case
                        if l1.xy[0][1] > l2.xy[0][1]:
                            return a1,a2 #first val is always topmost line
                        if l1.xy[0][1] < l2.xy[0][1]:
                            return a2,a1 #first val is always topmost line
                    if l1.xy[0][0] < l2.xy[0][0]: #a1 is leftmost line
                        return a1,a2 #first val is leftmost
                    if l1.xy[0][0] > l2.xy[0][0]: #a2 is leftmost line
                        return a2,a1 #first val is leftmost

    return -1,-1

def get_hallway_num(angle,N,a):
    '''Takes angle of parallel lines and finds corresponding hallway index num '''
    i = 0 #index num


    if abs(angle) <= 10**(-16):
        return 'h' #this should be an error... I think
    if  abs(angle-a) <= 10**(-16):
        return 0 #the horizontal lines are a special case always belonging to 0
    if 0 < angle < a:
        i = N/a * angle
    if a < angle <= 2*a:
        i = N/a*(angle-a)

    return int(round(i))

def get_push_direction_old(l1,l2,angle):
    '''Returns signed angle orthogonal to line pair w/ sign indicating direction'''
    if l1 > l2 and angle > 0:
        return angle - 180
    if l1 < l2 and angle > 0:
        return angle + 180
    if l1 > l2 and angle < 0:
        return angle + 180
    if l1 < l2 and angle < 0:
        return angle - 180

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

def push_hallway_old(hallway_set,hallway_num,push_dir,d):
    '''Takes hallway set & hallway num along w/ d=tolerance which determines
    how much to push the hallway by in push dir. Returns hallway set'''
    if push_dir == 270 or push_dir == -90: #special verticle case
        if push_dir == 270:
            push_dir = 90
        for i in range(1,len(hallway_set)-1):
            hallway_set[i] = translate(hallway_set[i],d*cos(push_dir*pi/180),d*sin(push_dir*pi/180))
        return hallway_set
    else:
        hallway_set[hallway_num] = translate(hallway_set[hallway_num],d*cos(push_dir*pi/180),d*sin(push_dir*pi/180))
        return hallway_set

def get_push_sign(l1,l2):
    if l1 > l2:
        return -1
    if l2 > l1:
        return 1

def push_hallway(hallway_set,hallway_num,angle,d,sign,a):
    '''Takes hallway set & hallway num along w/ d=tolerance which determines
    how much to push the hallway by in push dir. Returns hallway set'''
    hallway_set_temp = copy.copy(hallway_set)
    if abs(abs(angle)-a)<=10**(-10) : #special horiz case
        for i in range(1,len(hallway_set)-1):
            hallway_set_temp[i] = translate(hallway_set_temp[i],sign*d*cos(angle*pi/180),sign*d*sin(angle*pi/180))
        return hallway_set_temp
    else:
        hallway_set_temp[hallway_num] = translate(hallway_set_temp[hallway_num],sign*d*cos((hallway_num/N*a+a)*pi/180),sign*d*sin((hallway_num/N*a)*pi/180))
        return hallway_set_temp

def get_features(hallway,a):
    '''returns points,lines,angles which define hallway. To simplify other code'''
    points = get_poly_points(hallway)
    lines = points_to_lines(points)
    angles = lines_to_angles(lines,a)

    return points,lines,angles

def another_iteration(hallway,hallway_set,tolerance,N,k,a):
    '''Takes hallway, halway_set, tolerance and N = #num of hallway
    Finds unbalanced edges and pushes hallway set in orthogonal direction to
    unbalanced edges. Returns updated hallway and hallway_set'''

    #get hallway data to make push
    points,lines,angles = get_features(hallway,a)

    #find balance pair
    a1,a2 = balance_identifier(lines,angles,tolerance,k)
    if a1 == -1 == a2:
        return 'nb','nb' #unable to find line to balance

    #store pair lengths
    l1 = array_to_line(lines[a1])
    l2 = array_to_line(lines[a2])
    l1_length = l1.length
    l2_length = l2.length

    #search for valid hallway num
    hallway_num = get_hallway_num(angles[a1],N,a)
    if hallway_num == 'h':
        return 'r','r' #this was a roundoff error

    #check if parallel case
    if abs(angles[a1]-90) <= 10**(-10):
        line_yc = lines[a2][1][1] #y-cord of bottom parallel line
        line_angle = angles[a2]   #angle of bottom parallel line
        for i in range(len(lines)):
            if i != a2:
                if angles[i] == line_angle and lines[i][1][1] == line_yc:
                    l2_match = array_to_line(lines[i])
                    l2_length += l2_match.length
                    #print("paired line", lines[a2], "to line", lines[i])
                    #print("orig angle", angles[a2], "paired angle", angles[i])
                    #print("new length", l2_length, "added length", l2_match.length)

    #find direction of hallway push
    push_sign = get_push_sign(l1_length,l2_length)

    #push hallway
    #print("Line pair with angle", angles[a1], "belongs to hallway num", hallway_num)
    #print("Pushing hallway", hallway_num,"in direction of angle", angles[a1],"with sign", push_sign)
    hallway_set_temp = push_hallway(hallway_set,hallway_num,angles[a1],tolerance,push_sign,a)

    #reassemble sofa
    hallway_temp = set_to_poly(hallway_set_temp)

    if type(hallway_temp) is str or hallway_temp.geom_type != 'Polygon':
        return 'm','m' #incorrect geometry type (probably multigon)

    return hallway_temp,hallway_set_temp

def sanity_check(hallway,hallway_set,N,tolerance,k,a):
    '''N = number of hallways, tol = amount to push by, k = hallway num to push'''
    #create plot env
    fig = plt.figure(dpi=200, figsize=(4,4))
    ax=fig.add_subplot(111)

    #init hallway
    points,lines,angles = get_features(hallway,a)
    print("Initial Area: %f" %hallway.area)

    a1,a2 = balance_identifier(lines,angles,tolerance,k)
    print(angles)
    print(hallway_set)
    if a1 == -1 and a2 == -1:
        print("Got back poly is balanced")
        print("Dumping polygon data")
        print("LINES")
        print(np.array([lines]))
        for b in lines:
            print(array_to_line(b).length)
        print("ANGLES")
        print(np.array([angles]))
        print(distance_test(lines[1][0],lines[1][1],lines[7][1]))
        print(angles[1],angles[7])
        print(array_to_line(lines[1]).length,array_to_line(lines[7]).length)

    print("__________________________________________________________")

    #define line lengths
    l1 = array_to_line(lines[a1])
    l2 = array_to_line(lines[a2])
    l1_length = l1.length
    l2_length = l2.length
    l1lp = l1_length #used for plot title
    l2lp = l2_length #used for plot title
    ppa = angles[a1] #used for plot title
    if abs(angles[a1]-a) <= 10**(-10): #this method is obselete but ok for this function
        l2_length = l2_length*2 #bilat
        print("using bilat")
    print("angles: ",angles[a1],angles[a2])
    print("l1: ",lines[a1])
    print("l2: ",lines[a2])
    print("l1.length: ",l1_length)
    print("l2.length: ",l2_length)
    #manage bilat case

    print("____________________________________________________________")

    hallway_num = get_hallway_num(angles[a1],N,a)
    #hallway_num = next(i for i in range(len(angles)) if angles[i] == ppa)
    print("Line pair with angle %f belongs to hallway num %d" %(angles[a1],hallway_num))
    push_sign = get_push_sign(l1_length,l2_length)
    print("Pushing hallway %f in direction of angle %f with sign %d" % (hallway_num, angles[a1],push_sign))

    px2,py2 = hallway_set[hallway_num].exterior.xy
    ax.plot(px2,py2,color='blue',label='pre-push')

    print("Orig area: %f" %hallway.area)
    hallway_set = push_hallway(hallway_set,hallway_num,angles[a1],tolerance,push_sign,a)
    hallway = set_to_poly(hallway_set)
    print("Pushed area: %f" %hallway.area)

    print("____________________________________________________________")

    for j in range(len(hallway_set)):
        x,y = hallway_set[j].exterior.xy
        ax.plot(x,y,color='blue',alpha=0.3)

    px1,py1 = hallway_set[hallway_num].exterior.xy
    ax.plot(px1,py1,color='r',label='post_push')
    ax.set_title('N = %d, a=%f, L1=%f, L2=%f' %(N,hallway.area,l1lp,l2lp))
    plt.legend()
    ax.set_xlim([-2.55,1.25])
    ax.set_ylim([-0.75,2.25])
    ax.set_aspect(1)
    plt.show()


def try_push(hallway,hallway_set,N,tol,r,a):
    '''Takes polygon hallway obj, hallway_set a set of polygons, N the number of hallway intersections
    tol the amount to push by, r the recursion number (0 by default)'''

    #print('r:',r,'tol:',tol)
    #STAGE 0
    if r >= 10:
        return 're','re' #recursion error - no increase found after recursion lim

    #STAGE 1
    #keep track of how many angles we can iterate over
    points,lines,angles = get_features(hallway,a)
    #form list of angle nums randomly without repitition to iterate over
    k_vals = random.sample(range(len(angles)-1),len(angles)-2)
    #set initial attempt at increasing area
    hway_temp, hway_set = another_iteration(hallway,hallway_set,tol,N,k_vals[0],a)
    #set iterating variable
    i=1

    #DEBUGGING AREA 
    #print("type of hway_temp is: ",type(hway_temp))
    #DEBUGGING AREA

    #STAGE 2
    #If initial push was not an increase we loop over all angles until increase
    while (type(hway_temp) is str or hway_temp.area < hallway.area) and i<len(angles)-2:
                                                                   #if initial push didnt work try
                                                                   #until it does 
        if type(hway_temp) is not str and hway_temp.geom_type == 'Polygon':
            #print("TRU:",hallway.area,"TMP:",hway_temp.area)
            pass
        tol *= 1/5
        hway_temp,hway_set = another_iteration(hallway,hallway_set,tol,N,k_vals[i],a)
        i+=1

    #STAGE 3
    #if resulting hallway is 1) an error 2) a multigon 3) or still smaller
    if type(hway_temp) == str or hway_temp.geom_type != 'Polygon' or hway_temp.area < hallway.area:
        #then return error strings
        return try_push(hallway,hallway_set,N,tol*(1/10),r+1,a)

    #END
    #Return 
    #print("i:",i)

    if hway_temp.area < hallway.area:
        return hallway

    return hway_temp,hway_set

def get_carver(hallway_set):
    '''Takes hallway_set and returns polygon object used to smooth inside of sofa'''

    center_points_x = []
    center_points_y = []

    for k in range(1,len(hallway_set)-1):
        hway_len = len(hallway_set[k].exterior.xy[0])
        center_points_x.append(hallway_set[k].exterior.xy[0][0])
        center_points_y.append(hallway_set[k].exterior.xy[1][0])

    if True: #polynomial interp
        tpts = [n/N * 90 for n in range(1,N)]

        xtck = interpolate.splrep(tpts,center_points_x,s=0)
        ytck = interpolate.splrep(tpts,center_points_y,s=0)

        tpts = np.linspace(1/N*90, (N-1)/N*90, 100)

        xcp = list(interpolate.splev(tpts,xtck,der=0))
        ycp = list(interpolate.splev(tpts,ytck,der=0))

        xcp.append(center_points_x[round(len(center_points_x)/2)-1])
        ycp.append(-.4)

        carver = Polygon([(xcp[i],ycp[i]) for i in range(len(xcp))])

    if False: #piecewise lin carver
        center_points_x.append(center_points_x[round(len(center_points_x)/2)-1])
        center_points_y.append(-.4)
        carver = Polygon([(center_points_x[i],center_points_y[i]) for i in range(len(center_points_x))])


    #center_points_x.append(center_points_x[round(len(center_points_x)/2)-1])
    #center_points_y.append(-.4)
    #carver = Polygon([(center_points_x[i],center_points_y[i]) for i in range(len(center_points_x))])

    return carver

def main(N,hallway,hallway_set,tol,iterations,a,wireframe=True,smooth=True):
    #init vars and plotting logic
    start = time.time()
    plt.ion()
    plt.style.use('ggplot')
    fig = plt.figure(dpi=200)
    ax=fig.add_subplot(111)
    ax.set_xlim([-2.55,1.25])
    ax.set_ylim([-0.75,2.25])
    ax.set_aspect(1)

    points,lines,angles = get_features(hallway,a)

    if smooth:
        carver = get_carver(hallway_set)
        hallway_smth = hallway.difference(carver)
        ax.add_patch(PolygonPatch(rotate(hallway_smth,90-a,origin=(0,0)),fc='#0087C9',ec='grey'))
        smth_area = hallway_smth.area
        init_area = smth_area
        ax.set_title('N = %d, Area Change = %.16f, Area = %.16f' %(N, smth_area-init_area, smth_area))
    if not smooth:
        ax.add_patch(PolygonPatch(rotate(hallway,90-a,origin=(0,0)),fc='#0087C9',ec='grey'))
        new_area = hallway.area
        init_area = hallway.area
        ax.set_title('N = %d, Area Change = %.16f, Area = %.16f' %(N, new_area-init_area, new_area))

    fig.canvas.draw()
    plt.pause(1)

    #loop and push
    for i in range(iterations):
        print(i, hallway.area)
        hallway,hallway_set = try_push(hallway,hallway_set,N,tol,0,a)

        #if recursion depth is met we terminate
        if type(hallway) is str: #str is sign of recursion depth reached
            plt.ioff()
            plt.show()
            return 1

        #rotate visuals
        hallway_set_p = []
        for h in range(0,len(hallway_set)):
                hallway_set_p.append(rotate(hallway_set[h], 90-a,origin=(0,0)))
        hallway_p = set_to_poly(hallway_set_p)


        #reset canvas to redraw on
        fig.canvas.flush_events()
        plt.cla()

        ax.set_xlim([-3.1,2.25])
        ax.set_ylim([-1,2])
        ax.set_aspect(1)

        x,y = hallway_set_p[0].exterior.xy
        plt.plot(x,y,color='grey',linewidth=0.5)


        if wireframe:
            for i in range(1,len(hallway_set_p)):
                x,y = hallway_set_p[i].exterior.xy
                plt.plot(x,y,linewidth=0.2,color='grey')

        if smooth:
            carver = get_carver(hallway_set_p)
            hallway_smth = hallway_p.difference(carver)
            ax.add_patch(PolygonPatch(hallway_smth,fc='#0087C9',ec='grey'))
            smth_area = hallway_smth.area
            ax.set_title('N = %d, Area Change = %.16f, Area = %.16f' %(N, smth_area-init_area, smth_area),fontsize=10)
        if not smooth:
            ax.add_patch(PolygonPatch(hallway_p,fc='#0087C9',ec='grey'))
            new_area = hallway.area
            ax.set_title('N = %d, Area Change = %.16f, Area = %.16f' %(N, new_area-init_area, new_area),fontsize=10)

        fig.canvas.draw()


    #keeps figure open after completion
    fig.canvas.flush_events()
    plt.cla()
    ax.set_xlim([-2.55,1.25])
    ax.set_ylim([-0.75,2.25])
    ax.set_aspect(1)
    #ax.add_patch(PolygonPatch(hallway,fc='#FF5733'))

    if smooth:
        carver = get_carver(hallway_set_p)
        hallway_p = hallway_p.difference(carver)

    if wireframe:
        for i in range(1,len(hallway_set_p)):
            x,y = hallway_set_p[i].exterior.xy
            plt.plot(x,y,linewidth=0.2,color='grey')

    ax.add_patch(PolygonPatch(hallway_p,fc='#0087C9',ec='grey'))
    ax.set_title('N=%d, Area = %.16f' %(N, hallway.area),fontsize=10)
    #DEL ME

    print("--- %s --- seconds" %(time.time()-start))
    print("--- %f --- units/second " %(float(hallway.area-init_area)/float(time.time()-start)))
    plt.ioff()
    plt.show()

def balance(a,N,iterations,hallway,hallway_set,smooth=True):
    for i in range(iterations):
        tol = 1/10000
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

                flag = 0 #if turned to one program got stuck turned down tol

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
            return hallway,hallway_set,i

        if smooth == True:
            carver = get_carver(hallway_set)
            try:
                hallway_area = (hallway.difference(carver)).area
            except:
                print("failed to carve")
        if smooth == False:
            hallway_area = hallway.area

        print(i,":",hallway_area)


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

    hallway = rotate(hallway, 90-a, origin=(0,0))
    hallway_set[0] = rotate(hallway_set[0], 90-a, origin=(0,0))

    minx, miny, maxx, maxy = hallway.bounds


    plt.style.use('ggplot')
    fig = plt.figure(dpi=200,figsize=(5,3))
    ax=fig.add_subplot(111)
    ax.grid(False)
    ax.set_xlim([minx-.5,maxx+.5])
    ax.set_ylim([miny-.3,maxy+.5])
    ax.set_aspect(1)

    x,y = hallway_set[0].exterior.xy
    plt.plot(x,y,linewidth=.2,color='grey')

    ax.add_patch(PolygonPatch(hallway))
    plt.title(str(hallway.area)+ "N:" + str(N))
    fig.savefig("a:"+str(theta)+"_N:"+str(N)+"_Smth:"+str(smooth)+"_i:"+str(i)+".png",dpi=1200)
    dir_path = os.path.dirname(os.path.realpath(__file__))
    print("Saved plot to" + str(dir_path))
    #plt.show()

##########################################
##########################################
#there is a bit of extra code in this file
#I have not yet had time to clean up what
#can be removed. 
#The function balance() is mostly self-contained
#and serves as the brains for the program
##########################################
##########################################

print("----")
print("After the algorithm is unable to further interpolate the rotation path..")
print("It will self-terminate and save a plot of the result..")
print("In the location of sofa_balancer.py. You can also press...")
print(" 'enter' at any time to terminate the program and save the result...")
print("----")

print("Please enter the following options:")

a = int(input("Hallway bend degree (1 to 120): "))
N = int(input("Number of anchor points (5+): "))
iterations = 50000


#init vars
hallway = hallway_intersector(N,a,a)
hallway_set = hallway_list(N,a,a)
#balance
hallway, hallway_set, i = balance(a,N,iterations,hallway,hallway_set,smooth=True)
hallway = set_to_poly(hallway_set)


plot_saver(hallway,hallway_set,a,N,i,smooth=True)

























