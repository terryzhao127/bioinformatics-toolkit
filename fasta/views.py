from django.shortcuts import render

# Create your views here.


def get_page(request):
    return render(request, 'fasta/page.html')


def fasta(request):
    string_1 = request.POST['string_1']
    string_2 = request.POST['string_2']
    k_parameter = request.POST['k_tuple']
    if k_parameter is not None and k_parameter:
        k_parameter = int(k_parameter)

    positions_table = {}

    # Build position table.
    # TODO: Validation
    for index, base in enumerate(string_1):
        if index + k_parameter > len(string_1):
            break
        temp_str = string_1[index:index + k_parameter]
        if temp_str in positions_table:
            positions_table[temp_str].append(index)
        else:
            positions_table[temp_str] = [index]

    offsets_frequency = {}
    offsets_table = []
    # Calculate the offsets.
    for index, base in enumerate(string_2):
        if index + k_parameter > len(string_2):
            break
        offsets_single_tuple = []
        temp_str = string_2[index:index + k_parameter]
        if temp_str in positions_table:
            for pos in positions_table[temp_str]:
                offset = index - pos
                offsets_single_tuple.append(offset)
                if offset not in offsets_frequency:
                    offsets_frequency[offset] = 1
                else:
                    offsets_frequency[offset] += 1
        offsets_table.append([temp_str, offsets_single_tuple])

    # Get the most occurring offset.
    result_offsets = [k for k, v in offsets_frequency.items() if v == max(offsets_frequency.values())]

    # TODO: Get rid of HARD CODE.
    result = {
        'positions_table': positions_table,
        'offsets_table': offsets_table,
        'result_offsets': result_offsets,
        'matched_base_number': k_parameter,
    }

    return render(request, 'fasta/result.html', result)
