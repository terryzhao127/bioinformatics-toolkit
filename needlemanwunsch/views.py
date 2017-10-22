from django.shortcuts import render
from enum import Enum

# Create your views here.

# Define the scores of each alignment result.
BLOSUM_62 = {
    's': {'s': 4, 'k': 0, 'q': 0, 'l': -2, '*': -4, 'h': -1, 'g': 0, 't': 1, 'p': -1, 'f': -2, 'b': 0, 'y': -2, 'm': -1,
          'w': -3, 'e': 0, 'z': 0, 'd': 0, 'i': -2, 'a': 1, 'c': -1, 'r': -1, 'n': 1, 'x': 0, 'v': -2},
    'k': {'s': 0, 'k': 5, 'q': 1, 'l': -2, '*': -4, 'h': -1, 'g': -2, 't': -1, 'p': -1, 'f': -3, 'b': 0, 'y': -2,
          'm': -1, 'w': -3, 'e': 1, 'z': 1, 'd': -1, 'i': -3, 'a': -1, 'c': -3, 'r': 2, 'n': 0, 'x': -1, 'v': -2},
    'q': {'s': 0, 'k': 1, 'q': 5, 'l': -2, '*': -4, 'h': 0, 'g': -2, 't': -1, 'p': -1, 'f': -3, 'b': 0, 'y': -1, 'm': 0,
          'w': -2, 'e': 2, 'z': 3, 'd': 0, 'i': -3, 'a': -1, 'c': -3, 'r': 1, 'n': 0, 'x': -1, 'v': -2},
    'l': {'s': -2, 'k': -2, 'q': -2, 'l': 4, '*': -4, 'h': -3, 'g': -4, 't': -1, 'p': -3, 'f': 0, 'b': -4, 'y': -1,
          'm': 2, 'w': -2, 'e': -3, 'z': -3, 'd': -4, 'i': 2, 'a': -1, 'c': -1, 'r': -2, 'n': -3, 'x': -1, 'v': 1},
    '*': {'s': -4, 'k': -4, 'q': -4, 'l': -4, '*': 1, 'h': -4, 'g': -4, 't': -4, 'p': -4, 'f': -4, 'b': -4, 'y': -4,
          'm': -4, 'w': -4, 'e': -4, 'z': -4, 'd': -4, 'i': -4, 'a': -4, 'c': -4, 'r': -4, 'n': -4, 'x': -4, 'v': -4},
    'h': {'s': -1, 'k': -1, 'q': 0, 'l': -3, '*': -4, 'h': 8, 'g': -2, 't': -2, 'p': -2, 'f': -1, 'b': 0, 'y': 2,
          'm': -2, 'w': -2, 'e': 0, 'z': 0, 'd': -1, 'i': -3, 'a': -2, 'c': -3, 'r': 0, 'n': 1, 'x': -1, 'v': -3},
    'g': {'s': 0, 'k': -2, 'q': -2, 'l': -4, '*': -4, 'h': -2, 'g': 6, 't': -2, 'p': -2, 'f': -3, 'b': -1, 'y': -3,
          'm': -3, 'w': -2, 'e': -2, 'z': -2, 'd': -1, 'i': -4, 'a': 0, 'c': -3, 'r': -2, 'n': 0, 'x': -1, 'v': -3},
    't': {'s': 1, 'k': -1, 'q': -1, 'l': -1, '*': -4, 'h': -2, 'g': -2, 't': 5, 'p': -1, 'f': -2, 'b': -1, 'y': -2,
          'm': -1, 'w': -2, 'e': -1, 'z': -1, 'd': -1, 'i': -1, 'a': 0, 'c': -1, 'r': -1, 'n': 0, 'x': 0, 'v': 0},
    'p': {'s': -1, 'k': -1, 'q': -1, 'l': -3, '*': -4, 'h': -2, 'g': -2, 't': -1, 'p': 7, 'f': -4, 'b': -2, 'y': -3,
          'm': -2, 'w': -4, 'e': -1, 'z': -1, 'd': -1, 'i': -3, 'a': -1, 'c': -3, 'r': -2, 'n': -2, 'x': -2, 'v': -2},
    'f': {'s': -2, 'k': -3, 'q': -3, 'l': 0, '*': -4, 'h': -1, 'g': -3, 't': -2, 'p': -4, 'f': 6, 'b': -3, 'y': 3,
          'm': 0, 'w': 1, 'e': -3, 'z': -3, 'd': -3, 'i': 0, 'a': -2, 'c': -2, 'r': -3, 'n': -3, 'x': -1, 'v': -1},
    'b': {'s': 0, 'k': 0, 'q': 0, 'l': -4, '*': -4, 'h': 0, 'g': -1, 't': -1, 'p': -2, 'f': -3, 'b': 4, 'y': -3,
          'm': -3, 'w': -4, 'e': 1, 'z': 1, 'd': 4, 'i': -3, 'a': -2, 'c': -3, 'r': -1, 'n': 3, 'x': -1, 'v': -3},
    'y': {'s': -2, 'k': -2, 'q': -1, 'l': -1, '*': -4, 'h': 2, 'g': -3, 't': -2, 'p': -3, 'f': 3, 'b': -3, 'y': 7,
          'm': -1, 'w': 2, 'e': -2, 'z': -2, 'd': -3, 'i': -1, 'a': -2, 'c': -2, 'r': -2, 'n': -2, 'x': -1, 'v': -1},
    'm': {'s': -1, 'k': -1, 'q': 0, 'l': 2, '*': -4, 'h': -2, 'g': -3, 't': -1, 'p': -2, 'f': 0, 'b': -3, 'y': -1,
          'm': 5, 'w': -1, 'e': -2, 'z': -1, 'd': -3, 'i': 1, 'a': -1, 'c': -1, 'r': -1, 'n': -2, 'x': -1, 'v': 1},
    'w': {'s': -3, 'k': -3, 'q': -2, 'l': -2, '*': -4, 'h': -2, 'g': -2, 't': -2, 'p': -4, 'f': 1, 'b': -4, 'y': 2,
          'm': -1, 'w': 11, 'e': -3, 'z': -3, 'd': -4, 'i': -3, 'a': -3, 'c': -2, 'r': -3, 'n': -4, 'x': -2, 'v': -3},
    'e': {'s': 0, 'k': 1, 'q': 2, 'l': -3, '*': -4, 'h': 0, 'g': -2, 't': -1, 'p': -1, 'f': -3, 'b': 1, 'y': -2,
          'm': -2, 'w': -3, 'e': 5, 'z': 4, 'd': 2, 'i': -3, 'a': -1, 'c': -4, 'r': 0, 'n': 0, 'x': -1, 'v': -2},
    'z': {'s': 0, 'k': 1, 'q': 3, 'l': -3, '*': -4, 'h': 0, 'g': -2, 't': -1, 'p': -1, 'f': -3, 'b': 1, 'y': -2,
          'm': -1, 'w': -3, 'e': 4, 'z': 4, 'd': 1, 'i': -3, 'a': -1, 'c': -3, 'r': 0, 'n': 0, 'x': -1, 'v': -2},
    'd': {'s': 0, 'k': -1, 'q': 0, 'l': -4, '*': -4, 'h': -1, 'g': -1, 't': -1, 'p': -1, 'f': -3, 'b': 4, 'y': -3,
          'm': -3, 'w': -4, 'e': 2, 'z': 1, 'd': 6, 'i': -3, 'a': -2, 'c': -3, 'r': -2, 'n': 1, 'x': -1, 'v': -3},
    'i': {'s': -2, 'k': -3, 'q': -3, 'l': 2, '*': -4, 'h': -3, 'g': -4, 't': -1, 'p': -3, 'f': 0, 'b': -3, 'y': -1,
          'm': 1, 'w': -3, 'e': -3, 'z': -3, 'd': -3, 'i': 4, 'a': -1, 'c': -1, 'r': -3, 'n': -3, 'x': -1, 'v': 3},
    'a': {'s': 1, 'k': -1, 'q': -1, 'l': -1, '*': -4, 'h': -2, 'g': 0, 't': 0, 'p': -1, 'f': -2, 'b': -2, 'y': -2,
          'm': -1, 'w': -3, 'e': -1, 'z': -1, 'd': -2, 'i': -1, 'a': 4, 'c': 0, 'r': -1, 'n': -2, 'x': 0, 'v': 0},
    'c': {'s': -1, 'k': -3, 'q': -3, 'l': -1, '*': -4, 'h': -3, 'g': -3, 't': -1, 'p': -3, 'f': -2, 'b': -3, 'y': -2,
          'm': -1, 'w': -2, 'e': -4, 'z': -3, 'd': -3, 'i': -1, 'a': 0, 'c': 9, 'r': -3, 'n': -3, 'x': -2, 'v': -1},
    'r': {'s': -1, 'k': 2, 'q': 1, 'l': -2, '*': -4, 'h': 0, 'g': -2, 't': -1, 'p': -2, 'f': -3, 'b': -1, 'y': -2,
          'm': -1, 'w': -3, 'e': 0, 'z': 0, 'd': -2, 'i': -3, 'a': -1, 'c': -3, 'r': 5, 'n': 0, 'x': -1, 'v': -3},
    'n': {'s': 1, 'k': 0, 'q': 0, 'l': -3, '*': -4, 'h': 1, 'g': 0, 't': 0, 'p': -2, 'f': -3, 'b': 3, 'y': -2, 'm': -2,
          'w': -4, 'e': 0, 'z': 0, 'd': 1, 'i': -3, 'a': -2, 'c': -3, 'r': 0, 'n': 6, 'x': -1, 'v': -3},
    'x': {'s': 0, 'k': -1, 'q': -1, 'l': -1, '*': -4, 'h': -1, 'g': -1, 't': 0, 'p': -2, 'f': -1, 'b': -1, 'y': -1,
          'm': -1, 'w': -2, 'e': -1, 'z': -1, 'd': -1, 'i': -1, 'a': 0, 'c': -2, 'r': -1, 'n': -1, 'x': -1, 'v': -1},
    'v': {'s': -2, 'k': -2, 'q': -2, 'l': 1, '*': -4, 'h': -3, 'g': -3, 't': 0, 'p': -2, 'f': -1, 'b': -3, 'y': -1,
          'm': 1, 'w': -3, 'e': -2, 'z': -2, 'd': -3, 'i': 3, 'a': 0, 'c': -1, 'r': -3, 'n': -3, 'x': -1, 'v': 4}}
