"""
This file is for code that can be used to run simulations of Vancouver.
"""

from peer_review import *
import numpy as np
import matplotlib.pyplot as plt


stat_ids = {'Submission Grade Error': 0, 'Submission Variance Error': 1, 'User Variance Error': 2}


def evaluate_vancouver(num_assignments, num_reviews, num_truths, peer_quality, use_cover=True,
                       vancouver_steps=10,
                       grading_algorithm=lambda x: random.choice(x[0])):
    # generate random groups, assignments, qualities, and reviews
    """
    :param num_assignments: the number of submissions in the pool
    :param num_reviews: the number of submsisions reviewed by each student
    :param num_truths: the number of submissions to "see" a ground truth grade for
    :param peer_quality: a tuple of (function, arg_1, ..., arg_n) which will be called once for each grader to determine
    that grader's true quality. The function should return an integer, which will be used to determine how many samples
    that grader gets from the distribution (in our current model).
    :param vancouver_steps: the number of iterations before vancouver terminates
    :param peer_quality: tuple of (function, args) that returns an integer

    :return a tuple of three arrays, representing the submission grade errors, submission variance errors, and
    grader variance errors
    """
    groups = {sub: [sub + x for x in ['1', '2', '3']] for sub in [chr(ord('a') + z) for z in range(num_assignments)]}
    assignments, cover = peer_assignment_return_cover(groups, num_reviews)
    true_qualities = {i: peer_quality[0](*peer_quality[1:]) for i in assignments}
    reviews = random_reviews(assignments, true_qualities)

    # generate a random ground truth value for all submissions
    truths = {i: 0.5 for i in groups}

    # run initial vancouver
    truths_visible = {i: 0.5 for i in cover}
    init_scores, init_qualities = vancouver(reviews, truths_visible, vancouver_steps)
    omni_scores, omni_qualities = vancouver(reviews, truths, vancouver_steps)

    # make a truths_visible dictionary for the algorithm to have access to
    if use_cover:
        if len(cover) > num_truths:
            truths_visible = {i[0]: 0.5 for i in random.sample(list(cover), num_truths)}
        else:
            truths_visible = {i: 0.5 for i in cover}
            while len(truths_visible.keys()) < num_truths:
                truths_visible[grading_algorithm(truths, (init_qualities, init_scores),
                                                 (omni_scores, true_qualities))] = 0.5
    else:
        truths_visible = {i[0]: 0.5 for i in random.sample(list(truths), num_truths)}

    # run vancouver and omniscient vancouver
    scores, qualities = vancouver(reviews, truths_visible, vancouver_steps)

    # generate statistics on the data
    sub_score_error = [abs(scores[submission][0] - 0.5) for submission in scores]
    sub_var_error = [abs(scores[submission][1] - omni_scores[submission][1]) for submission in scores]
    grader_var_error = [abs(qualities[grader] - true_qualities[grader]) for grader in qualities]

    return sub_score_error, sub_var_error, grader_var_error


def vancouver_statistics(num_assignments, num_reviews, num_truths, num_runs, peer_quality,
                         use_cover=True, vancouver_steps=10):
    # generate each statistic for num_runs trials
    means_acc = []
    medians_acc = []
    maxes_acc = []
    for _ in range(num_runs):
        errors = evaluate_vancouver(num_assignments, num_reviews, num_truths, peer_quality,
                                    use_cover, vancouver_steps)
        means = [np.mean(stat) for stat in errors]
        means_acc.append(means)
        medians = [np.median(stat) for stat in errors]
        medians_acc.append(medians)
        maxes = [max(stat) for stat in errors]
        maxes_acc.append(maxes)

    # average the results of the statistics across the trials
    mean_average = np.mean(means_acc, axis=0)
    median_average = np.mean(medians_acc, axis=0)
    max_average = np.mean(maxes_acc, axis=0)

    # tidy up the output for user-friendliness
    mean_dict = {'sub_grade': mean_average[0], 'sub_var': mean_average[1], 'usr_var': mean_average[2]}
    median_dict = {'sub_grade': median_average[0], 'sub_var': median_average[1], 'usr_var': median_average[2]}
    max_dict = {'sub_grade': max_average[0], 'sub_var': max_average[1], 'usr_var': max_average[2]}

    return {'mean': mean_dict, 'median': median_dict, 'max': max_dict}


