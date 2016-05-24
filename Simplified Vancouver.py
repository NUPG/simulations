"""
Simplified Vancouver Algorithm

Author: Donald "Drew" Bronson
Creation Date:  12 May 2016

This algorithm was developed by Jason Hartline, Samuel Taggart, and Doug Downey at Northwestern University as part of
a research project in the field of peer grading algorithms. It represents a simplified version of the Vancouver
algorithm and is hypothesized by the above to output comparable results.

This file is a complete re-write of the original.
"""

from simplified_vancouver_tests import *


def read_peer_grades(filename):
    """
    Reads in the peer grades and returns them in submissions-have-graders format.

    :param filename: a string pointing to the file to read in from
    :return: a dictionary from submission_id (string) to submission, where a submission is a dictionary from
    grader_id (string) to grader_grade (float)
    """
    with open(filename) as grades_reader:
        peer_grades = {submission_id : {grader_id : grader_grade} for
                       submission_id, grader_id, grader_grade in grades_reader}
    return peer_grades


def read_ground_truth(filename):
    """
    Reads in the ground truths and returns them.

    :param filename: a string pointing to the file to read in from
    :return: a dictionary from submission_id (string) to ground_truth_grade (float)
    """
    with open(filename) as truth_reader:
        ground_truth = {submission_id : true_grade for
                        submission_id, true_grade in truth_reader}
    return ground_truth


def reciprocal(k: float):
    if k == 0:
        return 1.0 / (k + 0.01)
    else:
        return 1.0 / k


def get_submission_variances(user_variances, submissions):
    """
    Returns the submission variances, given user variances and submissions, where submissions are represented as
    dictionaries of the format grader:grade.

    :param user_variances: a dictionary from user_id (string) to user_variance (float)
    :param submissions: a dictionary from submission_id (string) to submission, where a submission is a dictionary from
    user_id (string) to user_grade (float)
    :return: a dictionary from submission_id (string) to submission_variance (float)
    """
    submission_variance_estimates = {}
    for submission_id in submissions:
        submission = submissions[submission_id]
        submission_variance_estimate = 0
        for grader_id in submission:
            grader_variance = user_variances[grader_id]
            submission_variance_estimate += reciprocal(grader_variance)
        submission_variance_estimate = reciprocal(submission_variance_estimate)
        submission_variance_estimates[submission_id] = submission_variance_estimate
    return submission_variance_estimates


def get_grade_estimates(user_variances, submission_variances, submissions, ground_truths=None):
    """
    Returns the grade estimates, given user variances, submission variances, and submissions represented as
    dictionaries of the format grader:grade.

    :param user_variances: a dictionary from user_id (string) to user_variance (float)
    :param submission_variances: a dictionary from submission_id (string) to submission_variance (float)
    :param submissions: a dictionary from submission_id (string) to submission, where a submission is a dictionary from
    user_id (string) to user_grade (float)
    :param ground_truths: optional dictionary from submission_id (string) to ground_truth_grade (float). Will be used
    if present to force submission grades to the ground truth values.
    :return: a dictionary from submission_id (string) to submission_grade_estimate (float)
    """
    grade_estimates = {}
    for submission_id in submissions:
        if ground_truths is not None and submission_id in ground_truths:
            grade_estimates[submission_id] = ground_truths[submission_id]
            continue
        submission = submissions[submission_id]
        grade_estimate = 0
        for grader_id in submission:
            grader_variance = user_variances[grader_id]
            grader_grade = submission[grader_id]
            grade_estimate += reciprocal(grader_variance) * grader_grade
        grade_estimate *= submission_variances[submission_id]
        grade_estimates[submission_id] = grade_estimate
    return grade_estimates


def get_user_variance_estimates(submission_variances, grade_estimates, graders):
    """
    Returns the user variance estimates, given submission variances, grade estimates, and graders represented as
    dictionaries of the format submission:grade.

    :param submission_variances: a dictionary from submission_id (string) to submission_variance (float)
    :param grade_estimates: a dictionary from submission_id (string) to submission_grade_estimate (float)
    :param graders: a dictionary from grader_id (string) to grader, where a grader is a dictionary from
    submission_id (string) to submission_grade (float)
    :return: a dictionary from user_id (string) to user_variance (float)
    """
    user_variances = {}
    for grader_id in graders:
        grader = graders[grader_id]
        acc_1 = 0
        for submission_id in grader:
            submission_variance = submission_variances[submission_id]
            acc_1 += reciprocal(submission_variance)
        acc_1 = reciprocal(acc_1)
        acc_2 = 0
        for submission_id in grader:
            submission_variance = submission_variances[submission_id]
            grader_grade = grader[submission_id]
            grade_estimate = grade_estimates[submission_id]
            grade_difference = grader_grade - grade_estimate
            acc_2 += reciprocal(submission_variance) * (grade_difference ** 2)
        user_variances[grader_id] = acc_1 * acc_2
    return user_variances


