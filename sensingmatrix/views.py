import math
from django.shortcuts import render
from BioinformaticsToolkit import utils as my_utils
import operator


def get_page(request):
    return render(request, 'sensingmatrix/page.html')


def algorithm(request):
    # Get necessary data
    method = int(request.POST['method'])
    threshold_pos = int(request.POST['threshold-pos'])
    threshold_neg = int(request.POST['threshold-neg'])
    train_set_pos = my_utils.get_fasta_from_file(request.FILES['train-set-pos'])
    train_set_neg = my_utils.get_fasta_from_file(request.FILES['train-set-neg'])
    test_set = my_utils.get_fasta_from_file(request.FILES['test-set'])

    # Process sequences.
    data = {}
    if method == 0:
        matrix, length, test_results = __normal_sensing_matrix(test_set, train_set_pos, train_set_neg,
                                                               threshold_pos, threshold_neg)
        data['matrix'] = matrix
    else:
        matrices, length, test_results = __probability_sensing_matrix(test_set, train_set_pos,
                                                                      train_set_neg, threshold_pos,
                                                                      threshold_neg)
        data['matrices'] = matrices
    data['length'] = range(1, length + 1)
    data['test_results'] = test_results
    data['method'] = method

    return render(request, 'sensingmatrix/result.html', data)


# Two main algorithms...
def __probability_sensing_matrix(test_set, train_set_pos,
                                 train_set_neg, threshold_pos,
                                 threshold_neg):
    # Process sequences.
    pos_set_cut, neg_set_cut, test_set_cut = __align_sequences(train_set_pos, train_set_neg, test_set)

    # Get two sensing matrices.
    matrices, length = __construct_matrices(pos_set_cut, neg_set_cut)

    # Calculate scores.
    pos_matrix = matrices[0]
    neg_matrix = matrices[1]
    test_results = []

    for seq, raw_seq in zip(test_set_cut, test_set):
        score = __calc_score_probability(pos_matrix, neg_matrix, seq)

        if score <= threshold_neg:
            test_results.append((0, score, raw_seq))
        elif score >= threshold_pos:
            test_results.append((1, score, raw_seq))
        else:
            test_results.append((2, score, raw_seq))

    return matrices, length, test_results


def __normal_sensing_matrix(test_set, train_set_pos, train_set_neg, threshold_pos, threshold_neg):
    # Process sequences.
    pos_set_cut, neg_set_cut, test_set_cut = __align_sequences(train_set_pos, train_set_neg, test_set)

    # Get sensing matrix.
    matrix, length = __construct_matrix(pos_set_cut, neg_set_cut, threshold_pos, threshold_neg)

    # Calculate scores.
    test_results = []

    for seq, raw_seq in zip(test_set_cut, test_set):
        score = __calc_score_normal(matrix, seq)

        if score <= threshold_neg:
            test_results.append((0, score, raw_seq))
        elif score >= threshold_pos:
            test_results.append((1, score, raw_seq))
        else:
            test_results.append((2, score, raw_seq))
    return matrix, length, test_results


# Align sequences by cutting out preserving the common part.
def __align_sequences(train_set_pos, train_set_neg, test_set):
    # Make the first sequence the base seq to calculate offsets.
    base_seq = train_set_pos[0][1]

    # Calculate offsets and endpoints based on base_seq.
    # Only positive set and test set should be calculated with FASTA
    pos_set_processed = []
    for seq in train_set_pos:
        offset = __fasta(base_seq, seq[1])
        end_point = offset + len(seq[1])
        pos_set_processed.append((seq[1], offset, end_point))

    test_set_processed = []
    for seq in test_set:
        offset = __fasta(base_seq, seq[1])
        end_point = offset + len(seq[1])
        test_set_processed.append((seq[1], offset, end_point))

    # Calculate the biggest start point and the smallest end point.
    pos_start_seq = max(pos_set_processed, key=operator.itemgetter(1))
    start_point = pos_start_seq[1]

    pos_end_seq = min(pos_set_processed, key=operator.itemgetter(2))
    end_point = pos_end_seq[2]

    # Cut sequence based on start/end_base_seq.
    pos_set_cut = []
    for seq_tuple in pos_set_processed:
        left = start_point - seq_tuple[1]
        right = len(seq_tuple[0]) - (seq_tuple[2] - end_point)

        # CUT
        pos_set_cut.append(seq_tuple[0][left:right])

    neg_set_cut = []  # Negative sequences can be cut randomly.
    for seq in train_set_neg:
        # CUT
        neg_set_cut.append(seq[1][:end_point - start_point])

    test_set_cut = []
    for seq_tuple in test_set_processed:
        if seq_tuple[1] <= start_point and seq_tuple[2] >= end_point:
            left = start_point - seq_tuple[1]
            right = len(seq_tuple[0]) - (seq_tuple[2] - end_point)
            test_set_cut.append(seq_tuple[0][left:right])
        else:
            # We regard this sequence as nonfunctional.
            test_set_cut.append(seq_tuple[0][:end_point - start_point])

    return pos_set_cut, neg_set_cut, test_set_cut


