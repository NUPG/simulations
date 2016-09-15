import math 
import random

#note this will only work on hashable objects
def duplicates(tocheck):
  return len(tocheck) != len(set(tocheck))

####
# GENERATE PEER ASSIGNMENT
# Input:
#    - peers: [peer ids]
#    - submissions: [submission ids].
#    - k: number of submissions to assign each peer.
#    - cover: [submission ids] (PASS BY REFERENCE)
#    - excludes: {peer id : [excluded submission ids]}
#    - num_tries: attempts a random matching this many times
#         (fails and returns {} if num_tries is exceeded)
# Output:
#    - assignments: {peer id : [submission_ids]} 
#
# Notes:
#    - if 'cover' is [], then it will replace with a random cover.
#      (pass by reference)
def peer_assignment_covered(peers,submissions,k,cover=[],excludes={},num_tries=1000):
    
    m = len(submissions)
    n = len(peers)

    excludes = {p : (excludes[p] if p in excludes else []) for p in peers}
    
    # load = ceil(n * k / m)
    # this is how many copies of random submission lists we need.
    load = int(math.ceil((n * k) / m))

    # extend cover to be the right length 
    # by adding random elements from 'submissions \ cover'
    cover_len = math.ceil(n/load)
    if len(cover) < cover_len:
        # get random elements from 'submissions \ cover'
        gen_cover = random.sample(set(submissions).difference(set(cover)),int(math.ceil(n/load)))
        # add to cover.
        cover.extend(gen_cover) 


    # assign the agents to the cover. 
    cover_assignments = peer_assignment(peers,submissions,1,excludes,num_tries)
    if not cover_assignments:
        return {}

    # add cover_assignment to excludes.
    excludes = {p: excludes[p] + cover_assignments[p] for p in peers}

    # the remaining submissions
    residual_submissions = set(submissions).difference(set(cover))

    residual_assignments = peer_assignment(peers,submissions,1,excludes,num_tries)
    if not residual_assignments:
        return {}
    
    # combine cover and residual assignment
    assignments = {p: cover_assignments[p] + residual_assignments[p] for p in peers}

    return assignments
    
####
# GENERATE PEER ASSIGNMENT
# Input:
#    - peers: [peer ids]
#    - submissions: [submission ids].
#    - k: number of submissions to assign each peer.
#    - excludes: {peer id : [excluded submission ids]}
#    - num_tries: attempts a random matching this many times
#         (fails and returns {} if num_tries is exceeded)
# Output:
#    - assignments: {peer id : [submission_ids]} 
def peer_assignment(peers,submissions,k,excludes={},num_tries=1000):
    n = len(peers)
    m = len(submissions)

    excludes = {p : (excludes[p] if p in excludes else []) for p in peers}

    # load = ceil(n * k / m)
    # number of peers per submission (rounded up).
    load = int(math.ceil((n * k) / m))

    peer_reps = peers * k
    submission_reps = submissions * load

    count = 0
    # try to get a matching with out duplicates or excluded assignments.
    for _ in range(num_tries):

        count += 1
        
        random.shuffle(submission_reps)

        # trim the imbalance between peer_reps and submission_reps
        # and make sure there no duplicates in residual.
        while len(peer_reps) < len(submission_reps):
        # check for duplicated in residual
            residual = submission_reps[len(peer_reps):]
            if (duplicates(residual)):
                random.shuffle(submission_reps)
            else:
                submission_reps = submission_reps[:len(peer_reps)]

        assignments = {p:[] for p in peers}

        for (p,s) in zip(peer_reps,submission_reps):
            assignments[p].append(s)

        # check for duplicates or excludesd assignemnts
        if any(duplicates(assignments[p] + excludes[p]) for p in peers):
            continue


        print "finished with " + str(count) + " tries."
        return assignments
 
    # we failed to find an assignment given the in num_tries tries.
    return {}

####
# CHECK TO SEE IF A PEER ASSIGNMENT IS VALID
#    - peers are not assigned to review the same submission multiple times.
#    - peers are not assigned to review any submissions in their excludes list.
def peer_assignment_check(peers,assignments,excludes):
    excludes = {p : (excludes[p] if p in excludes else []) for p in peers}

    return not any(duplicates(assignments[p] + excludes[p]) for p in peers)