def convert_submissions_to_graders(submissions):
    """
    Converts between the submissions-have-graders and graders-have-submissions forms of representing the peer grades.

    :param submissions: a dictionary from submission_id to submission, where a submission is a dictionary from
    grader_id (string) to grader_grade (float)
    :return: a dictionary from grader_id to grader, where a grader is a dictionary from submission_id (string) to
    submission_grade (float)
    """
    graders = {}
    for submission_id in submissions:
        submission = submissions[submission_id]
        for grader_id in submission:
            grader = {submission_id : submissions[submission_id][grader_id]}
            graders[grader_id] = grader
    return graders


def convert_graders_to_submissions(graders):
    """
    Wrappers the convert_submissions_to_graders function, which should rotate the array properly due to symmetry.

    :param graders: a dictionary from grader_id to grader, where a grader is a dictionary from submission_id (string)
    to submission_grade (float)
    :return: a dictionary from submission_id to submission, where a submission is a dictionary from grader_id (string)
    to grader_grade (float)
    """
    submissions = {}
    for grader_id in graders:
        grader = graders[grader_id]
        for submission_id in grader:
            grade = graders[grader_id][submission_id]
            submission = {grader_id: grade}
            submissions[submission_id] = submission
    return submissions


def vancouver_iteration(user_variances, submissions, ground_truths=None):
    """
    Takes in data from a previous time-step of the Vancouver algorithm (or the initial conditions) and outputs the
    data for the next iteration or display.

    :param user_variances: a dictionary from user_id (string) to user_variance (float)
    :param submissions: a dictionary from submission_id (string) to submission, where a submission is a dictionary from
    grader_id (string) to grader_grade (float)
    :return: submission_variances, grade_estimates, user_variances, submissions
    """

    submission_variances = get_submission_variances(user_variances, submissions)
    grade_estimates = get_grade_estimates(user_variances, submission_variances, submissions, ground_truths)
    graders = convert_submissions_to_graders(submissions)
    user_variances = get_user_variance_estimates(submission_variances, grade_estimates, graders)
    return submission_variances, grade_estimates, user_variances


def backtrace(d: dict, v: int):
    """
    Searches through the provided dictionary for the key whose value is v.

    :param d: a dictionary to search through
    :param v: the value to search for
    :return: a key from the dictionary
    """
    for key in d.keys():
        if d[key] == v:
            return key
    return 'Null'


def print_submissions(submissions, grade_estimates, submission_variances):
    """
    Prints the submissions dictionary in human-readable format.

    :param submissions: the submissions dictionary {string : {string : float}}
    :param grade_estimates: the grade_estimates dictionary {string : float}
    :param submission_variances: the submission_variances dictionary {string : float}
    :return:
    """
    for submission_id in submissions:
        print("Submission ID: ", submission_id, "\n")
        print("Submission Grade: ", grade_estimates[submission_id], "\n")
        print("Submission Variance: ", submission_variances[submission_id], "\n")
        print("\n")


def print_graders(graders, grader_variances):
    """
    Prints the graders dictionary in human-readable format.

    :param graders: the graders dictionary {string : {string : float}}
    :param grader_variances: the grader_variances dictionary {string : float}
    :return:
    """
    for grader_id in graders:
        print("Grader ID: ", grader_id, "\n")
        print("Grader Variance: ", grader_variances[grader_id], "\n")
        print("\n")


def run_vancouver(submissions, ground_truths=None, default_grader_variance=1.0):
    # initialize dummy user variances dictionary
    graders = convert_submissions_to_graders(submissions)
    grader_variances = {grader_id : default_grader_variance for grader_id in graders}

    for i in range(10):
        submission_variances, grade_estimates, grader_variances =\
            vancouver_iteration(grader_variances, submissions, ground_truths)
    return submissions, grade_estimates, submission_variances, grader_variances


s, ge, sv, gv = run_vancouver(test_submissions)
print_submissions(s, ge, sv)
print_graders(convert_submissions_to_graders(s), gv)