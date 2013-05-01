import orange , orngTree,orngFSS

data = orange.ExampleTable('C:\Users\mzhan\Documents\UROP2012\conv07_113.tab')
##data = orange.ExampleTable('C:\Users\mzhan\Documents\UROP2012\conv07_121029.tab')

dist = orange.DomainDistributions(data)
##print "Average values and mean square errors:"
##for i in range(len(data.domain.attributes)):
##    if data.domain.attributes[i].varType == orange.VarTypes.Continuous:
##        print "%s, mean=%5.2f +- %5.2f" % \
##            (data.domain.attributes[i].name, dist[i].average(), dist[i].error())
##
##print "\nFrequencies for values of discrete attributes:"
##for i in range(len(data.domain.attributes)):
##    a = data.domain.attributes[i]
##    if a.varType == orange.VarTypes.Discrete:
##        print "%s:" % a.name
##        for j in range(len(a.values)):
##            print "  %s: %d" % (a.values[j], int(dist[i][j]))
##
##print "\nNumber of items where attribute is not defined:"
##for i in range(len(data.domain.attributes)):
##    a = data.domain.attributes[i]
##    print "  %2d %s" % (dist[i].unknowns, a.name)

##tree = orngTree.TreeLearner(data, sameMajorityPruning=1, mForPruning=2)
##print "Possible classes:", data.domain.classVar.values
##for i in range(5):
##    p = tree(data[i], orange.GetProbabilities)
##    print "%d: %5.3f (originally %s)" % (i+1, p[1], data[i].getclass())
##
##orngTree.printTxt(tree)

"""
def report_relevance(data):
  m = orngFSS.attMeasure(data)
  for i in m:
    print "%5.3f %s" % (i[1], i[0])

print "Before feature subset selection (%d attributes):" % \
  len(data.domain.attributes)
report_relevance(data)
data = orange.ExampleTable('C:\Users\mzhan\Documents\UROP2012\conv07_113.tab')

marg = 0.001
filter = orngFSS.FilterRelief(margin=marg)
ndata = filter(data)
print "\nAfter feature subset selection with margin %5.3f (%d attributes):" % \
  (marg, len(ndata.domain.attributes))

report_relevance(ndata)

tree = orngTree.TreeLearner(data, sameMajorityPruning=1, mForPruning=2)
print "Possible classes:", data.domain.classVar.values
for i in range(15):
    p = tree(data[i], orange.GetProbabilities)
    p1, p2, p3 = p
    print "%d: %5.3f %5.3f %5.3f (originally %s)" % (i+1, p1, p2, p3, data[i].getclass())

##orngTree.printTxt(tree)
"""
# setting up the classifiers
majority = orange.MajorityLearner(data)
bayes = orange.BayesLearner(data)
tree = orngTree.TreeLearner(data, sameMajorityPruning=1, mForPruning=2)
knn = orange.kNNLearner(data, k=21)

##majority.name="Majority"; bayes.name="Naive Bayes";
##tree.name="Tree"; knn.name="kNN"
##
##classifiers = [majority, bayes, tree, knn]
##
### print the head
##print "Possible classes:", data.domain.classVar.values
##print "Original Class",
##for l in classifiers:
##    print "%-13s" % (l.name),
##print
##
### classify first 10 instances and print probabilities
##for example in data[:10]:
##    print "(%-10s)  " % (example.getclass()),
##    for c in classifiers:
##        p = apply(c, [example, orange.GetProbabilities])
##        print "%5.3f %5.3f %5.3f      " % (p[0], p[1], p[2]),
##    print
