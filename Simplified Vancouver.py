"""
Simplified Vancouver Algorithm

Author: Donald "Drew" Bronson
Creation Date:  12 May 2016

This algorithm was developed by Jason Hartline, Samuel Taggart, and Doug Downey at Northwestern University as part of
a research project in the field of peer grading algorithms. It represents a simplified version of the Vancouver
algorithm and is hypothesized by the above to output comparable results.
"""
import csv

import numpy as np

'''
This global variable represents the maximum score for each assignment (or rather, each pseudo-assignment).
It is used internally for sanity checking, to make sure Vancouver never estimates a grade for an assignment
that is higher than the maximum possible grade for that assignment. I have assumed for the sake of simplicity that all
categories on the rubric will be worth an equal number of points.
'''
MAX_GRADE = 2

'''
These global variables are used for initialization of Vancouver. They are included here for convenience of modification.
'''
DEFAULT_GRADER_VARIANCE = 1.0
DEFAULT_SUBMISSION_GRADE = 1.0
DEFAULT_SUBMISSION_VARIANCE = 1.0

'''
This global array is a placeholder for the eventual data, which should be declared as a global numpy array.
grades[i, j] represents the grade assigned by grader i to submission j, and should be NOT_GRADED_VALUE if no such
grade exists.

grades_path is the path to the csv file containing the grades. The required format for each line of the csv is:
grader_id, submission_id, score
'''
grades = np.array([[-1]])
grades_path = "Peer Review Data Sheet - Truncated.csv"
NOT_GRADED_VALUE = -1

'''
This global array is a placeholder for insertion of TA grades. They should be inserted in the same order as the grades,
with -1 flagging that there is no TA grade for this assignment. USE_GROUND_TRUTH toggles whether this data is
included. DEFAULT_GROUND_TRUTH_VALUE is a flag value which indicates that ground truth has not been set for a given
submission, either because it was not graded by a TA or because USE_GROUND_TRUTH was set to false. If USE_GROUND_TRUTH
is set to false, all ground_truth values for submissions will be set to DEFAULT_GROUND_TRUTH_VALUE; the program relies
on this internally.
'''
truths_path = "Processed_TA_groundtruth.csv"
USE_GROUND_TRUTH = False
DEFAULT_GROUND_TRUTH_VALUE = -1
ground_truths = []

'''
These two global arrays are both working variables for Vancouver and the method by which it outputs results.
Once Vancouver has finished running, the data in them should be accurate.
'''
graders = []
submissions = []

'''
These two dictionaries map the submission and grader ID numbers to the indices used internally by the program
for the grades and ground_truths arrays. They should be consulted to convert between these two representations.
The mapping is one-to-one, and there is a function below called backtrace which takes the index and returns
the grader or submission ID.
'''
grader_dict = {}
submission_dict = {}

EPSILON = 0.1


def parse_data():
    """
    Initializes working variables for the Vancouver algorithm by reading in data from the grades array and the
    ground_truths array.
    """
    for i in range(grades.shape[0]):
        graders.append(Grader(i))
    for j in range(grades.shape[1]):
        submissions.append(Submission(j))
    for i in range(grades.shape[0]):
        for j in range(grades.shape[1]):
            if grades[i, j] != -1:
                graders[i].submission_indices.append(j)
                submissions[j].grader_indices.append(i)
    if USE_GROUND_TRUTH:
        for i in range(len(submissions)):
            submissions[i].ground_truth = ground_truths[i]


def parse_truth():
    """
    This function reads in the ground_truths array from a CSV of the format:
    submission_id, grade
    :return:
    """
    with open(truths_path, newline='') as csv_file:
        global ground_truths
        global submissions
        while len(ground_truths) < grades.shape[1]:
            ground_truths.append(DEFAULT_GROUND_TRUTH_VALUE)
        truths_reader = csv.reader(csv_file, delimiter=',', quotechar='"')
        for row in truths_reader:
            submission_id = row[0]
            submission_index = submission_dict[submission_id]
            submission_grade = float(row[1])
            ground_truths[submission_index] = submission_grade


