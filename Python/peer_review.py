import random
import math


# average elements in list
def avg(lst):
    return sum(lst) / len(lst) if len(lst) > 0 else 0


# invert a dictionary of lists (assuming no duplicates)
def invert_dictlist(d):
    return dict((v, k) for k in d for v in d[k])


# invert a dictionary of lists (with duplicates)
def invert_dictlist_dup(d):
    values = set(a for b in d.values() for a in b)
    reverse_d = dict((new_key, [key for key, value in d.items() if new_key in value]) for new_key in values)
    return reverse_d


# wrapper for backwards compatibility
def peer_assignment(groups, k, debug=False):
    return peer_assignment_return_cover(groups, k, debug)[0]


# assign students in groups to k submissions, and return the assignments and the generated cover
def peer_assignment_return_cover(groups, k, debug=False):
    """Given no cover, first generate a cover with the first few submissions"""
    """Then, generate the rest of the assignments"""
    for i in range(1000):
        submissions = groups.keys()

        # lookup for which submissions to exclude from a particular student.
        exclude = invert_dictlist(groups)
        students = exclude.keys()
        studentList = list(students);

        # load = ceil(number of students * k / number of submissions)
        # this is how many copies of random submission lists we need.
        load = int(math.ceil((len(students) * k) / len(submissions)))

        # Repeat the submissions so that they each occur load times.
        repeatedSubmissions = [x for x in submissions for i in range(load)]

        # initialize empty assignment and cover
        assignments = {s: [] for s in students}
        cover = {s: [] for s in students}

        # cover with the first few submissions. Every time a submission is used, remove it.
        # This way, each submission is repeated at most load # of times.
        for s in students:
            for currentSubmission in repeatedSubmissions:
                if currentSubmission not in exclude[s]:
                    assignments[s].append(currentSubmission);
                    repeatedSubmissions.remove(currentSubmission);
                    cover[s].append(currentSubmission);
                    break;

        assignments = peer_assignment_with_cover(groups, k, cover);

        if (assignments != -1):
            break;

    if (assignments == -1) and debug:
        print("Couldn't generate good cover!");

    return assignments, invert_dictlist_dup(cover)


def peer_assignment_with_cover_submissions(groups, k, coverSubmissions, debug=False):
    """Given a list of submissions, generate a cover using those submissions"""
    """Then, generate the rest of the assignments"""

    for i in range(1000):
        submissions = groups.keys()

        # lookup for which submissions to exclude from a particular student.
        exclude = invert_dictlist(groups)
        students = exclude.keys()
        studentList = list(students);

        # load = ceil(number of students * k / number of submissions)
        # this is how many copies of random submission lists we need.
        load = int(math.ceil((len(students) * k) / len(submissions)))

        repeatedCoverSubmissions = [x for x in coverSubmissions for i in range(load)]

        # initialize empty cover
        cover = {s: [] for s in students}

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

        assignments = peer_assignment_with_cover(groups, k, cover);
        if (assignments == -1):
            break;

    if (assignments == -1) and debug:
        print("Couldn't generate good cover!");

    return assignments;


