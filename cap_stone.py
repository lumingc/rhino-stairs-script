import rhinoscriptsyntax as rs
import Rhino
import sys

#rs.DeleteObjects(rs.AllObjects())

def check_input(input): #check if user hits cancel
    if input is None:
        rs.MessageBox("canceling...quitting scripts...")
        sys.exit()

"""Ask for inputs"""
type = rs.GetBoolean("Select stairs type", ("type", "straight", "curvy/spiral"), True)[0]
check_input(type)
curve = rs.GetObject("Select a curve and make sure it's not parallel to the xy plane", rs.filter.curve)
check_input(curve)
start_pt = rs.CurveStartPoint(curve)
end_pt = rs.CurveEndPoint(curve)

if type:
    spiral = rs.GetBoolean("Select stairs type", ("type", "curvy", "spiral"), True)[0]
    if spiral:
        center = rs.GetPoint("Select the center point for your spiral stairs")

stair_width = rs.GetReal(message = "Enter stair width", number = 5)
check_input(stair_width)
steps = rs.GetInteger(message = "Enter steps", number = 20)
check_input(steps)
#base_height = rs.GetReal(message = "Enter base height", number = 0.5)

plinth = rs.GetBoolean("Plinth",("plinth","Disabled", "Enabled"), True)[0]
check_input(plinth)

plinth_lst = [plinth]
if plinth:
    plinth_height = rs.GetReal(message = "Enter plinth height", number = 1)
    check_input(plinth_height)
    plinth_thickness = rs.GetReal(message = "Enter plinth thickness", number = 0.3)
    check_input(plinth_thickness)
    if not type or not spiral:
        plinth_options = rs.CheckListBox([["left side", False], ["right side", False], ["both sides", True]], "which side(s)?")
        check_input(plinth_options)
    else:
        plinth_options = [("left", False),("right", True), ("both", False)]
    plinth_lst += [plinth_height, plinth_thickness, plinth_options]

bannister = rs.GetBoolean("Bannister",("bannister","Disabled", "Enabled"), True)[0]
check_input(bannister)
bannister_lst = [bannister]
if bannister:
    b_height = rs.GetReal(message = "Enter bannister height", number = 3)
    check_input(b_height)
    b_radius = rs.GetReal(message = "Enter bannister radius", number = 0.1)
    check_input(b_radius)
    b_col_num = rs.GetInteger(message = "Enter bannister column number", number = 5)
    check_input(b_col_num)
    b_col_radius = rs.GetReal(message = "Enter bannister column radius", number = 0.05)
    check_input(b_col_radius)
    if not type or not spiral:
        b_options = rs.CheckListBox([["left side", False], ["right side", False], ["both sides", True]], "which side(s)?")
        check_input(b_options)
    else:
        b_options = [("left", False),("right", True), ("both", False)]
    bannister_lst += [b_height, b_radius, b_col_num, b_col_radius, b_options]
""""""


def straight_plinth(spt, ept, stair_width, plinth_lst):
    p_height = [0, 0, plinth_lst[1]]
    p_lt = [-plinth_lst[2], 0, 0]
    p_rt = [plinth_lst[2] + stair_width, 0, 0]
    width = [stair_width, 0, 0]
    def build_left():
        p1 = [spt, rs.PointAdd(spt, p_height), rs.PointAdd(ept, p_height), ept]
        p2 = [rs.PointAdd(pt, p_lt) for pt in p1]
        rs.AddBox(p1+p2)
    def build_right():
        p1 = [spt, rs.PointAdd(spt, p_height), rs.PointAdd(ept, p_height), ept]
        p3 = [rs.PointAdd(pt, p_rt) for pt in p1]
        p4 = [rs.PointAdd(pt, width) for pt in p1]
        rs.AddBox(p4+p3)
    if plinth_lst[3][2][1]:
        build_left()
        build_right()
    elif plinth_lst[3][0][1]:
        build_left()
    else:
        build_right()



def curvy_plinth(curve, ref, stair_width, plinth_lst):

    def right():
        spt = rs.CurveStartPoint(curve)
        l = rs.OffsetCurve(curve, [-1,0,0], plinth_lst[2])
        l_p = rs.AddEdgeSrf([curve, l])
        guide_curve1 = rs.AddLine(spt, rs.PointAdd(spt, [0,0, plinth_lst[1]]))
        rs.ExtrudeSurface(l_p, guide_curve1)
        rs.DeleteObjects([guide_curve1, l])

    def left(): #very very computationally heavy. Be patient
        spt = rs.CurveStartPoint(ref)
        r = rs.OffsetCurve(ref, [1,0,0], plinth_lst[2])
        r_p = rs.AddEdgeSrf([ref, r])
        guide_curve2 = rs.AddLine(spt, rs.PointAdd(spt, [0,0, plinth_lst[1]]))
        rs.ExtrudeSurface(r_p, guide_curve2)
        rs.DeleteObjects([guide_curve2, r])

    if plinth_lst[3][2][1]:
        left()
        right()
    elif plinth_lst[3][0][1]:
        left()
    else:
        right()

