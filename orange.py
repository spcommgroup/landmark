print("Loading orange ..... "),
import Orange
print "DONE"
import os
from subprocess import call

data = Orange.data.Table("data/source/Conv07_choi_20130228_final.tab")
# tree = Orange.classification.tree.TreeLearner(data)

all_attributes = ["phone1-manner class", "phone2-type", "phone2-subnumber", 
                  "phone2-manner class", "outcome", "name", "phone1-subnumber",
                  "phone2-number", "phone2-stress", "phone1-stress",
                  "phone1-type", "phone1-number"]

def segmental_context():
    """This shows the distribution of LM preservations/deletions depending on 
     i) what the previous segment is, and 
     ii) what th following segment is. 
    This should already be included in the multi-factor .tab file, 
    so you can just put previous segment info in a .tab file and 
    run the program, then put following segment info in a .tab file 
    and run the program again."""

    for phone in ["phone1", "phone2"]:
        attributes_names = filter(lambda x: x.startswith(phone), all_attributes) + ["outcome"]
        save_path = os.path.join("results", "conv07 trees", phone)
        tree_file_name = phone + "-all.dot" #will also save a .png with the same name
        make_tree_from_attributes(attributes_names, save_path, tree_file_name)

def word_position():
    """This shows the distribution depending on where in the word this LM is: 
    the .tab info with the {o, n, c, a} info is what we need. 
    After running on this info, then combine the {n, a} data into 
    a {m} (=medial) category, and use this new .tab file to run the 
    program again."""

    attributes_names = filter(lambda x: x.endswith("type"), all_attributes) + ["outcome"]
    save_path = os.path.join("results", "conv07 trees", "word_position")
    tree_file_name = "word-position.dot" #will also save a .png with the same name
    make_tree_from_attributes(attributes_names, save_path, tree_file_name)
    
    # for entry in data:
    #     for attribute in entry:


# print tree.to_string()
# tree.dot(file_name=os.path.join("results","conv07 trees","full_tree.dot"), node_shape="ellipse", leaf_shape="box")

def make_tree_from_attributes(attributes_names, outpath, tree_file_name, data=data):
    attributes = filter(lambda x: x.name in attributes_names, data.domain.features)
    # for attribute_name in attributes_names:
    #     attributes.extend([x for x in data.domain.features if x.name == attribute_name])
    # outpath = os.path.join("results","conv07 trees",*attributes_names)
    call(["mkdir", "-p", outpath])
    # print("attributes =", [x.name for x in attributes])
    new_domain = Orange.data.Domain(attributes, data.domain.class_var)
    new_data = Orange.data.Table(new_domain, data)
    new_tree = Orange.classification.tree.TreeLearner(new_data)

    # file_name = os.path.join(outpath, list(data.domain)[feature_id].name+".dot")
    file_name = os.path.join(outpath, tree_file_name)
    new_tree.dot(file_name=file_name, node_shape="ellipse", leaf_shape="box")
    # print "Saved", file_name
    # os.system("dot -Tpng '"+file_name+"' -o '"+file_name[:-3]+"png'")
    call(["dot","-Tpng",file_name,"-o",file_name[:-3]+"png"])
    print "Saved", file_name[:-3]+"png"

# for feature_id in range(len(data.domain[:len(data.domain)-1])):
#     if not (data.domain[feature_id] in attributes):
#         new_domain = Orange.data.Domain(attributes + [list(data.domain)[feature_id]], data.domain.class_var)
#         new_data = Orange.data.Table(new_domain, data)
#         new_tree = Orange.classification.tree.TreeLearner(new_data)

#         # file_name = os.path.join(outpath, list(data.domain)[feature_id].name+".dot")
#         file_name = os.path.join(outpath, tree_file_name)
#         new_tree.dot(file_name=file_name, node_shape="ellipse", leaf_shape="box")
#         print "Saved", file_name
#         # os.system("dot -Tpng '"+file_name+"' -o '"+file_name[:-3]+"png'")
#         call(["dot","-Tpng",file_name,"-o",file_name[:-3]+"png"])
#         print "Saved", file_name[:-3]+"png"

segmental_context()