def parse_peer_grades():
    """
    This function reads in the grades array from a CSV of the format:
    grader_id, submission_id, grade
    """
    with open(grades_path, newline='') as csv_file:
        global grades
        grade_reader = csv.reader(csv_file, delimiter=',', quotechar='"')
        i = 1
        j = 1
        for row in grade_reader:
            grader = row[0]
            submission = row[1]
            score = row[2]
            if grader not in grader_dict:
                grader_dict[grader] = i - 1
                i += 1
                grader_row = np.zeros(j)
                for k in range(len(grader_row)):
                    grader_row[k] = NOT_GRADED_VALUE
                grades = np.append(grades, [grader_row], axis=0)
            if submission not in submission_dict:
                submission_dict[submission] = j - 1
                j += 1
                submission_row = np.zeros(i)
                for k in range(len(submission_row)):
                    submission_row[k] = NOT_GRADED_VALUE
                grades = np.append(grades, np.rot90([submission_row]), axis=1)
            grades[grader_dict[grader] + 1][submission_dict[submission] + 1] = float(score)
    grades = grades[1:, 1:]


class Submission:
    def __init__(self, index: int, grade: float = DEFAULT_SUBMISSION_GRADE,
                 variance: float = DEFAULT_SUBMISSION_VARIANCE,
                 ground_truth: float = DEFAULT_GROUND_TRUTH_VALUE):
        """
        Create a new submission.
        :type grade: float
        :type variance: float
        :type ground_truth: float
        """
        self.ground_truth = ground_truth

        self.grade = None
        self.set_grade(grade)

        self.variance = None
        self.set_variance(variance)

        self.grader_indices = []

        self.index = index

    def __str__(self):
        sub_id = backtrace(submission_dict, self.index)
        return "Submission: " + sub_id + "\n" + "Grade: " + str(self.grade) + \
               "\n" + "Variance: " + str(self.variance) + "\n" + "Ground Truth: " + str(self.ground_truth) + "\n"

    def set_grade(self, grade: float):
        """
        A wrapper for setting the grade of a submission, designed to catch incorrect values.
        :type grade: float
        """
        assert isinstance(grade, float), "Grade must be a float."
        assert grade <= MAX_GRADE, "Cannot set submission grade to more than the maximum possible points."
        assert grade >= 0, "Cannot set submission grade to less than zero."
        self.grade = grade

        '''
        This check ensures that no matter where the grade is set, it will be reverted immediately to ground truth,
        ensuring that the ground truth value is the only one which will ever appear outside of this function. The
        ground truth value is always initialized to DEFAULT_GROUND_TRUTH_VALUE even if USE_GROUND_TRUTH is false, so
        if it is still equivalent to that, it has never been set and should not be used.
        '''
        #if self.ground_truth != DEFAULT_GROUND_TRUTH_VALUE:
            #self.grade = self.ground_truth

    def set_variance(self, variance: float):
        """
        A wrapper for setting the variance of a submission, designed to catch incorrect values.
        :type variance: float
        """
        assert isinstance(variance, float), "Variance must be a float."
        assert variance >= 0
        self.variance = variance


class Grader:
    def __init__(self, index: int, variance: float = DEFAULT_GRADER_VARIANCE):
        """
        Create a new grader.
        :type variance: float
        """
        self.variance = None
        self.set_variance(variance)
        self.submission_indices = []
        self.index = index

    def set_variance(self, variance: float = 1):
        """
        A wrapper for setting the variance of a grader, designed to catch incorrect values.
        :type variance: float
        """
        assert isinstance(variance, float), "Variance must be a float."
        assert variance >= 0
        self.variance = variance


