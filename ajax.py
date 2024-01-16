from django.http import JsonResponse
from othello.models import History,Storage

def save_history(request):
    History.objects.create(
        code = 'aaaaaaaa',
        black = request.POST.get( 'black' ),
        white = request.POST.get( 'white' ),
    )
    return JsonResponse({},safe=False)

def save_storage(request):
    Storage.objects.all().delete()
    for i in range(8):
        for j in range(8):
            Storage.objects.create(
                code = 'aaaaaaaa',
                square = int(str(i+1)+str(j+1)),
                status = request.POST.get( 'square_' + str(i+1)+str(j+1) ),
            )

def get_storage(request):
    storage_list = list()
    for storage in Storage.objects.order_by('square').all():
        storage_list.append({
            'square' : storage.square,
            'status' : storage.status,
        })

    return JsonResponse( storage_list, safe=False )