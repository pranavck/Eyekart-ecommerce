from category.models import Category
from store.models import Product, Variation ,ProductGallery
from django import forms


class AddProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ('product_name','slug','description','category','images','stock','price',)

    def __init__(self, *args, **kwargs):
         super(AddProductForm, self).__init__(*args, **kwargs)
         for field in self.fields:
                self.fields[field].widget.attrs['class'] = 'form-control'

class AddCategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ('category_name','slug')

    def __init__(self, *args, **kwargs):
         super(AddCategoryForm, self).__init__(*args, **kwargs)
         for field in self.fields:
                self.fields[field].widget.attrs['class'] = 'form-control'

class AddVariationForm(forms.ModelForm):
    class Meta:
        model = Variation
        fields = ('product','variation_category','variation_value',)

    def __init__(self, *args, **kwargs):
         super(AddVariationForm, self).__init__(*args, **kwargs)
         for field in self.fields:
                self.fields[field].widget.attrs['class'] = 'form-control'

class ProductGalleryForm(forms.ModelForm):
    class Meta:
        model = ProductGallery
        fields = [
            "product",
            "image",
        ]
        widgets = {
            'product':forms.Select(attrs={'class':'form-control'}),
        }


