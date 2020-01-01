import numpy as np
from numpy.random import randint
from math import cos, sin, pi, atan2,exp
from shapely.ops import linemerge,polygonize_full,Polygon
from shapely.affinity import rotate,translate
from shapely.geometry import box,Point,LineString #use to create hallways
from shapely.geometry.polygon import LinearRing
from descartes import PolygonPatch #to help matplotlib plot polygons
from matplotlib import pyplot as plt #to plot polygons
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, FigureCanvasAgg
from matplotlib.figure import Figure
import PySimpleGUI as sg
import random
import copy

def rm(t):
    """Define a rotation matrix evaluated at angle 0<=t<=pi/2 and returned"""
    A = np.array([[cos(t),-sin(t)],[sin(t),cos(t)]])
    return A

def generate_hallway(t,a_param,b_param):
    """Generate hallway :)"""

    xtf = xt(t,a_param,b_param)

    #points for l_vert
    v1 = xtf + np.array(list(rotate(Point(0,1),t,origin=(0,0)).coords)[0])
    v2 = xtf + np.array(list(rotate(Point(1,1),t,origin=(0,0)).coords)[0])
    v3 = xtf + np.array(list(rotate(Point(1,-10),t,origin=(0,0)).coords)[0])
    v4 = xtf + np.array(list(rotate(Point(0,-10),t,origin=(0,0)).coords)[0])
    #points for l_horiz
    h1 = xtf + np.array(list(rotate(Point(-10,1),t,origin=(0,0)).coords)[0])
    h2 = xtf + np.array(list(rotate(Point(1,1),t,origin=(0,0)).coords)[0])
    h3 = xtf + np.array(list(rotate(Point(1,0),t,origin=(0,0)).coords)[0])
    h4 = xtf + np.array(list(rotate(Point(-10,0),t,origin=(0,0)).coords)[0])

    hallway = Polygon([h1,h2,h3,h4]).union(Polygon([v1,v2,v3,v4]))

    return hallway

def hallway_intersector(N):
    """WRITE THIS TOMORROW :)"""
    hallways = []
    hallways.append(Polygon([(-10,0),(-10,1),(10,1),(10,0)]))
    #<- angle subdivisions
    for i in range(1, N):
        t = 90 * i/N
        hallways.append(generate_hallway(t))

    final_shape = hallways[0]
    for i in hallways:
        final_shape = final_shape.intersection(i)

    house = box(-10,-20,1,20)

    final_shape = final_shape.intersection(house)

    return final_shape

def hallway_list(N,a_param,b_param):
    """Takes int N and returns array of rotated hallways"""
    hallways = []
    hallways.append(Polygon([(-10,0),(-10,1),(10,1),(10,0)]))
    #<- angle subdivisions
    for i in range(1, N):
        t = 90 * i/N
        hallways.append(generate_hallway(t,a_param,b_param))

    house = box(-10,-20,10,20)
    hallways.append(house)

    return hallways

def xt(t,a_param,b_param):
    """Define rotation path"""
    a = 2/pi-.2+a_param
    b = 2/pi-.5+b_param
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
    '''Takes list of points of form [[x,y],[x,y],...]. Returns list of lines
    in form [[[x1,y1],[x2,y2]],[[x2,y2],[x3,y3],...,[[xn,yn],[x1,y1]]]'''

    lines = []
    for p in range(len(points)-1):
        lines.append([[points[p][0],points[p][1]],[points[p+1][0],
                     points[p+1][1]]])

    return lines

def lines_to_angles(lines):
    '''takes lines turns them into angles'''
    angles = []

    for line in lines:
        x1,y1 = line[0][0],line[0][1]
        x2,y2 = line[1][0],line[1][1]

        if y1==y2:
            theta = 0 #angle from pos x axis
        if x1==x2:
            theta = -pi/2 #angle from pos x axis
        if y1 > y2:
            theta = atan2(y2-y1,x2-x1)
        if y1 < y2:
            theta = atan2(y1-y2,x1-x2)

        angles.append(theta*180/pi+90)


    return angles

