
# coding: utf-8

# In[1]:

import random
import math
import numpy as np

from peer_review_util import *



# In[2]:

# assign students in groups to k submissions.
def peer_assignment(groups,k,coverList=[],debug=False):
    """Given no cover, first generate a cover with the first few submissions"""
    """Then, generate the rest of the assignments"""
    
    submissions = groups.keys()
    
    # lookup for which submissions to exclude from a particular student.
    exclude = invert_dictlist(groups)
    students = exclude.keys()
    studentList = list(students);

 
    # load = ceil(number of students * k / number of submissions)
    # this is how many copies of random submission lists we need.
    load = int(math.ceil((len(students) * k) / len(submissions)))
    
    # Repeat the submissions so that they each occur load times.
    repeatedSubmissions = [x for x in submissions for i in range(load-1)]
    
    # initialize empty assignment and cover
    assignments = {s : [] for s in students}
    cover = {s : [] for s in students}
    
    # cover with the first few submissions. Every time a submission is used, remove it.
    # This way, each submission is repeated at most load # of times.
    for s in students:
        for currentSubmission in repeatedSubmissions:
            if currentSubmission not in exclude[s]:
                assignments[s].append(currentSubmission);
                repeatedSubmissions.remove(currentSubmission);
                cover[s].append(currentSubmission);
                break;
    
    assignments = peer_assignment_with_cover(groups,k,cover,coverList);
    
    if (assignments == -1) and debug:
        print("Couldn't generate good cover!");
    
    done = True;
    for s in students:
        if (len(assignments[s]) != k):
            done = False;
            
    if not(done) and debug:
        print("Not a good assignment!")
        return -1;
    
    return assignments;
    
def peer_assignment_with_cover_submissions(groups,k,coverSubmissions,coverList=[],debug=False):
    """Given a list of submissions, generate a cover using those submissions"""
    """Then, generate the rest of the assignments"""
    
    submissions = groups.keys()
    
    # lookup for which submissions to exclude from a particular student.
    exclude = invert_dictlist(groups)
    students = exclude.keys()
    studentList = list(students);

    # load = ceil(number of students * k / number of submissions)
    # this is how many copies of random submission lists we need.
    load = int(math.ceil((len(students) * k) / len(submissions)))
    
    repeatedCoverSubmissions = [x for x in coverSubmissions for i in range(load-1)]
    
    # initialize empty cover
    cover = {s : [] for s in students}
    
    # cover with the first few of coverSubmissions
    for s in students:
        for currentSubmission in repeatedCoverSubmissions:
            if currentSubmission not in exclude[s]:
                repeatedCoverSubmissions.remove(currentSubmission);
                cover[s].append(currentSubmission);
                break;
    
    for s in students:
        if len(assignments[s]) == 0:
            if (debug):
                print("Error: Submissions cannot cover students!")
            return -1;
        
    assignments = peer_assignment_with_cover(groups,k,cover,coverList);
    
    if (assignments == -1) and debug:
        print("Couldn't generate good cover!");
        return -1;
    
     
    done = True;
    for s in students:
        if (len(assignments[s]) != k):
            done = False;
            
    if not(done) and debug:
        print("Not a good assignment!")
        return -1;
    
    return assignments;
    
def peer_assignment_with_cover(groups,k,cover,coverList = [],debug=False):
    """Given an entire cover of (student,submission) pairs, generate the rest of the assignments"""
    
    
    for i in range(10000):
        
        submissions = groups.keys()
        submissionsList = list(submissions);
        
        # lookup for which submissions to exclude from a particular student.
        exclude = invert_dictlist(groups)
        students = exclude.keys()
        studentList = list(students);
    
     
        # load = ceil(number of students * k / number of submissions)
        # this is how many copies of random submission lists we need.
        load = int(math.ceil((len(students) * k) / len(submissions)))
    
        # Repeat the submissions so that they each occur load times.
        extras = len(students)*k - len(submissions)*(load - 1);
        repeatedSubmissions = [x for x in submissions for i in range(load-1)]
        more = submissionsList[:extras]
        repeatedSubmissions = repeatedSubmissions + more
        
    
        # Assign cover, and remove covered submissions from submissions list
        assignments = cover;
        for s in students:
            for currentSubmission in assignments[s]:
                repeatedSubmissions.remove(currentSubmission);
        
        permutedSubmissions = random.sample(repeatedSubmissions,len(repeatedSubmissions));
        repeatedStudents = [x for x in studentList for i in range(k-1)]
        permutedStudents = random.sample(repeatedStudents,len(repeatedStudents));
    
        for s in permutedStudents:
            for currentSubmission in permutedSubmissions:
                assignments[s].append(currentSubmission);
                if not(check_assignment(groups,assignments)):
                    assignments[s].remove(currentSubmission);
                else:
                    permutedSubmissions.remove(currentSubmission);
                    break;
        
        done = True;
        
        for s in students:
            if (len(assignments[s]) != k):
                done = False;
        
        if done:
            break;
    
    done = True;
    for s in students:
        if (len(assignments[s]) != k):
            done = False;
    
    if not(done) and debug:
        print("Bad Cover!")
        return -1;
      
        
    coverList.append(cover);
    return assignments
    

# make sure nobody is assigned own assignment or duplicates
def check_assignment(groups,assignments):
    # maps students to their own submission
    
    exclude = invert_dictlist(groups)

    passed = True
    
    for s in assignments.keys():
        if exclude[s] in assignments[s]:
            #print("Student " + s + " assigned to own submission\n")
            passed = False
        if len(assignments[s]) != len(set(assignments[s])):
            #print("Student " + s + " assigned duplicate submissions\n")
            passed = False
            
    return passed


# generates random reviews for assignments 
#    (assignments as returned from peer_assignments())
#   qualities: {i => number of draws from distribituion}
def random_reviews(assignments, qualities = {}):
    # fill in qualities if empty.
    # default quality is 1.
    if len(qualities.keys()) < 1:
        qs = {i: 1 for i in assignments.keys()}
        qs.update(qualities)
        qualities = qs;
        
    # Uniform reviews
    #reviews = {i: {j: np.mean([random.random() for _ in range(qualities[i])]) for j in js} for (i, js) in assignments.items()} 
    
    # Binomial reviews
    reviews = {i : {j: np.random.binomial(qualities[i],0.5)/qualities[i] for j in js} for (i,js) in assignments.items()}
    
    return reviews