def peer_assignment_with_cover(groups, k, cover, debug=False):
    """Given an entire cover of (student,submission) pairs, generate the rest of the assignments"""

    for i in range(1000):

        submissions = groups.keys()

        # lookup for which submissions to exclude from a particular student.
        exclude = invert_dictlist(groups)
        students = exclude.keys()
        studentList = list(students);

        # load = ceil(number of students * k / number of submissions)
        # this is how many copies of random submission lists we need.
        load = int(math.ceil((len(students) * k) / len(submissions)))

        # Repeat the submissions so that they each occur load times.
        repeatedSubmissions = [x for x in submissions for i in range(load)]

        # Assign cover, and remove covered submissions from submissions list
        assignments = cover;
        for s in students:
            for currentSubmission in assignments[s]:
                repeatedSubmissions.remove(currentSubmission);

        permutedSubmissions = random.sample(repeatedSubmissions, len(repeatedSubmissions));
        repeatedStudents = [x for x in studentList for i in range(k - 1)]
        permutedStudents = random.sample(repeatedStudents, len(repeatedStudents));

        for s in permutedStudents:
            for currentSubmission in permutedSubmissions:
                assignments[s].append(currentSubmission);
                if not (check_assignment(groups, assignments)):
                    assignments[s].remove(currentSubmission);
                else:
                    permutedSubmissions.remove(currentSubmission);
                    break;

        done = True;
        for s in students:
            if (len(assignments[s]) < k):
                done = False;
        if done:
            break;

    done = True;
    for s in students:
        if (len(assignments[s]) < k):
            done = False;
    if not (done) and debug:
        print("Bad Cover!")
        return -1;

    # print the cover
    # here one can also output to file, etc.
    # print("Cover: ");
    # print(invert_dictlist_dup(cover));

    return assignments


# make sure nobody is assigned own assignment or duplicates
def check_assignment(groups, assignments):
    # maps students to their own submission

    exclude = invert_dictlist(groups)

    passed = True

    for s in assignments.keys():
        if exclude[s] in assignments[s]:
            # print("Student " + s + " assigned to own submission\n")
            passed = False
        if len(assignments[s]) != len(set(assignments[s])):
            # print("Student " + s + " assigned duplicate submissions\n")
            passed = False

    return passed


# generates random reviews for assignments 
#    (assignments as returned from peer_assignments())
#   qualities: {i => number of draws from distribituion}
def random_reviews(assignments, qualities = {}):
    # fill in qualities if empty.
    # default quality is 1.
    qs = {i:1 for i in assignments.keys()}
    qs.update(qualities)
    
    return {i: {j: avg([random.random() for _ in range(qs[i])]) for j in js} for (i, js) in assignments.items()} 


MIN_VARIANCE = 0.001  # don't let 1/variance blow up if a peer is very accurate.
DEFAULT_VARIANCE = 1.0  # this does not matter as long as it is the same.


# assign students in groups to k submissions.
#    reviews:     {'peer name' => {'submission name' => score} 
#    truth:       {'submission name'=> score}
#    t:           number of iterations after which to quit.
# returns:
#    (scores,qualities): ({submission=>(score,var)},{peer=>var})
def simple_vancouver(reviews, truth, t):
    # i: peers; j: submissions

    # strip scores 
    #   iassign[i] = submissions assigned to peer i
    #   jassign[j] = peers assigned to review submission j
    iassign = {i: review.keys() for (i, review) in reviews.items()}
    jassign = invert_dictlist_dup(iassign)

    peers = iassign.keys()
    submissions = jassign.keys()

    # ivar[i] and jvar[j] are 1/variance
    jvar = {j: 1 / DEFAULT_VARIANCE for j in submissions}
    jmean = {j: 0.0 for j in submissions}
    ivar = {i: 1 / DEFAULT_VARIANCE for i in peers}

    for _ in range(t):
        # update score ivariances: jvar[j] = sum_i ivar[i]
        #    notes: ignores old ivar
        jvar = {j: sum([ivar[i] for i in jassign[j]]) for j in submissions}

        # update score mean: jmean[j] = (sum_i reviews[i,j] ivar[i]) / jvar[j]] 
        jmean = {j: sum([reviews[i][j] * ivar[i] for i in jassign[j]]) / jvar[j] for j in submissions}

        # reset the truth.
        jmean.update(truth)

        # update qualities: ivar[i] = (sum_j jvar[j]) / (sum_j jvar[j](reviews[i][j]-jmean[j]))
        ivar = {i: min(1 / MIN_VARIANCE,
                       sum([jvar[j] for j in iassign[i]]) / \
                       sum([jvar[j] * (reviews[i][j] - jmean[j]) ** 2 for j in iassign[i]])) \
                for i in peers}

    scores = {j: (jmean[j], 1.0 / jvar[j]) for j in submissions}
    quality = {i: 1.0 / ivar[i] for i in peers}

    return (scores, quality)


