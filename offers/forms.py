from django.forms import ModelForm
from .models import CategoryOffer

class CategoryOfferForm(ModelForm):
    class Meta:
        model = CategoryOffer
        fields = ["category_name", "discount"]

    def __init__(self, *args, **kwargs):
        super(CategoryOfferForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs["class"] = "form-control"
