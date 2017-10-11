from django.shortcuts import render
from django.http import HttpResponse

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import io

# Create your views here.


def get_page(request):
    return render(request, 'boxplot/page.html')


def get_result_page(request):
    string_1 = request.POST['string_1']
    string_2 = request.POST['string_2']

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

    return render(request, 'boxplot/result.html')


def box_plot_graph(request):
    string_1 = request.session['string_1']
    string_2 = request.session['string_2']

    window_size = request.session['window_size']
    if window_size is not None and window_size != '':
        window_size = int(window_size)
    move_step = request.session['move_step']
    if move_step is not None and move_step != '':
        move_step = int(move_step)
    stringency = request.session['stringency']
    if stringency is not None and stringency != '':
        stringency = int(stringency)

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

    # Create plot graph
    string_1_ticks = [x.upper() for x in string_1]
    string_2_ticks = [x.upper() for x in string_2]

    buf = io.BytesIO()
    fig = plt.figure()
    for x in range(len(string_1)):
        for y in range(len(string_2)):
            if box_plot_graph[x][y]:
                plt.plot(x, y, '.k')
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

    return response


def __compare_string(string_1, string_2, stringency):
    mismatch_char = 0
    for char_1, char_2 in zip(string_1, string_2):
        if char_1 != char_2:
            mismatch_char += 1
        if mismatch_char > len(string_1) - stringency:
            return False
    return True
