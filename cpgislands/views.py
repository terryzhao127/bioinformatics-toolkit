import math
from django.shortcuts import render

# Create your views here.
from BioinformaticsToolkit import utils

__EXTREMELY_SMALL_NUM = 0.001


def get_page(request):
    return render(request, 'cpgislands/page.html')


def algorithm(request):
    # Get necessary data.
    work_type = request.POST['work_type']
    train_set_pos = __get_raw_seqs(
        utils.get_fasta_from_file(request.FILES['train-set-pos']))
    train_set_neg = __get_raw_seqs(
        utils.get_fasta_from_file(request.FILES['train-set-neg']))
    test_set = utils.get_fasta_from_file(request.FILES['test-set'])

    # Select algorithm by work type number.
    work_type = int(work_type)
    if work_type == 0:
        threshold = request.POST['threshold']
        threshold = float(threshold)

        result, pos_matrix, neg_matrix = __identify_cpg_island(train_set_pos,
                                                               train_set_neg,
                                                               test_set,
                                                               threshold)
        return render(request, 'cpgislands/result.html', {
            'work_type': work_type,
            'result': result,
            'pos_matrix': pos_matrix,
            'neg_matrix': neg_matrix,
        })
    else:
        prob_p = request.POST['probability-p']
        prob_q = request.POST['probability-q']
        prob_p = float(prob_p)
        prob_q = float(prob_q)

        result, joint_matrix = __find_cpg_island(train_set_pos, train_set_neg,
                                                 test_set, prob_p, prob_q)
        processed_matrix = {
            'aplus': {},
            'tplus': {},
            'cplus': {},
            'gplus': {},
            'aminus': {},
            'tminus': {},
            'cminus': {},
            'gminus': {},
        }
        for state, row in joint_matrix.items():
            for dest, item in row.items():
                if state[1] == '+' and dest[1] == '+':
                    processed_matrix[state[0] + 'plus'][dest[0] + 'plus'] = \
                        joint_matrix[state][dest]
                elif state[1] == '+' and dest[1] == '-':
                    processed_matrix[state[0] + 'plus'][dest[0] + 'minus'] = \
                        joint_matrix[state][dest]
                elif state[1] == '-' and dest[1] == '-':
                    processed_matrix[state[0] + 'minus'][dest[0] + 'minus'] = \
                        joint_matrix[state][dest]
                elif state[1] == '-' and dest[1] == '+':
                    processed_matrix[state[0] + 'minus'][dest[0] + 'plus'] = \
                        joint_matrix[state][dest]

        return render(request, 'cpgislands/result.html', {
            'work_type': work_type,
            'result': result,
            'joint_matrix': processed_matrix,
        })


