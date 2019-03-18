import json
import Rhino
import Rhino.Geometry as rg
import rhinoscriptsyntax as rs

# Clear canvas
rs.DeleteObjects(rs.AllObjects(select=True))

# Add relevant layers (if they don't exist)
layers = {'Structure': ['s_points', 's_lines', 's_areas'], 
          'Strip A': ['CSA', 'MSA'], 'Strip B': ['CSB', 'MSB']}

for key in layers.keys():
    if rs.IsLayer(key):
        rs.DeleteLayer(key)
    rs.AddLayer(key)
    sublayers = layers[key]
    for sublayer in sublayers:
        rs.AddLayer(sublayer, parent=key)

# Change layer colors for strips (increase visibility)
rs.LayerColor('CSA', color=(255,0,0))
rs.LayerColor('CSB', color=(255,0,0))
rs.LayerColor('MSA', color=(0,0,255))
rs.LayerColor('MSB', color=(0,0,255))

# Load data
with open('data.json') as fh:
    data = json.load(fh)

points = data['OBJECT GEOMETRY - POINT COORDINATES']
lines  = data['OBJECT GEOMETRY - LINES 01 - GENERAL']
areas  = data['OBJECT GEOMETRY - AREAS 01 - GENERAL']
design_strips = data['OBJECT GEOMETRY - DESIGN STRIPS']

# Add structural points 
for key, attr in points.iteritems():
    rs.CurrentLayer('s_points')
    obj = rs.AddPoint([attr['GlobalX'],attr['GlobalY'], attr['GlobalZ']])
    if obj:
        rs.ObjectName(obj, str(key))

# Add structural lines
for key, attr in lines.iteritems():
    rs.CurrentLayer('s_lines')
    start = rs.coerce3dpoint(rs.ObjectsByName('Point ' + attr['PointI'])[0])
    end   = rs.coerce3dpoint(rs.ObjectsByName('Point ' + attr['PointJ'])[0])
    if start and end:
        rs.AddLine(start, end)
        
# Add structural areas
for key, attr in areas.iteritems():
    rs.CurrentLayer('s_areas')
    numPoints = int(attr['NumPoints'])
    point_list = []
    for i in xrange(numPoints):
        point_list.append(rs.coerce3dpoint(rs.ObjectsByName('Point ' + attr['Point' + str(i + 1)])[0]))
    point_list.append(point_list[0])
    outline = rs.AddPolyline(point_list)
    if attr['AreaType'] != 'Slab':
        rs.AddPlanarSrf(outline)
    
# Add existing design strips
for key in design_strips.keys():
    # select appropriate layer
    if 'CSA' in key:
        rs.CurrentLayer('CSA')
    if 'MSA' in key:
        rs.CurrentLayer('MSA')
    if 'CSB' in key:
        rs.CurrentLayer('CSB')
    if 'MSB' in key:
        rs.CurrentLayer('MSB')
    numPoints = len(design_strips[key])
    z_vector = rg.Vector3d(0.0, 0.0, 1.0)
    point_list = []
    for i in xrange(len(design_strips[key])):
        point_list.append(rg.Point3d(float(design_strips[key][i]['GlobalX']),
                                           float(design_strips[key][i]['GlobalY']),
                                                 1.0))
        if i != 0:
            start = point_list[i - 1]
            end = point_list[i]
            v01 = rg.Vector3d.Subtract(rg.Vector3d(end), rg.Vector3d(start))
            rg.Vector3d.Unitize(v01)
            v_rh = rg.Vector3d.CrossProduct(z_vector, v01)
            st_lo = rg.Point3d.Add(start, rg.Vector3d.Multiply(float(design_strips[key][i - 1]['WALeft']), v_rh))
            st_ro = rg.Point3d.Add(start, rg.Vector3d.Multiply(-1*float(design_strips[key][i - 1]['WARight']), v_rh))
            end_lo = rg.Point3d.Add(end, rg.Vector3d.Multiply(float(design_strips[key][i]['WBLeft']), v_rh))
            end_ro= rg.Point3d.Add(end, rg.Vector3d.Multiply(-1*float(design_strips[key][i]['WBRight']), v_rh))
            outline_pts = [st_lo, end_lo, end_ro, st_ro, st_lo]
            outline = rs.AddPolyline(outline_pts)
            rs.AddPlanarSrf(outline)
    rs.AddPolyline(point_list)
    




