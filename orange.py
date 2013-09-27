print("Loading orange ..... "),
import Orange
print "DONE"
import os
from subprocess import call


# Data related to conv07
conv07_tab = "data/source/Conv07_choi_20130228_final.tab"
conv07_data = Orange.data.Table(conv07_tab)
# tree = Orange.classification.tree.TreeLearner(data)
all_attributes = ["phone1-manner class", "phone2-type", "phone2-subnumber", 
                  "phone2-manner class", "outcome", "name", "phone1-subnumber",
                  "phone2-number", "phone2-stress", "phone1-stress",
                  "phone1-type", "phone1-number"]

def readTab(file_name):
    """Reads a .tab file into a 2D array. Separates meta info from data."""
    data = []
    meta = []
    l=0
    for line in open(file_name):
        if l<3:
            meta.append(line.strip("\n").split("\t"))
        else:
            if len(line.strip("\n").split("\t")) == len(meta[0]):
                data.append(line.strip("\n").split("\t"))
        l += 1
    return (meta, data)

def saveTab((meta, data), file_name):
    output = ""
    meta.extend(data)
    for line in meta:
        output += "\t".join(line) + "\n"
    f = open(file_name, "w")
    f.write(output)
    f.close()
    return file_name

def combineMedialCategory(input_filename=conv07_tab):
    (meta,data) = readTab(input_filename)
    columns = [meta[0].index("phone2-type"), meta[0].index("phone1-type")]
    for line in data:
        for column in columns:
            if line[column] in "na":
                line[column] = "m"

    output_filename = input_filename[:-4]+"_combineMedialCategory.tab"
    saveTab((meta, data), output_filename)
    return output_filename;

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
        make_tree_from_attributes(save_path, tree_file_name, attributes_names, modified_data)

def word_position():
    """This shows the distribution depending on where in the word this LM is: 
    the .tab info with the {o, n, c, a} info is what we need. 
    After running on this info, then combine the {n, a} data into 
    a {m} (=medial) category, and use this new .tab file to run the 
    program again."""

    input_without_inserted = saveTab(readTab(conv07_tab), conv07_tab[:-4]+"_withoutInserted.tab")
    data_without_inserted = Orange.data.Table(input_without_inserted)

    attributes_names = filter(lambda x: x.endswith("type"), all_attributes) + ["outcome"]
    save_path = os.path.join("results", "conv07 trees", "word_position")
    tree_file_name = "word-position.dot" #will also save a .png with the same name

    make_tree_from_attributes(save_path, tree_file_name, attributes_names)

    modified_data = Orange.data.Table(combineMedialCategory(input_without_inserted))
    make_tree_from_attributes(save_path, "word-pos-with-m.dot", attributes_names, modified_data)

def make_tree_from_attributes(outpath, tree_file_name, attributes_names=None, data=conv07_data):
    if attributes_names != None: 
        attributes = filter(lambda x: x.name in attributes_names, data.domain.features)
        new_domain = Orange.data.Domain(attributes, data.domain.class_var)
        data = Orange.data.Table(new_domain, data)
    tree = Orange.classification.tree.TreeLearner(data)
    call(["mkdir", "-p", outpath])

    file_name = os.path.join(outpath, tree_file_name)
    tree.dot(file_name=file_name, node_shape="ellipse", leaf_shape="box")

    call(["dot","-Tpng",file_name,"-o",file_name[:-3]+"png"])
    print "Saved", file_name[:-3]+"png"

child_tab = "data/source/SLI3122_CNREP_choi.tab"
child_data = Orange.data.Table(child_tab)
child_outpath = os.path.join("results","child_trees")

make_tree_from_attributes(child_outpath, "full_tree.dot", None, child_data)