ALIGN_GAP = -4


class __AlignType(Enum):
    MATCH = 1
    MISMATCH = 2
    GAP = 3


def get_page(request):
    return render(request, 'needlemanwunsch/page.html')


def algorithm(request):
    string_1 = request.POST['string_1']
    string_2 = request.POST['string_2']
    score_matrix = [[None] * (len(string_1) + 1) for i in range(len(string_2) + 1)]

    # Initialize the first element with 0.
    score_matrix[0][0] = 0

    # Initialize the first row.
    for i in range(1, len(score_matrix[0])):
        score_matrix[0][i] = score_matrix[0][i - 1] + ALIGN_GAP

    # Initialize the first column.
    for i in range(1, len(score_matrix)):
        score_matrix[i][0] = score_matrix[i - 1][0] + ALIGN_GAP

    # Calculate the score matrix.
    for row in range(1, len(score_matrix)):
        for col in range(1, len(score_matrix[row])):
            char_1 = string_2[row - 1]
            char_2 = string_1[col - 1]
            match_score = BLOSUM_62[string_2[row - 1]][string_1[col - 1]] + score_matrix[row - 1][col - 1]
            gap_from_above = score_matrix[row - 1][col] + ALIGN_GAP
            gap_from_left = score_matrix[row][col - 1] + ALIGN_GAP
            score_matrix[row][col] = max(match_score, gap_from_above, gap_from_left)

    # Traceback to find the best alignment (using DFS).
    colored_matrix = [[(col, False) for col in row] for row in score_matrix]
    paths_queue = [((len(string_2), len(string_1)), '', '')]
    alignments = []
    colored_matrix[len(string_2)][len(string_1)] = (colored_matrix[len(string_2)][len(string_1)][0], True)
    while True:
        if len(paths_queue) == 0:
            break
        temp_align_point = paths_queue.pop(0)
        temp_string_1 = temp_align_point[1]
        temp_string_2 = temp_align_point[2]
        temp_pos = temp_align_point[0]

        # End
        if temp_pos == (0, 0):
            alignment = (temp_string_1, temp_string_2)
            alignments.append(alignment)
            continue

        # Three cases:
        row, col = temp_pos
        if row - 1 >= 0 and score_matrix[row - 1][col] == score_matrix[row][col] - ALIGN_GAP:
            colored_matrix[row - 1][col] = (colored_matrix[row - 1][col][0], True)
            new_string_1 = '-' + temp_string_1
            new_string_2 = string_2[row - 1] + temp_string_2
            new_pos = temp_pos[0] - 1, temp_pos[1]
            new_align_point = (new_pos, new_string_1, new_string_2)
            paths_queue.append(new_align_point)
        if col - 1 >= 0 and score_matrix[row][col - 1] == score_matrix[row][col] - ALIGN_GAP:
            colored_matrix[row][col - 1] = (colored_matrix[row][col - 1][0], True)
            new_string_1 = string_1[col - 1] + temp_string_1
            new_string_2 = '-' + temp_string_2
            new_pos = temp_pos[0], temp_pos[1] - 1
            new_align_point = (new_pos, new_string_1, new_string_2)
            paths_queue.append(new_align_point)
        if row - 1 >= 0 and col - 1 >= 0 and score_matrix[row - 1][col - 1] == score_matrix[row][col] - \
                BLOSUM_62[string_2[row - 1]][string_1[col - 1]]:
            colored_matrix[row - 1][col - 1] = (colored_matrix[row - 1][col - 1][0], True)
            new_string_1 = string_1[col - 1] + temp_string_1
            new_string_2 = string_2[row - 1] + temp_string_2
            new_pos = temp_pos[0] - 1, temp_pos[1] - 1
            new_align_point = (new_pos, new_string_1, new_string_2)
            paths_queue.append(new_align_point)

    # Color alignments.
    colored_alignments = []
    for alignment in alignments:
        colored_alignment = []
        for ch1, ch2 in zip(alignment[0], alignment[1]):
            if ch1 == ch2:
                colored_alignment.append((ch1, ch2, __AlignType.MATCH))
            elif ch1 == '-' or ch2 == '-':
                colored_alignment.append((ch1, ch2, __AlignType.GAP))
            else:
                colored_alignment.append((ch1, ch2, __AlignType.MISMATCH))
        colored_alignments.append(colored_alignment)

    # Procession for django template.
    string_1 = '*' + string_1
    string_2 = '*' + string_2
    processed_matrix = []
    for row, ch in zip(colored_matrix, string_2):
        temp = row[:]
        temp.insert(0, ch)
        processed_matrix.append(tuple(temp))
    result = {
        'string_1': string_1,
        'string_2': string_2,
        'processed_matrix': processed_matrix,
        'colored_alignments': colored_alignments
    }

    return render(request, 'needlemanwunsch/result.html', result)