def straight_bannister(spt, ept, stair_width, b_lst):
    bh = (0, 0, b_lst[1])
    radius = b_lst[2]
    col_spacing = [0, (ept[1] - spt[1])/(b_lst[3] - 1), (ept[2] - spt[2])/(b_lst[3] - 1)]

    def left(spt, ept):
        l_base = rs.PointAdd(spt, bh)
        l_height = rs.PointAdd(ept, bh)
        rs.AddCylinder(l_base, l_height, radius)

        #build columns
        for i in range(b_lst[3]):
            rs.AddCylinder(spt, l_base, b_lst[4])
            spt = rs.PointAdd(spt, col_spacing)
            l_base = rs.PointAdd(l_base, col_spacing)

    def right(spt, ept):
        width = [stair_width, 0, 0]
        r_base = rs.PointAdd(rs.PointAdd(spt, bh), width)
        r_height = rs.PointAdd(rs.PointAdd(ept, bh), width)
        rs.AddCylinder(r_base, r_height, radius)
        #build columns
        for i in range(b_lst[3]):
            rs.AddCylinder(rs.PointAdd(spt, width), r_base, b_lst[4])
            spt = rs.PointAdd(spt, col_spacing)
            r_base = rs.PointAdd(r_base, col_spacing)

    if b_lst[5][2][1]:
        left(spt, ept)
        right(spt, ept)
    elif b_lst[5][0][1]:
        left(spt, ept)
    else:
        right(spt, ept)


def curvy_bannister(curve, ref, stair_width, b_lst):
    ref_pts = [n * 1/(b_lst[3] - 1) for n in range(b_lst[3])]

    def left():
        l_curve = rs.CopyObject(ref,[0,0,b_lst[1]])
        rs.AddPipe(l_curve, 0, b_lst[2], cap = 1)
        rs.DeleteObjects(l_curve)
        pts = [rs.EvaluateCurve(ref, t) for t in ref_pts]
        for i in range(b_lst[3]):
            base = rs.PointAdd(pts[i], [0, 0, b_lst[1]])
            rs.AddCylinder(pts[i], base, b_lst[4])

    def right():
        r_curve = rs.CopyObject(curve,[0,0,b_lst[1]])
        rs.AddPipe(r_curve, 0, b_lst[2], cap = 1)
        rs.DeleteObjects(r_curve)
        pts = [rs.EvaluateCurve(curve, t) for t in ref_pts]
        for i in range(b_lst[3]):
            base = rs.PointAdd(pts[i], [0, 0, b_lst[1]])
            rs.AddCylinder(pts[i], base, b_lst[4])

    if b_lst[5][2][1]:
        left()
        right()
    elif b_lst[5][0][1]:
        left()
    else:
        right()


def straight_stairs(start_pt, end_pt, stair_width, steps, plinth_lst, bannister_lst):
    height = end_pt[2] - start_pt[2]
    rise = [0,0,height/steps]
    length = end_pt[1] - start_pt[1]
    run = [0,length/steps, 0]
    width = [stair_width, 0, 0]

    #back surface
    rs.AddSrfPt([start_pt, end_pt, rs.PointAdd(end_pt, width), rs.PointAdd(start_pt, width)])

    #plinth
    if plinth_lst[0]:
        straight_plinth(start_pt, end_pt, stair_width, plinth_lst)

    #bannister
    if bannister_lst[0]:
        straight_bannister(start_pt, end_pt, stair_width, bannister_lst)

    for i in range(steps):
        #vertices for rise surfaces:
        v_ver = [start_pt, rs.PointAdd(start_pt, rise), rs.PointAdd(rs.PointAdd(start_pt, width), rise), rs.PointAdd(start_pt, width)]

        #draw rise
        rs.AddSrfPt(v_ver)
        #update start_pt
        start_pt = rs.PointAdd(start_pt, rs.PointAdd(rise, run))
        #vertices for run surfaces:
        v_hori = [v_ver[1], v_ver[2], rs.PointAdd(start_pt, width), start_pt]
        #draw run
        rs.AddSrfPt(v_hori)

        #draw sides
        rs.AddSrfPt([v_ver[0], v_ver[1], start_pt])
        rs.AddSrfPt([v_ver[3], v_ver[2], v_hori[2]])

