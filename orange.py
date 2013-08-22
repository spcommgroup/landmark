print("Loading orange ..... "),
import Orange
print "DONE"
import os
from subprocess import call

data = Orange.data.Table("data/source/Conv07_choi_20130228_final.tab")

# print "Attributes:", ", ".join(x.name for x in data.domain.features)
# print "Class:", data.domain.class_var.name
# print "Data instances", len(data)

tree = Orange.classification.tree.TreeLearner(data)
# print tree.to_string()
tree.dot(file_name=os.path.join("results","conv07 trees","full_tree.dot"), node_shape="ellipse", leaf_shape="box")

attributes_names = ["phone2-manner class",]
attributes = []
for attribute_name in attributes_names:
	attributes.extend([x for x in data.domain.features if x.name == attribute_name])
outpath = os.path.join("results","conv07 trees",*attributes_names)
call(["mkdir", "-p", outpath])
print("attributes =", [x.name for x in attributes])

for feature_id in range(len(data.domain[:len(data.domain)-1])):
	if not (data.domain[feature_id] in attributes):
		new_domain = Orange.data.Domain(attributes + [list(data.domain)[feature_id]], data.domain.class_var)
		new_data = Orange.data.Table(new_domain, data)
		new_tree = Orange.classification.tree.TreeLearner(new_data)

		file_name = os.path.join(outpath, list(data.domain)[feature_id].name+".dot")
		new_tree.dot(file_name=file_name, node_shape="ellipse", leaf_shape="box")
		# os.system("dot -Tpng '"+file_name+"' -o '"+file_name[:-3]+"png'")
		call(["dot","-Tpng",file_name,"-o",file_name[:-3]+"png"])