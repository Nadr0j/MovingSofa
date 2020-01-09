# <p align='center'> Software for the Moving Sofa Problem </p>

Software developed under the mentorship of Professor of Mathematics Dan Romik at the University of California, Davis.
Please click the document titled "An Algorithm for Balancing Sofas" for a complete description of the project. The gif below shows a short run of the algorithm on a low resolution discrete approximation. Keep scrolling to get into the nitty-gritty.

![Algorithm Run with 6 Anchor Points](media/n=6_ns.gif)

# Abstract

Posed by Leo Moser in 1966, the moving sofa problem remains unsolved. In 1992, Joseph Gerver constructed a sofa which he conjectured to be the optimal solution to Moser's problem. However, Gerver provided no proof of this conjecture and to this date it remains unproven. Making use of Gerver's observations, we develop a variant of Phillip Gibbs' algorithm which provides computational evidence for Gerver's conjecture. We begin the paper by describing how we can approximate solutions to the moving sofa problem using the intersection of a finite number of polygons. Then, we show how we can increase the size of the approximation using Gerver's observations. Finally, we provide a description of the developed algorithm and show that the produced approximation seems to converge in shape and area to Gerver's construction. In the last two sections we briefly describe how to install and use our implementation of the algorithm *sofa_gui.py*. This project was done under the mentorship of Professor Dan Romik at the University of California, Davis.

# A Brief History of the Problem

In 1966, Leo Moser asked the question
>"what is the shape of largest area in the plane that can be moved around a right-angled corner in a two-dimensional hallway of width 1?"

Despite the problem's simple statement, it remains unsolved. Notable points of progess in the problem's history begin in 1968 with the work of John Hammersley who conjectured that his construction (as seen below) of area 2/pi + pi/2 = 2.2074... was optimal. 

<p align='center'><img src="https://github.com/Nadr0j/MovingSofa/blob/master/media/Hammersley.png" width="400"></p>

In 1992 came the work of Joseph Gerver who found a valid construction (as seen below) of area 2.2195... which was a modest improvement over Hammersley's construction.

<p align='center'><img src="https://github.com/Nadr0j/MovingSofa/blob/master/media/Gerver.png" width="400"></p>

However, Gerver's results were interesting for reasons other than an increase in area over Hammersley's sofa. Derived from considerations of local optimality, Gerver conjectured that his construction was indeed the solution to Moser's 1966 question. Despite the fact that Gerver's construction remains the largest discovered to date, his conjecture of global optimality remains unproven.

# Discrete Approximations
## Notation
We begin by defining the sofa in terms of a rotating coordinate frame. Consider the L-shaped hallway that a candidate sofa moves through as given by

<p align='center'><img src="https://github.com/Nadr0j/MovingSofa/blob/master/media/eq1.png"></p>

Let R <sub>t</sub> denote the rotation matrix

<p align='center'><img src="https://github.com/Nadr0j/MovingSofa/blob/master/media/eq2.png"></p>

Then we let S be a planar shape which satisfies

<p align='center'><img src="https://github.com/Nadr0j/MovingSofa/blob/master/media/eq3.png"></p>

Where <img src="https://github.com/Nadr0j/MovingSofa/blob/master/media/eq4.png"> is a continuous path satisfying *x(0) = (0,0)* which defines the movement of the inner corner of L. As in Romik's 2016 paper, we call *x(t)* the *rotation path*. Only *x(t)* which produces connected shapes will be considered. All S defined in this way will be able to traverse the L-shaped hallway. For simplicity's sake, we can enforce the same restrictions on S by combining the horizontal hallway and the rotated vertical hallway to create one long horizontal hallway. Let
<p align='center'><img src="https://github.com/Nadr0j/MovingSofa/blob/master/media/eq5.png"></p>
Now define

<p align='center'><img src="https://github.com/Nadr0j/MovingSofa/blob/master/media/eq6.png"></p>

Consider then, for any given **x(t)** a sampling of **N+1** equidistant nodes. More specifically, call <img src="https://github.com/Nadr0j/MovingSofa/blob/master/media/eq7.png"> the set of anchor points which satisfy <img src="https://github.com/Nadr0j/MovingSofa/blob/master/media/eq8.png">. For the sake of simplifying notation, let <img src="https://github.com/Nadr0j/MovingSofa/blob/master/media/eq9.png">.
