import json

def parse_info(line, data_type=None):
	if data_type == None:
		raise NotImplementedError
	data = list(filter(None, line.split('   ')))
	data_field = data.pop(0)
	data_id = data_field.split("=")[-1]
	data_id = data_type + " " + data_id
	attr_dict = {}
	for attr in data:
		key, value = attr.split("=")[:]
		if '\n' in value:
			value = value.replace('\n','')
		attr_dict[key] = value
	return data_id, attr_dict


def create_slab_data(filepath):
	with open(filepath) as fp:
		line = fp.readline()
		cnt = 1
		while line:
			if "TABLE" in line:
				heading = line.split('"')[1::2]
				# store data per heading as separate dictionary
				if heading:
					heading = heading[0]
					data_dict[heading] = {}

					if heading == 'OBJECT GEOMETRY - POINT COORDINATES':
						line = fp.readline()
						while len(line.strip()) > 0:
							point_id, attr_dict = parse_info(line, data_type='Point')
							data_dict[heading][point_id] = attr_dict
							line = fp.readline() # go to next line
					if heading == 'OBJECT GEOMETRY - LINES 01 - GENERAL':
						line = fp.readline()
						while len(line.strip()) > 0:
							line_id, attr_dict = parse_info(line, data_type='Line')
							data_dict[heading][line_id] = attr_dict
							line = fp.readline() # go to next line
					if heading == 'OBJECT GEOMETRY - AREAS 01 - GENERAL':
						line = fp.readline()
						while len(line.strip()) > 0:
							area_id, attr_dict = parse_info(line, data_type='Area')
							data_dict[heading][area_id] = attr_dict
							line = fp.readline() # go to next line
					if heading == 'OBJECT GEOMETRY - DESIGN STRIPS':
						# Design strip info is a polyline with "width"
						line = fp.readline()
						while len(line.strip()) > 0:
							# detect strip polyline points
							strip_id, attr_dict = parse_info(line, data_type='Strip')
							if not strip_id in data_dict[heading]:
								data_dict[heading][strip_id] = []
							data_dict[heading][strip_id].append(attr_dict)
							line = fp.readline()
			line = fp.readline()

if __name__ == '__main__':
	
	with open('data.json', 'w') as outfile:
		json.dump(data_dict, outfile)

