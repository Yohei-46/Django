from django.db.models import F
from django.shortcuts import render
from django.views.generic import View
from othello.models import History

class IndexView(View):
    template_name = 'othello.html'

    def get(self, request, **kwargs):

        history = History.objects.order_by('-created_at').all()
        history_count = History.objects.order_by('-created_at').count()
        black_count = History.objects.filter(black__gt=F('white')).order_by('-created_at').count()
        white_count = History.objects.filter(black__lt=F('white')).order_by('-created_at').count()
        draw_count = History.objects.filter(black=F('white')).order_by('-created_at').count()


        black_per = 0
        white_per = 0
        if history_count != 0:
            black_per = round(black_count / (history_count - draw_count) * 100)
            white_per = round(white_count / (history_count - draw_count) * 100)

        data = {
            'history': history,
            'black_per': black_per,
            'white_per': white_per,
            'test': 'test',
        }

        return render(self.request, self.template_name, data)