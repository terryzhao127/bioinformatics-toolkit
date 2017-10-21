from django.shortcuts import render

# Create your views here.


def get_page(request):
    return render(request, 'koperation/page.html')


def algorithm(request):
    mode = request.POST['mode']
    mode = int(mode)
    string = request.POST['string']

    num_1 = request.POST['num_1']
    if num_1 is not None and num_1:
        num_1 = int(num_1)

    num_2 = 0
    if mode == 2:
        num_2 = request.POST['num_2']
        if num_2 is not None and num_2:
            num_2 = int(num_2)

    if mode == 0:
        string = string[:num_1]
    elif mode == 1:
        string = string[num_1:]
    elif mode == 2:
        string = string[num_1:num_2]
    return render(request, 'koperation/result.html', dict(result=string))
