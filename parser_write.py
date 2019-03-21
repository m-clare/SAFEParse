import json

with open('odata.json', 'r') as fh:
	data = json.load(fh)

start_field = ['Point', 'GlobalX', 'GlobalY', 'WALeft', 'WARight', 'Autowiden']
end_field = ['Point', 'GlobalX', 'GlobalY', 'WBLeft', 'WBRight']

file = open('output.txt', 'w')
for i in range(len(data.keys())):
	key = 'Strip CSA' + str(i + 1)
	strip = data[key]
	ostring0 = '   ' + key.replace(' ', '=')
	ostring1 = '   ' + key.replace(' ', '=')
	for field in start_field:
		ostring0 += '   ' + str(field) + '=' + str(strip[0][field])
	for field in end_field:
		ostring1 += '   ' + str(field) + '=' + str(strip[1][field])
	file.write(ostring0 + '\n')
	file.write(ostring1 + '\n')

file.close()