# Return an offset for seq_2 to seq_1
def __fasta(seq_1, seq_2):
    # Build position table.
    positions_table = {}
    for index, base in enumerate(seq_1):
        if index + 1 > len(seq_1):
            break
        base = seq_1[index:index + 1]
        if base in positions_table:
            positions_table[base].append(index)
        else:
            positions_table[base] = [index]

    offsets_frequency = {}

    # Calculate the offsets.
    for index, base in enumerate(seq_2):
        if index + 1 > len(seq_2):
            break
        offsets_single_tuple = []
        base = seq_2[index:index + 1]
        if base in positions_table:
            for pos in positions_table[base]:
                offset = pos - index
                offsets_single_tuple.append(offset)
                if offset not in offsets_frequency:
                    offsets_frequency[offset] = 1
                else:
                    offsets_frequency[offset] += 1

    # Get the most occurring offset
    for k, v in offsets_frequency.items():
        if v == max(offsets_frequency.values()):
            return k


# Construct matrices
def __construct_matrices(pos_set, neg_set):
    length = len(pos_set[0])

    matrices = []

    # Get two sensing matrices.
    for my_set in (pos_set, neg_set):
        temp_matrix = {x: [0] * length for x in 'actg'}

        # Count frequencies.
        for seq in my_set:
            for index, base in enumerate(seq):
                temp_matrix[base][index] += 1

        # Calculate probability of each base present in some position.
        result_matrix = {x: [0] * length for x in 'actg'}
        for base, frequency_on_positions in temp_matrix.items():
            # Calculate the total frequencies.
            total_frequencies = sum(frequency_on_positions)

            for index, frequency in enumerate(frequency_on_positions):
                if total_frequencies == 0:
                    result_matrix[base][index] = float('{0:.3f}'.format(0))
                else:
                    result_matrix[base][index] = float('{0:.3f}'.format(frequency / total_frequencies))

        matrices.append(result_matrix)

    return matrices, length


def __construct_matrix(pos_set, neg_set, pos_threshold, neg_threshold):
    length = len(pos_set[0])

    matrix = {x: [0] * length for x in 'actg'}

    # Train with positive set
    for seq in pos_set:
        if __calc_score_normal(matrix, seq) >= pos_threshold:
            continue
        for index, base in enumerate(seq):
            matrix[base][index] += 1

    # Train with negative set
    for seq in neg_set:
        if __calc_score_normal(matrix, seq) <= neg_threshold:
            continue
        for index, base in enumerate(seq):
            matrix[base][index] -= 1
    return matrix, length


# Calculate scores
def __calc_score_normal(matrix, seq):
    score = 0
    for index, base in enumerate(seq):
        score += matrix[base][index]
    return score


def __calc_score_probability(pos_matrix, neg_matrix, seq):
    pos_score = 1
    neg_score = 1
    for index, base in enumerate(seq):
        if pos_matrix[base][index] != 0:
            pos_score *= pos_matrix[base][index]
        if neg_matrix[base][index] != 0:
            neg_score *= neg_matrix[base][index]

    return math.log(pos_score / neg_score)
