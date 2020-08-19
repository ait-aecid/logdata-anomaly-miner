import pickle
from scipy.stats import uniform, norm, beta, bernoulli
import matplotlib.pyplot as plt

distr_list = ['nor', 'uni', 'spec', 'beta']  # List of the distributions for which the sample generator is implemented
count_distr = [1, 1, 1, 1, 1, 1]


# Generates totalcount logdata with one variables distributed according to the distr in distr_list_in
def generate_sample(changes_at, distr_list_in, totalcount, plot_bool=False, spec_distr_file_name=None):
    if len(changes_at) != len(distr_list_in) - 1 or totalcount < 1:
        print('Warning: len(changes_at) != len(distr_list_in)-1 in generate_sample')
        return None

    changes_at.sort()

    if changes_at and changes_at[-1] > totalcount:
        print('Warning: changes_at[-1] > totalcount in generate_sample')
        return None

    path_name = ''
    if len(distr_list_in) == 1 and distr_list_in[0][0] in distr_list:
        path_name = 'con' + str(count_distr[distr_list.index(distr_list_in[0][0])])
        count_distr[distr_list.index(distr_list_in[0][0])] += 1
    elif len(distr_list_in) == 1 and distr_list_in[0][0] == 'd':
        path_name = 'discrete' + str(count_distr[5])
        count_distr[5] += 1
    else:
        path_name = 'mixed' + str(count_distr[4])
        count_distr[4] += 1

    data_lst = []
    if len(changes_at) == 0:
        val = gs_rvs(distr_list_in[0], totalcount, spec_distr_file_name)

        for v in val:
            data_lst.append((path_name, v))
        if plot_bool:
            plt.hist(val, bins='auto', alpha=0.5)
    else:
        val = gs_rvs(distr_list_in[0], changes_at[0], spec_distr_file_name)

        for v in val:
            data_lst.append((path_name, v))
        if plot_bool:
            plt.hist(val, bins='auto', alpha=0.5)

    for i in range(1, len(distr_list_in) - 1):
        val = gs_rvs(distr_list_in[i], changes_at[i] - changes_at[i - 1], spec_distr_file_name)
        for v in val:
            data_lst.append((path_name, v))
        if plot_bool:
            plt.hist(val, bins='auto', alpha=0.5)

    if len(changes_at) != 0 and changes_at[-1] != totalcount:
        val = gs_rvs(distr_list_in[-1], totalcount - changes_at[-1], spec_distr_file_name)
        for v in val:
            data_lst.append((path_name, v))
        if plot_bool:
            plt.hist(val, bins='auto', alpha=0.5)

    if plot_bool:
        plt.show()
    return data_lst


# Generating a random variable sample
def gs_rvs(distr, num, spec_distr_file_name=None):  # ['nor', 'uni', 'spec', 'beta']
    if (distr[0] not in distr_list) and (distr[0] != 'd'):
        return []

    if distr[0] == 'd':  # ['d', ['A', 'B', 'C'], [0.2, 0.2, 0.6]]
        x = list(bernoulli.rvs(1 - distr[2][0], loc=0, size=num, random_state=None))
        for i in range(num):
            if x[i] == 1 and len(distr[1]) >= 3:
                if bernoulli.rvs(1 - (distr[2][1]) / (1 - distr[2][0]), loc=0, size=1, random_state=None)[0] == 1:
                    x[i] = distr[1][2]
                else:
                    x[i] = distr[1][1]
            else:
                x[i] = distr[1][0]
        return x

    if distr[0] == 'nor':
        x = []
        tmp = 0
        while tmp < num:
            y = norm.rvs(loc=distr[1], scale=distr[2], size=num - tmp)
            y = [i for i in y if distr[3] <= i <= distr[4]]
            tmp += len(y)
            x += y
        return x

    if distr[0] == 'uni':
        x = uniform.rvs(distr[1], distr[2] - distr[1], size=num)
        return x

    if distr[0] == 'spec':
        x = []
        tmp = 0

        f = open(spec_distr_file_name, 'rb')
        varsample = pickle.load(f)
        f.close()
        if distr[5] == 1:
            varsample = -varsample
        while tmp < num:
            y = uniform.rvs(loc=0, scale=1, size=num - tmp) * len(varsample)
            y = [varsample[int(i)] * distr[2] + distr[1] for i in y if distr[3] <= varsample[int(i)] * distr[2] + distr[1] <= distr[4]]
            tmp += len(y)
            x += y
        return x

    if distr[0] == 'beta':
        x = []
        tmp = 0
        a, b = 0, 0
        if distr[5] == 1:
            a, b = 0.5, 0.5
        elif distr[5] == 2:
            a, b = 5, 2
        elif distr[5] == 3:
            a, b = 2, 5
        elif distr[5] == 4:
            a, b = 1, 5
        elif distr[5] == 5:
            a, b = 5, 1

        while tmp < num:
            y = beta.rvs(a, b, loc=distr[1], scale=distr[2], size=num - tmp)
            y = [i for i in y if distr[3] <= i <= distr[4]]
            tmp += len(y)
            x += y
        return x
    return []


if __name__ == '__main__':
    var_ev = 0
    var_var = 2
    dir1 = r"/tmp/testdaten_generiert"
    spec_distr_file = r"spec_distribution_k"
    with open(dir1, "w") as fobj1:
        # ["string:uni", -1, 1] # Variance = var_var/np.sqrt(3)  # generate_sample([], [['nor', var_ev, var_var, -1000, 1000]], 50, fobj1)
        # ["string:nor", 0, 1, -1000, 1000]
        data_list = generate_sample([], [['uni', var_ev - var_var, var_ev + var_var]], 50, plot_bool=False)
        data_list += generate_sample([], [['spec', 0, 1, -1000, 1000, 0]], 200, plot_bool=False, spec_distr_file_name=spec_distr_file)
        # ["string:beta", 0, 1, -1000, 1000, 1]
        data_list += generate_sample([], [['beta', (-0.5 + var_ev) / 0.35355339059327379 * var_var, 1 / 0.35355339059327379 * var_var,
                                          -1000, 1000, 1]], 50, plot_bool=False)
        # ["string:beta", 0, 1, -1000, 1000, 2]
        data_list += generate_sample([], [
            ['beta', (-0.7142857142857143 + var_ev) / 0.15971914124998499 * var_var, 1 / 0.15971914124998499 * var_var, -1000, 1000, 2]],
            50, plot_bool=False)
        # ["string:beta", 0, 1, -1000, 1000, 4]
        data_list += generate_sample([], [
            ['beta', (-0.166666666666 + var_ev) / 0.14085904245475278 * var_var, 1 / 0.14085904245475278 * var_var, -1000, 1000, 4]], 50,
            plot_bool=False)
        data_list += generate_sample([250, 500], [['nor', 100, 1, 90, 110], ['uni', 90, 110], ['nor', 110, 1, 90, 110]], 1000,
                                     plot_bool=False)

        for data_type, data in data_list:
            fobj1.write('%s %f\n' % (data_type, data))
