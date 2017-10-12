from django.shortcuts import render
from django.http import HttpResponse

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
# import matplotlib.lines as mlines

import io

matplotlib.pyplot.switch_backend('Agg')


# Create your views here.


def get_page(request):
    return render(request, 'boxplot/page.html')


def get_result_page(request):
    string_1 = request.POST['string_1'].upper()
    string_2 = request.POST['string_2'].upper()

    window_size = request.POST['window_size']
    if window_size is not None and window_size != '':
        window_size = int(window_size)
    move_step = request.POST['move_step']
    if move_step is not None and move_step != '':
        move_step = int(move_step)
    stringency = request.POST['stringency']
    if stringency is not None and stringency != '':
        stringency = int(stringency)

    # Use session to store data
    request.session['string_1'] = string_1
    request.session['string_2'] = string_2
    request.session['window_size'] = window_size
    request.session['move_step'] = move_step
    request.session['stringency'] = stringency

    box_plot_graph = [[0 for x in range(len(string_2))] for y in range(len(string_1))]
    align_offset = int((window_size - 1) / 2)
    for index_1 in range(0, len(string_1) - (window_size - 1), move_step):
        for index_2 in range(0, len(string_2) - (window_size - 1), move_step):
            temp_1 = string_1[index_1:index_1 + window_size]
            temp_2 = string_2[index_2:index_2 + window_size]
            if __compare_string(temp_1, temp_2, stringency):
                box_plot_graph[index_1 + align_offset][index_2 + align_offset] = 1
            else:
                box_plot_graph[index_1 + align_offset][index_2 + align_offset] = 0
    request.session['box_plot_graph'] = box_plot_graph

    # Get a list of motifs
    motifs = []
    for index_1 in range(len(string_1)):
        is_motif_found = False

        # Get the max times of iteration.
        motif_length = 0
        if len(string_1) - index_1 <= len(string_2):
            loop_length = len(string_1) - index_1
        else:
            loop_length = len(string_2)

        for offset in range(loop_length):
            if box_plot_graph[index_1 + offset][offset]:
                if not is_motif_found:
                    is_motif_found = True
                motif_length += 1
            else:
                if is_motif_found:
                    temp_str_1 = string_1[
                                 index_1 + offset - motif_length - align_offset:index_1 + offset + align_offset]
                    temp_str_2 = string_2[offset - motif_length - align_offset:offset + align_offset]
                    motifs.append([temp_str_1, temp_str_2])
                    is_motif_found = False
                    motif_length = 0

    for index_2 in range(1, len(string_2)):
        is_motif_found = False

        # Get the max times of iteration.
        motif_length = 0
        if len(string_2) - index_2 <= len(string_1):
            loop_length = len(string_2) - index_2
        else:
            loop_length = len(string_1)

        for offset in range(loop_length):
            if box_plot_graph[offset][index_2 + offset]:
                if not is_motif_found:
                    is_motif_found = True
                motif_length += 1
            else:
                if is_motif_found:
                    temp_str_1 = string_1[offset - motif_length - align_offset:offset + align_offset]
                    temp_str_2 = string_2[
                                 index_2 + offset - motif_length - align_offset:index_2 + offset + align_offset]
                    motifs.append([temp_str_1, temp_str_2])
                    is_motif_found = False
                    motif_length = 0

    # Sort motifs by length.
    motifs.sort(key=lambda item: len(item[0]), reverse=True)
    result = {
        'motifs': motifs,
    }
    return render(request, 'boxplot/result.html', result)


def get_graph(request):
    string_1 = request.session['string_1']
    string_2 = request.session['string_2']
    box_plot_graph = request.session['box_plot_graph']

    # Create plot graph
    string_1_ticks = [x.upper() for x in request.session['string_1']]
    string_2_ticks = [x.upper() for x in string_2]

    buf = io.BytesIO()
    fig = plt.figure()
    for x in range(len(string_1)):
        for y in range(len(string_2)):
            if box_plot_graph[x][y]:
                plt.plot(x, y, '.k')

    # # Draw lines.
    # for index_1 in range(len(box_plot_graph)):
    #     is_line_found = False
    #
    #     # Get the max times of iteration.
    #     line_length = 0
    #     if len(box_plot_graph) - index_1 <= len(box_plot_graph[0]):
    #         loop_length = len(string_1) - index_1
    #     else:
    #         loop_length = len(string_2)
    #
    #     start_point = []
    #     end_point = []
    #     for offset in range(loop_length):
    #         if box_plot_graph[index_1 + offset][offset]:
    #             if not is_line_found:
    #                 is_line_found = True
    #                 start_point.append(index_1)
    #                 start_point.append(index_1 + offset)
    #             line_length += 1
    #         else:
    #             if is_line_found:
    #                 end_point.append(index_1 + offset - 1)
    #                 end_point.append(offset - 1)
    #                 __newline(start_point, end_point)
    #                 is_line_found = False
    #                 line_length = 0

    x = np.array(list(range(len(string_1))))
    y = np.array(list(range(len(string_2))))
    plt.xticks(x, string_1_ticks)
    plt.yticks(y, string_2_ticks)
    fig.savefig(buf, format='png')

    response = HttpResponse(content_type='image/png')
    response.write(buf.getvalue())
    buf.close()

    del request.session['string_1']
    del request.session['string_2']
    del request.session['window_size']
    del request.session['move_step']
    del request.session['stringency']
    del request.session['box_plot_graph']

    return response


def __compare_string(string_1, string_2, stringency):
    mismatch_char = 0
    for char_1, char_2 in zip(string_1, string_2):
        if char_1 != char_2:
            mismatch_char += 1
        if mismatch_char > len(string_1) - stringency:
            return False
    return True


def __newline(p1, p2):
    ax = plt.gca()
    xmin, xmax = ax.get_xbound()

    if(p2[0] == p1[0]):
        xmin = xmax = p1[0]
        ymin, ymax = ax.get_ybound()
    else:
        ymax = p1[1]+(p2[1]-p1[1])/(p2[0]-p1[0])*(xmax-p1[0])
        ymin = p1[1]+(p2[1]-p1[1])/(p2[0]-p1[0])*(xmin-p1[0])

    l = mlines.Line2D([xmin,xmax], [ymin,ymax])
    ax.add_line(l)
    return l
