from __future__ import division
"""

Simple k nearest neighbours implementation

- See http://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.KDTree.query.html#scipy.spatial.KDTree.query

Created on 29/01/2011

@author: peter
"""

import sys, math, pickle, misc, csv, kd_tree
import numpy as np
# Does not work
from scipy.spatial import KDTree
# Use our replacement
from kd_tree import KDTree

def get_knn(k, training_data_class, test_data, kd_tree):
    """ Naive implementation of k nearest neighbours
        k: number of nearest neighbours
        training_data_class: classes of each training training_data instance
        test_data: test_data to classify
        returns: classes of each input instance
    """
    num_inputs = np.shape(test_data)[0]
    if True:
        print 'k =', k
        print 'num_inputs =', num_inputs
        print 'training_data_class =', training_data_class[:20]
 
    closest = np.zeros(num_inputs)

    for n in range(num_inputs):
        retval = kd_tree.query(test_data[n,:], k=k)
        #print 'kd_tree.query returned', retval
        distances, indices = retval

        if k == 1:
            indices = np.array([indices])
            distances = np.array([distances])
       
        #print 'k =', k
        #print 'i =', test_data[n,:]
        #print 'd =', distances
        #print 'indices =', indices

        classes = training_data_class[indices[:k]]
        #print 'classes =', classes

        classes = np.unique(classes)
        #print 'unique classes =', classes
        if len(classes) == 1:
            closest[n] = np.unique(classes)
        else:
            #print 'x'*10
            counts = np.zeros(max(classes) + 1)
            for i in range(k):
                counts[training_data_class[indices[i]]] += 1
            #print 'counts =', counts
            closest[n] = np.argmax(counts)

    return closest

if False:
    def get_knn_probability(k, training_data, training_data_class, test_data):
        """ Use knn to compute probabilities of test_data belonging to training_data_class
            k: number of nearest neighbors
            training_data: training training_data instances
            training_data_class: classes of each training training_data instance
            test_data: test_data to classify
            returns: probabilities of each input instance belonging to each class
        """
        num_inputs = np.shape(test_data)[0]
        unique_classes = np.unique(training_data_class)
        unique_class_to_index = {}
        for i in range(len(unique_classes)):
            unique_class_to_index[unique_classes[i]] = i
        num_classes = len(unique_classes)
        if False:
            print 'num_inputs =', num_inputs
            print 'num_classes =', num_classes
            print 'training_data_class =', training_data_class
            print 'unique_classes =', unique_classes
            print 'unique_class_to_index =', unique_class_to_index
            exit()
            print 'training_data =', training_data
            
            print 'test_data =', test_data
        probabilites = np.zeros((num_inputs,num_classes),dtype = 'f')
        
        if USE_KD_TREE:
            print 'Training kd tree'
            kd_tree = KDTree(training_data)
            print 'Done training kd, tree'
    
        for n in range(num_inputs):
        
            if USE_KD_TREE:
                distances, indices = kd_tree.query(test_data[n,:], k=k)
            else:
                distances = np.sqrt(np.sum((training_data - test_data[n,:])**2, axis = 1))
                indices = np.argsort(distances, axis = 0)
    
            #print 'i =', test_data[n,:]
            #print 'd =', distances
            #print 'indices =', indices
    
            classes = training_data_class[indices[:k]]
            if False:
                print 'classes =', classes
               
            class_totals = np.zeros(num_classes)
            for i in range(classes.shape[0]):
                class_totals[unique_class_to_index[classes[i]]] += 1
            #print 'class_totals =', class_totals
            for i in range(class_totals.shape[0]):
                probabilites[n,i] = class_totals[i]/classes.shape[0]
            
        return unique_classes, probabilites

def rand(max_delta):
    """ Return a random number in range [-max_delta..max_delta] """
    return (np.random.random() - 0.5) * max_delta/0.5

def blend(a,b,r):
    """ Blend a and b with ratio r """
    return (r*a + b)/(1.0 + r)