def __find_cpg_island(train_set_pos, train_set_neg, test_set, prob_p, prob_q):
    # Initialize joint
    joint_matrix = {}
    for i in 'actg':
        joint_matrix[i + '+'] = {}
        joint_matrix[i + '-'] = {}
        for j in 'actg':
            joint_matrix[i + '+'][j + '+'] = 0
            joint_matrix[i + '+'][j + '-'] = 0
            joint_matrix[i + '-'][j + '-'] = 0
            joint_matrix[i + '-'][j + '+'] = 0

    # Train matrices
    for seq in train_set_pos:
        for i, ch in enumerate(seq):
            if i == len(seq) - 1:
                break
            joint_matrix[seq[i] + '+'][seq[i + 1] + '+'] += 1
    for seq in train_set_neg:
        for i, ch in enumerate(seq):
            if i == len(seq) - 1:
                break
            joint_matrix[seq[i] + '-'][seq[i + 1] + '-'] += 1

    for i in joint_matrix:
        total_frequency = 0
        for j in joint_matrix[i]:
            if i[1] == j[1]:
                total_frequency += joint_matrix[i][j]
        for j in joint_matrix[i]:
            if i[1] == j[1]:
                if joint_matrix[i][j] == 0:
                    joint_matrix[i][j] = __EXTREMELY_SMALL_NUM
                else:
                    if i[1] == '+':
                        joint_matrix[i][j] = joint_matrix[i][
                                                 j] / total_frequency * prob_p
                    else:
                        joint_matrix[i][j] = joint_matrix[i][
                                                 j] / total_frequency * prob_q
            else:
                if i[1] == '+':
                    joint_matrix[i][j] = (1 - prob_p) / 4
                else:
                    joint_matrix[i][j] = (1 - prob_q) / 4

    # Viterbi Algorithm
    result = []
    for seq_data in test_set:
        seq = seq_data[1]
        viterbi_matrix = {key: [0 for x in range(len(seq))] for key in '+-'}
        viterbi_matrix['+'][0] = viterbi_matrix['-'][0] = 1
        for i, ch in enumerate(seq):
            if i == len(seq) - 1:
                break
            pos_base = ch + '+'
            neg_base = ch + '-'
            next_base = seq[i + 1]
            for sign in viterbi_matrix:
                viterbi_matrix[sign][i + 1] = max(
                    math.log(joint_matrix[pos_base][next_base + sign], 2) *
                    viterbi_matrix['+'][i],
                    math.log(joint_matrix[neg_base][next_base + sign], 2) *
                    viterbi_matrix['-'][i])
        # Traceback
        if viterbi_matrix['+'][len(seq) - 1] >= viterbi_matrix['-'][
                    len(seq) - 1]:
            temp = '+'
        else:
            temp = '-'

        trace_result = [seq[len(seq) - 1] + temp]
        for i in range(len(seq) - 2, -1, -1):
            for sign in viterbi_matrix:
                a = viterbi_matrix[sign][i] * math.log(
                    joint_matrix[seq[i] + sign][
                        seq[i + 1] + temp], 2)
                b = viterbi_matrix[temp][i + 1]
                if viterbi_matrix[sign][i] * math.log(
                        joint_matrix[seq[i] + sign][
                                    seq[i + 1] + temp], 2) == \
                        viterbi_matrix[temp][i + 1]:
                    if sign == '-':
                        trace_result.insert(0, (seq[i], 0))
                    else:
                        trace_result.insert(0, (seq[i], 1))
                    temp = sign
                    break
        result.append((seq_data, trace_result))

    return result, joint_matrix


def __identify_cpg_island(train_set_pos, train_set_neg, test_set, threshold):
    # Initialize matrices
    pos_matrix = {}
    neg_matrix = {}
    for i in 'actg':
        pos_matrix[i] = {}
        neg_matrix[i] = {}
        for j in 'actg':
            pos_matrix[i][j] = 0
            neg_matrix[i][j] = 0

    # Train matrices
    for seq in train_set_pos:
        for i, ch in enumerate(seq):
            if i == len(seq) - 1:
                break
            pos_matrix[seq[i]][seq[i + 1]] += 1
    for i in pos_matrix:
        total_frequency = 0
        for j in pos_matrix[i]:
            total_frequency += pos_matrix[i][j]
        for j in pos_matrix[i]:
            if pos_matrix[i][j] == 0:
                pos_matrix[i][j] = __EXTREMELY_SMALL_NUM
            else:
                pos_matrix[i][j] = pos_matrix[i][j] / total_frequency

    for seq in train_set_neg:
        for i, ch in enumerate(seq):
            if i == len(seq) - 1:
                break
            neg_matrix[seq[i]][seq[i + 1]] += 1
    for i in neg_matrix:
        total_frequency = 0
        for j in neg_matrix[i]:
            total_frequency += neg_matrix[i][j]
        for j in neg_matrix[i]:
            if neg_matrix[i][j] == 0:
                neg_matrix[i][j] = __EXTREMELY_SMALL_NUM
            else:
                neg_matrix[i][j] = neg_matrix[i][j] / total_frequency

    # Identification
    result = []
    for seq_data in test_set:
        total_likelihood = 0
        seq = seq_data[1]
        for i, ch in enumerate(seq):
            if i == len(seq) - 1:
                break
            total_likelihood += math.log(pos_matrix[seq[i]][seq[i + 1]]
                                         / neg_matrix[seq[i]][seq[i + 1]], 2)
        identify_result = total_likelihood / len(seq)
        if identify_result >= threshold:
            result.append((seq_data, True, identify_result))
        else:
            result.append((seq_data, False, identify_result))
    return result, pos_matrix, neg_matrix


def __get_raw_seqs(fasta_seqs):
    raw_seqs = []
    for seq_data in fasta_seqs:
        raw_seqs.append(seq_data[1])
    return raw_seqs