def array_to_line(line):
    '''Takes [[a,b],[c,d]] and returns LineString
    w/ pt1 = (a,b) and pt2 = (c,d)'''
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
    '''Takes lines and angles which define hallway. Searches for lines w/
    same angle of rotation relative to y axis which are also one unit
    apart and returns. Tolerance determines how close line
    lengths need to be to be considered balanced'''

    for a2 in range(len(angles)):
        if a2 != a1: #don't check the same index number
            if abs(angles[a1] - angles[a2]) <= 10**(-10): #lines are parallel
                l1 = array_to_line(lines[a1])
                l2 = array_to_line(lines[a2])
                line_dist = distance_test(lines[a1][0],lines[a1][1],
                                                       lines[a2][0])
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
                if abs(line_dist-1) <= 10**(-10) and \
                   abs(l1_length-l2_length) > 10**(-20):
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

def get_hallway_num(angle,N):
    '''Takes angle of parallel lines and finds
    corresponding hallway index num '''
    i = 0 #index num

    if abs(angle) <= 10**(-16):
        return 'h' #this should be an error... I think
    if  abs(angle-90) <= 10**(-16):
        return 0 #the horizontal lines are a special case always belonging to 0
    if angle > 0: #line pairs belonging to lvert
        i = N*angle/90
    if angle < 0: #line pairs beloning to lhoriz
        i = N + N*angle/90

    return int(round(i))

def set_to_poly(s):
    '''takes set of hallway polygons (type: geom).
    Intersects them and returns final polygon'''
    final_shape = s[0]

    for hallway in s:
        try:
            final_shape = final_shape.intersection(hallway)
        except:
            return 'er' #return error string

    return final_shape

def get_push_sign(l1,l2):
    if l1 > l2:
        return -1
    if l2 > l1:
        return 1

def push_hallway(hallway_set,hallway_num,angle,d,sign):
    '''Takes hallway set & hallway num along w/ d=tolerance which determines
    how much to push the hallway by in push dir. Returns hallway set'''
    hallway_set_temp = copy.copy(hallway_set)
    if abs(abs(angle)-90)<=10**(-10) : #special verticle case
        for i in range(1,len(hallway_set)-1):
            hallway_set_temp[i] = translate(hallway_set_temp[i],
                    sign*d*cos(angle*pi/180),sign*d*sin(angle*pi/180))
        return hallway_set_temp
    else:
        hallway_set_temp[hallway_num] = translate(hallway_set_temp[hallway_num],
                              sign*d*cos(angle*pi/180),sign*d*sin(angle*pi/180))
        return hallway_set_temp

def get_features(hallway):
    '''returns points,lines,angles which define hallway.
    To simplify other code'''
    points = get_poly_points(hallway)
    lines = points_to_lines(points)
    angles = lines_to_angles(lines)

    return points,lines,angles

def another_iteration(hallway,hallway_set,tolerance,N,k):
    '''Takes hallway, halway_set, tolerance and N = #num of hallway
    Finds unbalanced edges and pushes hallway set in orthogonal direction to
    unbalanced edges. Returns updated hallway and hallway_set'''

    #get hallway data to make push
    points,lines,angles = get_features(hallway)

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
    hallway_num = get_hallway_num(angles[a1],N)
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

    #find direction of hallway push
    push_sign = get_push_sign(l1_length,l2_length)

    #push hallway
    hallway_set_temp = push_hallway(hallway_set,hallway_num,angles[a1],
                                    tolerance,push_sign)

    #reassemble sofa
    hallway_temp = set_to_poly(hallway_set_temp)

    if type(hallway_temp) is str or hallway_temp.geom_type != 'Polygon':
        return 'm','m' #incorrect geometry type (probably multigon)

    return hallway_temp,hallway_set_temp

def try_push(hallway,hallway_set,N,tol,r):
    '''Takes polygon hallway obj, hallway_set a set of polygons,
       N the number of hallway intersections tol the amount to push by,
       r the recursion number (0 by default)'''

    #STAGE 0
    if r >= 10:
        return 're','re' #recursion error - no increase by recursion lim

    #STAGE 1
    #keep track of how many angles we can iterate over
    points,lines,angles = get_features(hallway)
    #form list of angle nums randomly without repitition to iterate over
    k_vals = random.sample(range(len(angles)-1),len(angles)-2)
    #set initial attempt at increasing area
    hway_temp, hway_set = another_iteration(hallway,hallway_set,tol,N,k_vals[0])
    #set iterating variable
    i=1

    #STAGE 2
    #If initial push was not an increase we loop over all angles until increase
    while (type(hway_temp) is str or hway_temp.area < hallway.area) and \
                                    i<len(angles)-2:
                                                 #if initial push didnt work try
                                                 #until it does 
        if type(hway_temp) is not str and hway_temp.geom_type == 'Polygon':
            #print("TRU:",hallway.area,"TMP:",hway_temp.area)
            pass
        tol *= 1/5
        hway_temp,hway_set = another_iteration(hallway,hallway_set,
                                                    tol,N,k_vals[i])
        i+=1


    #STAGE 3
    #if resulting hallway is 1) an error 2) a multigon 3) or still smaller
    if type(hway_temp) == str or hway_temp.geom_type != 'Polygon' or \
                                hway_temp.area < hallway.area:
        #then return error strings
        return try_push(hallway,hallway_set,N,tol*(1/10),r+1)

    #END
    #Return 
    #print("i:",i)
    return hway_temp,hway_set

