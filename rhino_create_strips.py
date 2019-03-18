import Rhino
import rhinoscriptsyntax as rs
import scriptcontext as sc
import json

def active_strip_filter(rhino_object, geometry, component_index):
    # only allow objects with a name starting with "active"
    if rhino_object.Attributes.Name.startswith("active"):
        return True
    return False
    
def max_point_index(strip_layers):
    return

def write_strip_data(layer, point_ind):
    # get all surfaces on layer
    strips = rs.ObjectsByLayer(layer)
    strip_ind = 1
    strip_dict = {}
    for strip in strips:
        # get only surfaces
        if rs.IsSurface(strip):
            if rs.IsSurfacePlanar(strip):
                strip_dict['Strip=' + layer + str(strip_ind)] = []
                strip_brep = rs.coercebrep(strip)
                edges = Rhino.Geometry.Brep.DuplicateEdgeCurves(strip_brep)
                edge_ids = []
                ind = 0
                for edge in edges:
                    edge_id = sc.doc.Objects.AddCurve(edge)
                    if edge_id:
                        rs.ObjectName(edge_id, 'active' + str(ind))
                        edge_ids.append(edge_id)
                        ind += 1
                # Get strip geometry
                # change color to help find strip
                rs.ObjectColor(strip, color=(255,0,255))
                start_edge = rs.GetObject('Select start edge.', 4, False, False, active_strip_filter)
                start_length = rs.CurveLength(start_edge)
                sp = rs.CurveMidPoint(start_edge)
                rs.ObjectName(rs.AddPoint(sp), name='SP_' + str(point_ind)) 
                end_edge = rs.GetObject('Select end edge.', 4, False, False, active_strip_filter)
                end_length = rs.CurveLength(end_edge)
                ep = rs.CurveMidPoint(end_edge)
                rs.ObjectName(rs.AddPoint(ep), name='SP_' + str(point_ind)) 
                # Clean up
                rs.DeleteObjects(edge_ids)
                rs.ObjectColor(strip, color=(128,0,128))
                # write to json
                start = {'Point': point_ind, 'GlobalX': round(sp.X, 4), 'GlobalY': round(sp.Y, 4),
                         'WALeft': round(start_length*0.5, 4), 'WARight': round(start_length*0.5, 4),
                         'Autowiden': 'No'}
                point_ind += 1
                end = {'Point': point_ind, 'GlobalX': round(ep.X, 4), 'GlobalY': round(ep.Y, 4),
                       'WBLeft': round(end_length*0.5, 4), 'WBRight': round(end_length*0.5, 4),
                       }
                strip_dict['Strip=' + layer + str(strip_ind)].append(start)
                strip_dict['Strip=' + layer + str(strip_ind)].append(end)
                point_ind += 1
                strip_ind += 1
    return strip_dict
    
if __name__ == "__main__":
    strip_layers = ['CSA', 'MSA', 'CSB', 'MSB']
    strip_layer = rs.GetString('Input name of strips to export.', strings=strip_layers)
    pt_ind = rs.GetInteger(message='Provide start integer for strip group', minimum=0)
    # set current layer to strip_layer
    rs.CurrentLayer(strip_layer)
    
    # Turn off other layers
    for layer in strip_layers:
        if layer != strip_layer:
            rs.LayerVisible(layer, visible=False, force_visible=True)
    # write strip data
    strip_dict = write_strip_data(strip_layer, pt_ind)
    
    with open(strip_layer + '.json', 'w') as outfile:
        json.dump(strip_dict, outfile)