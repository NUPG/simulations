"""
This file is for code that can be used to run simulations of Vancouver.
"""

from peer_review import *
import numpy as np
import matplotlib.pyplot as plt


def evaluate_vancouver(num_assignments, num_reviews, num_truths, min_quality=1, max_quality=5, use_cover=True,
                       vancouver_steps=10):
    # generate random groups, assignments, qualities, and reviews
    groups = {sub: [sub + x for x in ['1', '2', '3']] for sub in [chr(ord('a') + z) for z in range(num_assignments)]}
    assignments, cover = peer_assignment(groups, num_reviews)
    true_qualities = {i: random.randint(min_quality, max_quality) for i in assignments}
    reviews = random_reviews(assignments, true_qualities)

    # generate a random ground truth value for all submissions
    truths = {i: 0.5 for i in groups}

    # make a truths_visible dictionary for the algorithm to have access to
    if use_cover:
        if len(cover) > num_truths:
            truths_visible = {i[0]: 0.5 for i in random.sample(list(cover), num_truths)}
        else:
            truths_visible = {i: 0.5 for i in cover}
            while len(truths_visible.keys()) < num_truths:
                truths_visible[random.choice(truths)] = 0.5
    else:
        truths_visible = {i[0]: 0.5 for i in random.sample(list(truths), num_truths)}

    # run vancouver and omniscient vancouver
    scores, qualities = vancouver(reviews, truths_visible, vancouver_steps)
    omni_scores, omni_qualities = vancouver(reviews, truths, vancouver_steps)

    # generate statistics on the data
    sub_score_error = [abs(scores[submission][0] - 0.5) for submission in scores]
    sub_var_error = [abs(scores[submission][1] - omni_scores[submission][1]) for submission in scores]
    grader_var_error = [abs(qualities[grader] - true_qualities[grader]) for grader in qualities]

    return sub_score_error, sub_var_error, grader_var_error


def vancouver_statistics(num_assignments, num_reviews, num_truths, num_runs, min_quality=1, max_quality=5,
                         use_cover=True, vancouver_steps=10):
    # generate each statistic for num_runs trials
    means_acc = []
    medians_acc = []
    maxes_acc = []
    for _ in range(num_runs):
        errors = evaluate_vancouver(num_assignments, num_reviews, num_truths, min_quality, max_quality,
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
    print('Expectation of the Error in a Given Trial', '\n')

    print('Assignment Grades:')
    print('Mean Error: ', stats['mean']['sub_grade'])
    print('Maximum Error: ', stats['max']['sub_grade'])
    print('Median Error: ', stats['median']['sub_grade'], '\n')

    print('Assignment Variances:')
    print('Mean Error: ', stats['mean']['sub_var'])
    print('Maximum Error: ', stats['max']['sub_var'])
    print('Median Error: ', stats['median']['sub_var'], '\n')

    print('Grader Variances:')
    print('Mean Error: ', stats['mean']['usr_var'])
    print('Maximum Error: ', stats['max']['usr_var'])
    print('Median Error: ', stats['median']['usr_var'], '\n', '\n')


def plot_stats(stat_type, stat_variable, min_quality=1, max_quality=5, use_cover=True,
               vancouver_steps=10, num_subs=20, num_grades_per_sub=3, num_trials=10, step_size=1):
    stats = []
    for num_true_grades in range(0, num_subs + step_size, step_size):
        # print(num_true_grades)
        stats.append(vancouver_statistics(num_subs, num_grades_per_sub, num_true_grades, num_trials, min_quality,
                                          max_quality, use_cover)[stat_type][stat_variable])

    plt.plot(range(0, num_subs + step_size, step_size), stats)
    plt.xlabel('Number of Ground-Truth Grades')
    plt.ylabel(stat_type + ' ' + stat_variable + ' Error')
    plt.title('Quality ranging from ' + str(min_quality) + ' to ' + str(max_quality))
    plt.show()