def make_data(num_instances, num_classes, num_dimensions, max_delta):
    """ Make classification test training_data 
        num_instances: number of training samples
        num_classes: number of different classes for samples
        num_dimensions: number of attributes in training_data
        max_delta: each attribute of each training sample is in range 
                    [centroid-max_deta,centroid+max_delta]
        returns: training_data,training_data_class,test_data,test_data_class
            training_data: training samples
            training_data_class: classes of training samples
            test_data: test samples
            test_data_class: classes of test samples
    """
    verbose = False
    
    print 'make_data', num_instances, num_classes, num_dimensions
    instances_per_class = int(math.ceil(num_instances/num_classes))
    centroids = [[i+1] * num_dimensions for i in range(num_classes)]
    training_data_class = []
    training_data = []
    for i in range(num_instances):
        clazz = i//instances_per_class
        cent = centroids[clazz]
        val = [cent[j] + rand(max_delta) for j in range(num_dimensions)]
        training_data_class.append(clazz)
        training_data.append(val)
    test_data = sorted(centroids) 
    ratio = 4.0
    for k in range(1):
        #print len(test_data), test_data
        for i in range(1,len(test_data)):
            new_els = [[blend(test_data[i-1][j], test_data[i][j], ratio) for j in range(num_dimensions)],
                       [blend(test_data[i-1][j], test_data[i][j], 1.0/ratio) for j in range(num_dimensions)]]
            #print 'new_els = ', new_els
            test_data += new_els
        test_data.sort()
    if verbose:
        print 'centroids', centroids
        print 'test_data', len(test_data), test_data
        print 'training_data', training_data
        print 'training_data_class', training_data_class
    test_data_class = [np.argmin(np.array([abs(inp[0] - cent[0]) for cent in centroids])) for inp in test_data]
    if verbose:
        for i,inp in enumerate(test_data):
            print '%2d:'%i, [abs(inp[0] - cent[0]) for cent in centroids], test_data_class[i]
    test_data_class = [np.argmin(np.array([abs(inp[0] - cent[0]) for cent in centroids])) for inp in test_data]
    if verbose:
        print 'test_data_class', test_data_class
    #exit()
    return np.array(training_data), np.array(training_data_class), np.array(test_data), np.array(test_data_class)

