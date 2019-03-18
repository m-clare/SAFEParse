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
	heading_data = {'OBJECT GEOMETRY - POINT COORDINATES': 'Point', 
				 	'OBJECT GEOMETRY - LINES 01 - GENERAL': 'Line',
				 	'OBJECT GEOMETRY - AREAS 01 - GENERAL': 'Area',
				 	'OBJECT GEOMETRY - DESIGN STRIPS': 'Strip'}
	data_dict = {}
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
					if heading in heading_data:
						line = fp.readline()
						while len(line.strip()) > 0:
							obj_id, attr_dict = parse_info(line, data_type=heading_data[heading])
							data_dict[heading][obj_id] = attr_dict
							line = fp.readline() # go to next line
			line = fp.readline()
	with open('output.json', 'w') as outfile:
		json.dump(data_dict, outfile)

if __name__ == '__main__':
	
	fp = './input/14_in_slab.f2k'
	create_slab_data(fp)