# assign students in groups to k submissions.
#    reviews:     {'peer name' => {'submission name' => score} 
#    truth:       {'submission name'=> score}
#    t:           number of iterations after which to quit.
# returns:
#    (scores,qualities): ({submission=>(score,var)},{peer=>var})
# PRECONDITIONS:
#    - peers assigned to at least two submissions.
#    - submissions assigned to at least two peers.
# NOTES:
#    - runs exactly t iterations.  does not stop if no improvements.
def vancouver(reviews, truth, t):
    # i: peers; j: submissions

    # strip scores 
    #   iassign[i] = submissions assigned to peer i
    #   jassign[j] = peers assigned to review submission j
    iassign = {i: review.keys() for (i, review) in reviews.items()}
    jassign = invert_dictlist_dup(iassign)

    # make sure preconditions are met
    kmin = min(len(subs) for (i, subs) in iassign.items())
    assert kmin >= 2, "Vancouver needs at least two submissions per peer!"
    lmin = min(len(peers) for (j, peers) in jassign.items())
    assert lmin >= 2, "Vancouver needs at least two peers per submission!"

    peers = iassign.keys()
    submissions = jassign.keys()

    # maintain ivar, jvar, jmean for each edge in assignment
    # ivar and jvar are 1/variance!
    ivars = {i: {j: 1 / DEFAULT_VARIANCE for j in iassign[i]} for i in peers}
    jvars = {i: {j: 1 / DEFAULT_VARIANCE for j in iassign[i]} for i in peers}
    # jmean = {i: {j: avg([reviews[ii][j] for ii in jassign[j] if ii != i]) for j in iassign[i]} for i in peers}
    jmeans = {i: {j: 1.0 for j in iassign[i]} for i in peers}

    for _ in range(t):
        # update score inverse variances for submissions
        jvars = {i: {j: sum([ivars[ii][j] for ii in jassign[j] if ii != i]) for j in iassign[i]} for i in peers}

        # update score mean: jmean[j] = (sum_i reviews[i,j] ivar[i]) / jvar[j]] 
        jmeans = {i: {j: truth[j] if j in truth \
            else sum([reviews[ii][j] * ivars[ii][j] for ii in jassign[j] if ii != i]) / jvars[i][j] \
                      for j in iassign[i]} \
                  for i in peers}

        # update qualities: ivar[i] = (sum_j jvar[j]) / (sum_j jvar[j](reviews[i][j]-jmean[j]))
        ivars = {i: {j: min(1 / MIN_VARIANCE,
                            sum([jvars[i][jj] for jj in iassign[i] if jj != j]) / \
                            sum([jvars[i][jj] * (reviews[i][jj] - jmeans[i][jj]) ** 2 for jj in iassign[i] if jj != j])) \
                     for j in iassign[i]}
                 for i in peers}

    # update score ivariances: jvar[j] = sum_i ivar[i]
    #    notes: ignores old ivar
    jvar = {j: sum([ivars[i][j] for i in jassign[j]]) for j in submissions}

    # update score mean: jmean[j] = (sum_i reviews[i,j] ivar[i]) / jvar[j]] 
    jmean = {j: sum([reviews[i][j] * ivars[i][j] for i in jassign[j]]) / jvar[j] for j in submissions}

    # reset the truth.
    jmean.update(truth)

    # update qualities: ivar[i] = (sum_j jvar[j]) / (sum_j jvar[j](reviews[i][j]-jmean[j]))
    ivar = {i: min(1 / MIN_VARIANCE,
                   sum([jvars[i][j] for j in iassign[i]]) / \
                   sum([jvars[i][j] * (reviews[i][j] - jmeans[i][j]) ** 2 for j in iassign[i]])) \
            for i in peers}

    scores = {j: (jmean[j], 1.0 / jvar[j]) for j in submissions}
    quality = {i: 1.0 / ivar[i] for i in peers}

    return (scores, quality)