def test_knn_on_sample(title, num_instances, num_classes, num_dimensions, max_delta):
    """ Test get_knn() by running it on some synthetic samples
        title: name of test
        num_instances: number of training samples
        num_classes: number of different classes for samples
        num_dimensions: number of attributes in training_data
        max_delta: each attribute of each training sample is in range 
                    [centroid-max_deta,centroid+max_delta]
        return: True iff all samples are classified correctly
    """
    print '#'*40
    training_data,training_data_class,test_data,test_data_class = make_data(num_instances, num_classes, num_dimensions, max_delta)
    print '='*40
    print 'num_instances, num_classes, num_dimensions, max_delta =', num_instances, num_classes, num_dimensions, max_delta
    for k in range(1, min(10,num_instances//num_classes)+1):
        print '-'*40 + ':', title, num_instances, num_classes, num_dimensions, max_delta 
        closest = get_knn(k, training_data, training_data_class, test_data)
        print 'k =', k
        print 'closest =', closest
        print 'test_data_class =', test_data_class
        matches = [closest[i] == test_data_class[i] for i in range(test_data_class.shape[0])]
        print 'matches =', matches
        if not all(matches):
            print 'mismatch!'
            return False
    
    return True

def test_knn_probability_on_sample(title, num_instances, num_classes, num_dimensions, max_delta):
    """ Test get_knn_probability() by running it on some synthetic samples
        title: name of test
        num_instances: number of training samples
        num_classes: number of different classes for samples
        num_dimensions: number of attributes in training_data
        max_delta: each attribute of each training sample is in range 
                    [centroid-max_deta,centroid+max_delta]
        return: True iff all samples are classified correctly
    """
    print '#'*40
    training_data,training_data_class,test_data,test_data_class = make_data(num_instances, num_classes, num_dimensions, max_delta)
    print '='*40
    print 'num_instances, num_classes, num_dimensions, max_delta =', num_instances, num_classes, num_dimensions, max_delta
    k = min(100, num_instances//4)
    
    print '-'*40 + ':', title, num_instances, num_classes, num_dimensions, max_delta 
    unique_classes, probabilities = get_knn_probability(k, training_data, training_data_class, test_data)
    print 'k =', k
    print 'unique_classes =', unique_classes
    print 'probabilities =', probabilities
    print 'test_data_class =', test_data_class
    for i in range(test_data_class.shape[0]):
        print test_data_class[i], np.argmax(probabilities[i]), probabilities[i]

    return True

def make_pickle_filename(name):
    return 'knn.%s.pkl' % name

def get_pickled_base(name):
    f = open(make_pickle_filename(name), 'rb')
    val = pickle.load(f)
    f.close()
    return val

def set_pickled(name, val):
    f = open(make_pickle_filename(name), 'wb')
    val = pickle.dump(val,f)
    f.close()

def get_pickled(name, default):
    try:
        val = get_pickled_base(name)
    except:
        set_pickled(name, default)
        val = get_pickled_base(name)
    return val

def test_knn():
    # Need to seed random number generator to give same result for each run
    np.random.seed(111)
    test_settings = [(4, 2, 50, 0.499),
                     (4, 2, 2, 0.1),
                     (35, 5, 3, 0.3),
                     ( 6, 2, 1, 0.1),
                     (35, 5, 1, 0.4),
                     (10055, 5, 17, 0.4),
                     #(10055, 15, 27, 0.49)
                     ]

    title = 'base test' 
    for num_instances, num_classes, num_dimensions, max_delta in test_settings:
        if not test_knn_on_sample(title, num_instances, num_classes, num_dimensions, max_delta):
            exit()
    
    test_number = 1
    # highest_max_delta convergeed to 0.324486403921 in previous testing
    highest_max_delta = get_pickled('highest_max_delta', 0.4999)           
    while True:
        title = 'test %02d' % test_number
        for num_instances, num_classes, num_dimensions, max_delta in test_settings:
            while True:
                if test_knn_on_sample(title,num_instances, num_classes, num_dimensions, highest_max_delta):
                    break
                highest_max_delta *= 0.99
                set_pickled('highest_max_delta', highest_max_delta)
        print '*** test:', test_number, ', highest_max_delta:', highest_max_delta 
        test_number += 1

def test_knn0():
    if False:
        training_data = np.array([[1,2,3],[3,1,2],[2,3,1],[4,5,6],[6,4,5],[5,6,4]])
        training_data_class = np.array([0,0,0,1,1,1])
        test_data = np.array([[2,2,2],[5,5,5],[3.4,3.5,3.6]])
         
    num_instances, num_classes, num_dimensions, max_delta = 35, 5, 3, 0.3
    num_instances, num_classes, num_dimensions, max_delta = 6, 2, 1, 0.1
    #num_instances, num_classes, num_dimensions, max_delta = 35, 5, 1, 0.3
    num_instances, num_classes, num_dimensions, max_delta = 35, 5, 1, 0.4
    #num_instances, num_classes, num_dimensions, max_delta = 10055, 5, 17, 0.4
    #num_instances, num_classes, num_dimensions, max_delta = 1090055, 15, 27, 0.49
    training_data,training_data_class,test_data,test_data_class = make_data(num_instances, num_classes, num_dimensions, max_delta)
   
    for k in range(1, min(10,num_instances//num_classes)+1):
        print '-'*20
        closest = get_knn(k, training_data, training_data_class, test_data)
        print 'k =', k
        print 'closest =', closest
        print 'test_data_class =', test_data_class
        matches = [closest[i] == test_data_class[i] for i in range(test_data_class.shape[0])]
        print 'matches =', matches
        if not all(matches):
            print 'mismatch!'
            exit()

def test_knn_probability0():
    # Need to seed random number generator to give same result for each run
    np.random.seed(112)
    title = 'test_knn_probability0'
    num_instances, num_classes, num_dimensions, max_delta = 35, 5, 3, 0.3
    num_instances, num_classes, num_dimensions, max_delta = 6, 2, 1, 0.1
    #num_instances, num_classes, num_dimensions, max_delta = 35, 5, 1, 0.3
    num_instances, num_classes, num_dimensions, max_delta = 35, 5, 1, 0.4
    num_instances, num_classes, num_dimensions, max_delta = 35, 7, 3, 0.3
    num_instances, num_classes, num_dimensions, max_delta = 10055, 5, 17, 4.8
    #num_instances, num_classes, num_dimensions, max_delta = 1090055, 15, 27, 0.49
    training_data,training_data_class,test_data,test_data_class = make_data(num_instances, num_classes, num_dimensions, max_delta)

    test_knn_probability_on_sample(title, num_instances, num_classes, num_dimensions, max_delta)

if __name__ == '__main__':
    if False:
        test_knn()
    if False:
        test_knn_probability0()
        
    if len(sys.argv) < 3:
        print 'usage:', sys.argv[0], '<training file name> <test file name>'
        exit()

    training_data_csv = sys.argv[1]
    test_data_csv = sys.argv[2]
    k = 4 
    print 'training_data_csv:', training_data_csv
    print 'test_data_csv:', test_data_csv
    print 'k:', k

    training_data_dict_str, _ = csv.readCsvAsDict(training_data_csv)
    training_data_dict = {}
    for k in training_data_dict_str.keys():
        training_data_dict[k] = [float(x) for x in training_data_dict_str[k]]
    print 'training keys:', training_data_dict.keys()
    training_data_class = training_data_dict['Grant.Status']
    training_data_keys = [k for k in sorted(training_data_dict.keys()) if k != 'Grant.Status']
    training_data = misc.transpose([training_data_dict[k] for k in training_data_keys])
    print 'training data:', len(training_data), len(training_data[0])

    test_data_dict_str, _ = csv.readCsvAsDict(test_data_csv)
    test_data_dict = {}
    for k in test_data_dict_str.keys():
        test_data_dict[k] = [float(x) for x in test_data_dict_str[k]]
    # Use training data column headers to ensure data matches
    test_data = misc.transpose([test_data_dict[k] for k in training_data_keys])
    print 'test data:', len(test_data), len(test_data[0])
    
    #kd_root = kd_tree.KDTree.construct_from_data(test_data)
    kd_root = kd_tree.KDTree(test_data)

    test_data_class = get_knn(3, np.array(training_data_class), np.array(test_data), kd_root)
    
    print 'test_data_class:', len(test_data_class), test_data_class[:100]
    