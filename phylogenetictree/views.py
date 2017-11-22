from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from Bio import Phylo
import io

from matplotlib import pylab
import matplotlib.pyplot

matplotlib.pyplot.switch_backend('Agg')


def get_page(request):
    return render(request, 'phylogenetictree/page.html')


def result_page(request):
    i = 0
    species_data = []
    while ('name-' + str(i)) in request.POST:
        name = request.POST['name-' + str(i)]
        age = request.POST['age-' + str(i)]
        species_data.append((name, age))
        i += 1
    species_data.sort(key=lambda x: x[1], reverse=True)

    # processed_data = []
    # for i, specie in enumerate(species_data):
    #     if i == len(species_data) - 1:
    #         processed_data.append((species_data[i][0], 0))
    #         break
    #     processed_data.append((specie[0], int(specie[1]) - int(species_data[i + 1][1])))

    # Get tree string
    tree_string = ''
    for index, specie in enumerate(species_data):
        # Add middle terms.
        if index != 0:
            if index == len(species_data) - 1:
                tree_string += ', ' + specie[0] + ':' + str(specie[1])
            else:
                tree_string += ', (' + specie[0] + ':' + str(specie[1])
        else:
            tree_string += '(' + specie[0] + ':' + str(specie[1])

        # Add last parentheses.
        if index == len(species_data) - 1:
            if len(species_data) == 1:
                tree_string += ')'
            else:
                for i in range(1, len(species_data)):
                    tree_string += ')'
    request.session['tree_string'] = tree_string
    return render(request, 'phylogenetictree/result.html')


def get_tree(request):
    tree_string = request.session['tree_string']
    string_io = io.StringIO(tree_string)
    tree = Phylo.read(string_io, 'newick')
    Phylo.draw(tree, do_show=False)

    buf = io.BytesIO()
    pylab.savefig(buf, format='png')
    response = HttpResponse(content_type='image/png')
    response.write(buf.getvalue())
    buf.close()
    return response