def print_stats(stats):
    print 'Expectation of the Error in a Given Trial', '\n'

    print 'Assignment Grades:'
    print 'Mean Error: ', stats['mean']['sub_grade']
    print 'Maximum Error: ', stats['max']['sub_grade']
    print 'Median Error: ', stats['median']['sub_grade'], '\n'

    print 'Assignment Variances:'
    print 'Mean Error: ', stats['mean']['sub_var']
    print 'Maximum Error: ', stats['max']['sub_var']
    print 'Median Error: ', stats['median']['sub_var'], '\n'

    print 'Grader Variances:'
    print 'Mean Error: ', stats['mean']['usr_var']
    print 'Maximum Error: ', stats['max']['usr_var']
    print 'Median Error: ', stats['median']['usr_var'], '\n', '\n'


def plot_stats(stat_type, stat_variable, peer_quality, use_cover=True,
               vancouver_steps=10, num_subs=20, num_grades_per_sub=3, num_trials=10, step_size=1):
    stats = []
    for num_true_grades in range(0, num_subs + step_size, step_size):
        # print(num_true_grades)
        stats.append(vancouver_statistics(num_subs, num_grades_per_sub, num_true_grades, num_trials, peer_quality,
                                          use_cover, vancouver_steps)[stat_type][stat_variable])

    plt.plot(range(0, num_subs + step_size, step_size), stats)
    plt.xlabel('Number of Ground-Truth Grades')
    plt.ylabel(stat_type + ' ' + stat_variable + ' Error')
    plt.show()


def plot_histogram(num_subs=20, num_grades_per_sub=3, num_truths=5, peer_quality=(random.randint, 1, 5), use_cover=True,
                   vancouver_steps=10, stat_type='Submission Grade Error', num_trials=20, cumulative=True,
                   grading_algorithm=lambda x: random.choice(x[0])):
    vancouver_bulk = []
    for _ in range(num_trials):
        vancouver_bulk.extend(evaluate_vancouver(num_subs, num_grades_per_sub, num_truths,
                                                 peer_quality, use_cover, vancouver_steps,
                                                 grading_algorithm=grading_algorithm)[stat_ids[stat_type]])
    plt.hist(vancouver_bulk, cumulative=cumulative)
    plt.xlabel(stat_type)
    plt.show()


def plot_cdfs(num_subs=20, num_grades_per_sub=3, num_truths=(0, 5, 10, 15), peer_quality=(random.randint, 1, 5),
              use_cover=True, vancouver_steps=10, stat_type='Submission Grade Error', num_trials=50,
              grading_algorithm=lambda x: random.choice(x[0]), resolution=100, xrange=[0, 0.4]):
    for truth_num in num_truths:
        vancouver_bulk = []
        for _ in range(num_trials):
            vancouver_bulk.extend(evaluate_vancouver(num_subs, num_grades_per_sub, truth_num,
                                                     peer_quality, use_cover, vancouver_steps,
                                                     grading_algorithm=grading_algorithm)[stat_ids[stat_type]])
        vancouver_bulk.sort()
        vmin = vancouver_bulk[0]
        vmax = vancouver_bulk[-1]
        step = (vmax - vmin) / resolution
        hist = []
        values = []
        i = 0
        for value in np.arange(vmin, vmax, step):
            while vancouver_bulk[i] < value:
                i += 1
            hist.append(i)
            values.append(value)
        hist_max = hist[-1]
        hist = [float(item) / hist_max for item in hist]
        plt.plot(values, hist)
    plt.legend(num_truths)
    plt.xlabel(stat_type)
    plt.ylabel('Normalized CDF')
    plt.xlim(xrange)
    plt.show()


