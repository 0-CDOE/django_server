# pybo/views/detection_views.py
from .base_views import BaseListView, BaseDetailView, BaseCreateView, BaseUpdateView, BaseDeleteView, BaseVoteView
from ..models import Detection
from ..forms import DetectionForm
from django.urls import reverse_lazy

class DetectionListView(BaseListView):
    model = Detection
    template_name = 'pybo/detection_list.html'
    search_fields = ['subject', 'content', 'author__username']


class DetectionDetailView(BaseDetailView):
    model = Detection
    template_name = 'pybo/detection_detail.html'


class DetectionCreateView(BaseCreateView):
    model = Detection
    form_class = DetectionForm
    success_url = 'pybo:detection_detail'


class DetectionUpdateView(BaseUpdateView):
    model = Detection
    form_class = DetectionForm
    success_url = 'pybo:detection_detail'


class DetectionDeleteView(BaseDeleteView):
    model = Detection
    success_url = 'pybo:detection_list'


class DetectionVoteView(BaseVoteView):
    model = Detection
    success_url = 'pybo:detection_detail'