def get_carver(hallway_set):
    '''Takes hallway_set and returns polygon object
        used to smooth inside of sofa'''

    center_points_x = []
    center_points_y = []

    for k in range(1,len(hallway_set)-1):
        hway_len = len(hallway_set[k].exterior.xy[0])
        center_points_x.append(hallway_set[k].exterior.xy[0][hway_len-3])
        center_points_y.append(hallway_set[k].exterior.xy[1][hway_len-3])

    center_points_x.append(center_points_x[round(len(center_points_x)/2)-1])
    center_points_y.append(-.4)
    carver = Polygon([(center_points_x[i],center_points_y[i]) \
             for i in range(len(center_points_x))])

    return carver

def draw_figure(canvas,figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure,canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top',fill='both',expand=1)
    return figure_canvas_agg

def main():

    ###### GUI LOGIC ######
    iterations=100 #needed to init progress bar
    #define window layout
    sg.LOOK_AND_FEEL_TABLE['Reddit']['BORDER'] = 0
    sg.change_look_and_feel('Reddit')

    btn_layout = [
                [sg.Button('Run'),sg.Button('Preview Sofa', key='preview'), \
                    sg.Button('Stop')],
                ]

    col = [
            [sg.Text('Please enter the following values',size=(30,3), \
                font=('Helvetica',12), justification='center')],
            [sg.Text('Number of Anchor Points', size=(30,2)), \
                sg.InputCombo(values=(1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16, \
                    17,18,19,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35, \
                    36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55, \
                    56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75, \
                    76,77,78,79,80,81,82,83,84,85,86,87,88,89,91,92,93,94,95,96, \
                    97,98,99,100,128,256,512,\
                    1024), key='N', size=(8,10),tooltip='whole number input')],
            [sg.Text('Number of Iterations', size=(30,2)), sg.InputText( \
                key='iterations',size=(10,2),tooltip='whole number input')],
            [sg.Text('Show Hallway Outlines', size=(30,2)), sg.OptionMenu( \
                values = ('True', 'False'), key='outline',size=(10,2))],
            [sg.Text('Smooth Sofa Object', size=(30,2)), sg.OptionMenu( \
                values=('True','False'),key='smooth',default_value='False', \
                size=(10,2))],
            [sg.Text('Hallway placement (height)', size=(30,1)), sg.Slider( \
                range=(0,5), orientation='h', size=(10,10), default_value=5,\
                key='b-param')],
            [sg.Text('Hallway placement (width)', size=(30,1)), sg.Slider( \
                range=(0,2), orientation='h', size=(10,10), default_value=2,\
                key='a-param')],
            [sg.Frame('',btn_layout,border_width=0,pad=((50,0),(50,0)))],
            [sg.ProgressBar(iterations,orientation='h',pad=((65,0),(10,0)), \
                size=(20,20),key='progressbar')]
          ]

    layout = [
                [sg.Canvas(key='-CANVAS-'),sg.VerticalSeparator( \
                    pad=((0,30),(43,43))),sg.Column(col),]
            ]

    #plotting logic so initial grid displays
    plt.style.use('ggplot')
    fig = Figure()
    ax=fig.add_subplot(111)

    #define window layout
    window = sg.Window('Moving Sofa Balancer',layout,finalize=True) # window
    canvas_elem = window.FindElement('-CANVAS-') #identify canvas elem
    canvas = canvas_elem.TKCanvas #place in TK
    fig_agg = draw_figure(canvas,fig)
    progress_bar = window['progressbar']

    while True:
        #lets user preview sofas until run is pressed
        while True:
            ax.cla()
            events, values = window.read() #read arg vals into vars
            #----read arguments 

            # Provide a way out when user closes program
            if events in ('Exit', None):
                window.close()
                exit(-1)

            try:
                test_var1 = int(values['N'])
                test_var2 = int(values['iterations'])
            except:
                sg.Popup('One or more inputs of incorrect type.',
                              title='Type Err', line_width=30)
                continue

            N = int(values['N']) + 1
            if N <= 8:
                tol = 1/50
            if 18 > N > 8:
                tol = 1/150
            if 30 > N > 18:
                tol = 1/500
            if 60 > N > 30:
                tol= 1/1000
            if N > 60:
                tol = 1/5000
            if N > 120:
                tol = 1/50000

            iterations = int(values['iterations'])
            wireframe = bool(values['outline'] == 'True')
            smooth = bool(values['smooth'] == 'True')
            a_param = int(values['a-param'])/10
            b_param = int(values['b-param'])/10
            #----make hallway objs based on args
            hallway_set = hallway_list(N,a_param,b_param)
            hallway = set_to_poly(hallway_set)
            #init vars and plotting logic
            minx,miny,maxx,maxy = hallway.bounds

            ax.set_xlim([-2.75,1.5])
            ax.set_ylim([-1,2])
            ax.set_aspect(1)

            if smooth:
                carver = get_carver(hallway_set)
                hallway_smth = hallway.difference(carver)
                ax.add_patch(PolygonPatch(hallway_smth,fc='#0087C9',ec='grey'))
                smth_area = hallway_smth.area
                init_area = smth_area
                ax.set_title('Area Change = %.16f, Area = %.16f' %( \
                    smth_area-init_area, smth_area),fontsize=10)

            if not smooth:
                ax.add_patch(PolygonPatch(hallway,fc='#0087C9',ec='grey'))
                new_area = hallway.area
                init_area = hallway.area
                ax.set_title('Area Change = %.16f, Area = %.16f' %( \
                    new_area-init_area, new_area),fontsize=10)

            if wireframe:
                for i in range(1,len(hallway_set)):
                    x,y = hallway_set[i].exterior.xy
                    ax.plot(x,y,linewidth=0.2)

            fig_agg.draw()
            if events in ('Run', None):
                break
            if events in ('Exit', None):
                exit(-1)

        #loop and push
        for i in range(iterations):
            event, values = window.Read(timeout=0.01)
            if event in ('Exit', None):
                window.close()
                exit(-1)
            if event in ('Stop', None):
                break

            progress_bar.UpdateBar(i+1,iterations)

            hallway,hallway_set = try_push(hallway,hallway_set,N,tol,0)

            #if recursion depth is met we terminate
            if type(hallway) is str: #str is sign of recursion depth reached
                exit(1)
                return 1

            #reset canvas to redraw on
            ax.cla()
            plt.cla()

            ax.set_xlim([-2.75,1.5])
            ax.set_ylim([-1,2])
            ax.set_aspect(1)

            x,y = hallway_set[0].exterior.xy
            ax.plot(x,y,color='grey',linewidth=0.5)

            if wireframe:
                for i in range(1,len(hallway_set)):
                    x,y = hallway_set[i].exterior.xy
                    ax.plot(x,y,linewidth=0.2)

            if smooth:
                carver = get_carver(hallway_set)
                hallway_smth = hallway.difference(carver)
                ax.add_patch(PolygonPatch(hallway_smth,fc='#0087C9',ec='grey'))
                smth_area = hallway_smth.area
                ax.set_title('Area Change = %.16f, Area = %.16f' %( \
                    smth_area-init_area, smth_area),fontsize=10)
            if not smooth:
                ax.add_patch(PolygonPatch(hallway,fc='#0087C9',ec='grey'))
                new_area = hallway.area
                ax.set_title('Area Change = %.16f, Area = %.16f' %( \
                    new_area-init_area, new_area),fontsize=10)

            fig_agg.draw()


        #keeps figure open after completion
        plt.cla()
        ax.set_xlim([minx-.5,maxx+.5])
        ax.set_ylim([miny-.25,maxy+.5])
        ax.set_aspect(1)
        #ax.add_patch(PolygonPatch(hallway,fc='#FF5733'))

        if smooth:
            carver = get_carver(hallway_set)
            hallway = hallway.difference(carver)

        if wireframe:
            for i in range(1,len(hallway_set)):
                x,y = hallway_set[i].exterior.xy
                ax.plot(x,y,linewidth=0.2)

        ax.add_patch(PolygonPatch(hallway,fc='#0087C9',ec='grey'))
        ax.set_title('N=%d, Area = %.16f' %(N, hallway.area),fontsize=10)

        #DEL ME

if __name__ == '__main__':
    main()


