def invert(k: float):
    if k == 0:
        return 1.0 / (k + 0.01)
    else:
        return 1.0 / k

def update_submission_variance_estimates():
    for j in range(len(submissions)):
        variance = 0
        for i in submissions[j].grader_indices:
            variance += invert(graders[i].variance)
        variance = invert(variance)
        submissions[j].set_variance(variance)
    return True


def update_grade_estimates():
    for j in range(len(submissions)):
        grade = 0
        for i in submissions[j].grader_indices:
            grade += (grades[i, j] * invert(graders[i].variance))
        grade *= submissions[j].variance
        submissions[j].set_grade(grade)
    return True


def update_user_variance_estimates():
    for i in range(len(graders)):
        part_a = 0
        for j in graders[i].submission_indices:
            part_a += invert(submissions[j].variance)
        part_a = invert(part_a)
        part_b = 0
        for j in graders[i].submission_indices:
            part1 = invert(submissions[j].variance)
            part2 = (grades[i, j] - submissions[j].grade) ** 2
            part_b += (part1 * part2)
        graders[i].set_variance(part_a * part_b)
    return True


'''
def update_submission_variance():
    """
    Helper function for Vancouver which updates estimates of submission variances.
    :return: a boolean indicating whether there has been an update
    """
    updated = False
    for j in range(len(submissions)):
        variance = 0.0
        for i in submissions[j].grader_indices:
            variance += invert(graders[i].variance)
        variance = invert(variance)
        if abs(variance - submissions[j].variance) > EPSILON:
            updated = True
        submissions[j].set_variance(variance)
    return updated


def update_grade_estimates():
    """
    Helper function for Vancouver which updates estimates of submission grades.
    :return: a boolean indicating whether there has been an update
    """
    updated = False
    for j in range(len(submissions)):
        assert isinstance(submissions[j], Submission)
        grade = 0
        for i in submissions[j].grader_indices:
            assert isinstance(graders[i], Grader)
            grade += invert(graders[i].variance) * grades[i, j]
        grade *= submissions[j].variance
        if abs(grade - submissions[j].grade) > EPSILON:
            updated = True
        submissions[j].set_grade(grade)
    return updated


def update_grader_variance():
    """
    Helper function for Vancouver which updates estimates of grader variances.
    :return: a boolean indicating whether there has been an update
    """
    updated = False
    for i in range(len(graders)):
        sum1 = 0
        sum2 = 0
        for j in graders[i].submission_indices:
            sum1 += invert(submissions[j].variance)
            sum2 += invert(submissions[j].variance) * (grades[i, j] - submissions[j].grade) ** 2
        sum1 = invert(sum1)
        variance = sum1 * sum2
        if abs(variance - graders[i].variance) > EPSILON:
            updated = True
        graders[i].set_variance(variance)
    return updated
'''

def backtrace(d: dict, value: int):
    """
    Runs backwards through the dictionary, searching for the key which maps to the input value.
    :return the key whose dictionary entry is value
    """
    for key in d.keys():
        if d[key] == value:
            return key
    return 'Null'


def run_vancouver():
    """
    Runs the Vancouver algorithm, modifying the "submissions" and "graders" global arrays.
    """
    parse_data()
    updated = True
    i = 0
    while updated and i < 1:
        i += 1
        updated = False
        updated = updated or update_submission_variance_estimates()
        updated = updated or update_grade_estimates()
        updated = updated or update_user_variance_estimates()
    for submission in submissions:
        subid = backtrace(submission_dict, submission.index)
        print(subid)
        print(submission)
'''
    with open('fold3.csv', 'w') as csvfile:
        foldwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for submission in submissions:
            subid = backtrace(submission_dict, submission.index)
            print(subid)
            foldwriter.writerow([str(subid), str(submission.grade)])
            print(submission)
'''

parse_peer_grades()
if USE_GROUND_TRUTH:
    parse_truth()
run_vancouver()