def plot_cdfs_2(num_subs=20, num_grades_per_sub=3, num_truths=(10,), peer_quality=(random.randint, 1, 5),
                use_cover=True, vancouver_steps=(1, 10, 20), stat_type='Submission Grade Error', num_trials=50,
                grading_algorithm=lambda x: random.choice(x[0]), resolution=100, xrange=[0, 0.4]):
    """
    Allows plotting of multiple Vancouver iterations at once.
    :return:
    """
    legend = []
    for vs in vancouver_steps:
        for truth_num in num_truths:
            vancouver_bulk = []
            for _ in range(num_trials):
                vancouver_bulk.extend(evaluate_vancouver(num_subs, num_grades_per_sub, truth_num,
                                                         peer_quality, use_cover, vs,
                                                         grading_algorithm=grading_algorithm)[stat_ids[stat_type]])
            vancouver_bulk.sort()
            vmin = vancouver_bulk[0]
            vmax = vancouver_bulk[-1]
            step = (vmax - vmin) / resolution
            hist = []
            values = []
            i = 0
            for value in np.arange(vmin, vmax, step):
                while vancouver_bulk[i] < value:
                    i += 1
                hist.append(i)
                values.append(value)
            hist_max = hist[-1]
            hist = [float(item) / hist_max for item in hist]
            plt.plot(values, hist)
            legend.append(str(vs) + ' Steps, ' + str(truth_num) + ' True Grades')
    plt.legend(legend, loc=4)
    plt.xlabel(stat_type)
    plt.ylabel('Normalized CDF')
    plt.xlim(xrange)
    plt.show()
    return


def plot_cdfs_3(num_subs=20, num_grades_per_sub=3, num_truths=(0,), peer_quality=(random.randint, 1, 5),
                use_cover=True, vancouver_steps=10, stat_type='Submission Grade Error', num_trials=50,
                algs=(lambda x: random.choice(x[0]), ), alg_names=('Random', ), resolution=100, xrange=[0, 0.4]):
    legend=[]
    for j, grading_algorithm in enumerate(algs):
        for truth_num in num_truths:
            vancouver_bulk = []
            for _ in range(num_trials):
                vancouver_bulk.extend(evaluate_vancouver(num_subs, num_grades_per_sub, truth_num,
                                                         peer_quality, use_cover, vancouver_steps,
                                                         grading_algorithm=grading_algorithm)[stat_ids[stat_type]])
            vancouver_bulk.sort()
            vmin = vancouver_bulk[0]
            vmax = vancouver_bulk[-1]
            step = (vmax - vmin) / resolution
            hist = []
            values = []
            i = 0
            for value in np.arange(vmin, vmax, step):
                while vancouver_bulk[i] < value:
                    i += 1
                hist.append(i)
                values.append(value)
            hist_max = hist[-1]
            hist = [float(item) / hist_max for item in hist]
            plt.plot(values, hist)
            legend.append(alg_names[j] + ', ' + str(truth_num) + ' Ground Truths')
    plt.legend(legend, loc=4)
    plt.xlabel(stat_type)
    plt.ylabel('Normalized CDF')
    plt.xlim(xrange)
    plt.show()


def plot_cdfs_4(num_subs=20, num_grades_per_sub=3, num_truths=(0,), peer_qualities=((random.randint, 1, 5),),
                use_cover=True, vancouver_steps=10, stat_type='Submission Grade Error', num_trials=50,
                grading_algorithm=lambda x: random.choice(x[0]), pq_names=('Random on {1,2,3,4,5}',), resolution=100, xrange=[0, 0.4]):
    legend = []
    for j, peer_quality in enumerate(peer_qualities):
        for truth_num in num_truths:
            vancouver_bulk = []
            for _ in range(num_trials):
                vancouver_bulk.extend(evaluate_vancouver(num_subs, num_grades_per_sub, truth_num,
                                                         peer_quality, use_cover, vancouver_steps,
                                                         grading_algorithm=grading_algorithm)[stat_ids[stat_type]])
            vancouver_bulk.sort()
            vmin = vancouver_bulk[0]
            vmax = vancouver_bulk[-1]
            step = (vmax - vmin) / resolution
            hist = []
            values = []
            i = 0
            for value in np.arange(vmin, vmax, step):
                while vancouver_bulk[i] < value:
                    i += 1
                hist.append(i)
                values.append(value)
            hist_max = hist[-1]
            hist = [float(item) / hist_max for item in hist]
            plt.plot(values, hist)
            legend.append(pq_names[j] + ', ' + str(truth_num) + ' Truths')
    plt.legend(legend, loc=4)
    plt.xlabel(stat_type)
    plt.ylabel('Normalized CDF')
    plt.xlim(xrange)
    plt.show()