def curvy_stairs(curve, start_pt, end_pt, stair_width, steps, plinth_lst, bannister_lst):
    ref = rs.OffsetCurve(curve, [1,0,0], stair_width) # create the second curve to guide the stair
    ref_pts = [n * 1/steps for n in range(steps + 1)] # guide points to divide up the curve
    left_pts = [rs.EvaluateCurve(curve, t) for t in ref_pts] # guide points on input curve
    right_pts = [rs.EvaluateCurve(ref, t) for t in ref_pts] #guide points on the offset curve
    height = end_pt[2] - start_pt[2] #stair height
    rise = [0,0,height/steps] # a vector

    for i in range(steps):
        #draw rise
        v_ver = [left_pts[i], right_pts[i], rs.PointAdd(right_pts[i], rise), rs.PointAdd(left_pts[i], rise)]
        rs.AddSrfPt(v_ver)

        #draw run
        v_hori =[v_ver[3], v_ver[2], right_pts[i+1], left_pts[i+1]]
        rs.AddSrfPt(v_hori)

        #draw sides
        s1 = rs.AddLine(left_pts[i], rs.PointAdd(left_pts[i], rise))
        s2 = rs.AddLine(rs.PointAdd(left_pts[i], rise), left_pts[i+1])
        s3 = rs.AddSubCrv(curve, rs.CurveClosestPoint(curve, left_pts[i]), rs.CurveClosestPoint(curve, left_pts[i+1]))
        rs.AddEdgeSrf([s1,s2, s3])
        rs.DeleteObjects([s1, s2, s3])
        s1 = rs.AddLine(right_pts[i], rs.PointAdd(right_pts[i], rise))
        s2 = rs.AddLine(rs.PointAdd(right_pts[i], rise), right_pts[i+1])
        s3 = rs.AddSubCrv(ref, rs.CurveClosestPoint(ref, right_pts[i]), rs.CurveClosestPoint(ref, right_pts[i+1]))
        rs.AddEdgeSrf([s1,s2,s3])
        rs.DeleteObjects([s1, s2, s3])

    s1 = rs.AddLine(left_pts[0], right_pts[0])
    s2 = rs.AddLine(left_pts[-1], right_pts[-1])
    rs.AddEdgeSrf([s1, curve, s2, ref])
    rs.DeleteObjects([s1, s2])

    if plinth_lst[0]:
        curvy_plinth(curve, ref, stair_width, plinth_lst)

    if bannister_lst[0]:
        curvy_bannister(curve, ref, stair_width, bannister_lst)

def spiral_stairs(curve, center, start_pt, end_pt, stair_width, steps, plinth_lst, bannister_lst):
    height = end_pt[2] - start_pt[2]
    cen = rs.AddLine(center, rs.PointAdd(center, [0, 0, height]))
    cen_e = rs.CurveEndPoint(cen)
    ref_pts = [n * 1/steps for n in range(steps + 1)]
    outer_pts = [rs.EvaluateCurve(curve, t) for t in ref_pts]
    inner_pts = [[cen_e[0], cen_e[1], cen_e[2] * t] for t in ref_pts]
    print(inner_pts)
    rise = [0,0,height/steps]

    for i in range(steps):
        #draw rise
        v_ver = [outer_pts[i], inner_pts[i], rs.PointAdd(inner_pts[i], rise), rs.PointAdd(outer_pts[i], rise)]
        rs.AddSrfPt(v_ver)

        #draw run
        v_hori =[v_ver[3], v_ver[2], outer_pts[i+1]]
        rs.AddSrfPt(v_hori)

        #draw sides
        s1 = rs.AddLine(outer_pts[i], rs.PointAdd(outer_pts[i], rise))
        s2 = rs.AddLine(rs.PointAdd(outer_pts[i], rise), outer_pts[i+1])
        s3 = rs.AddSubCrv(curve, rs.CurveClosestPoint(curve, outer_pts[i]), rs.CurveClosestPoint(curve, outer_pts[i+1]))
        rs.AddEdgeSrf([s1,s2, s3])
        rs.DeleteObjects([s1, s2, s3])

    if plinth_lst[0]:
        curvy_plinth(curve, None, stair_width, plinth_lst)

    if bannister_lst[0]:
        curvy_bannister(curve, None, stair_width, bannister_lst)


if rs.IsLine(curve):
    straight_stairs(start_pt, end_pt, stair_width, steps, plinth_lst, bannister_lst)
else:
    if not spiral:
        curvy_stairs(curve, start_pt, end_pt, stair_width, steps, plinth_lst, bannister_lst)
    else:
        spiral_stairs(curve, center, start_pt, end_pt, stair_width, steps, plinth_lst, bannister_lst)
