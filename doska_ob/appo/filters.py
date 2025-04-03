from django_filters import FilterSet, CharFilter, ModelChoiceFilter
from .models import Advertisement, Category  # Предполагается, что у вас есть модель Category


class AdvertisementFilter(FilterSet):
    title = CharFilter(label="Название объявления", lookup_expr='icontains')
    categories = ModelChoiceFilter(queryset=Category.objects.all(), label="Категория")

    class Meta:
        model = Advertisement
        fields = {
            'title': [],
            'categories': [],
        }
