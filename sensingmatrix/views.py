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
    pos_set_cut, neg_set_cut, test_set_cut = __align_sequences(train_set_pos, train_set_neg, test_set)

    # Get Constructed Matrix
    constructed_matrix = __construct_matrix(pos_set_cut, neg_set_cut, threshold_pos, threshold_neg)

    # Calculate scores
    result_scores = []

    for seq, raw in zip(test_set_cut, test_set):
        score = __calc_score(constructed_matrix, seq)

        if score <= threshold_neg:
            result_scores.append((0, score, raw))
        elif score >= threshold_pos:
            result_scores.append((1, score, raw))
        else:
            result_scores.append((2, score, raw))

    result = {
        'scores': result_scores,
    }

    return render(request, 'sensingmatrix/result.html', result)


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


def __construct_matrix(pos_set, neg_set, pos_threshold, neg_threshold):
    length = len(pos_set[0])

    constructed_matrix = {x: [0 for i in range(length)] for x in 'actg'}

    # Train with positive set
    for seq in pos_set:
        if __calc_score(constructed_matrix, seq) >= pos_threshold:
            continue
        for index, base in enumerate(seq):
            constructed_matrix[base][index] += 1

    # Train with negative set
    for seq in neg_set:
        if __calc_score(constructed_matrix, seq) <= neg_threshold:
            continue
        for index, base in enumerate(seq):
            constructed_matrix[base][index] -= 1
    return constructed_matrix


def __calc_score(matrix, seq):
    score = 0
    for index, base in enumerate(seq):
        score += matrix[base][index]
    return score
