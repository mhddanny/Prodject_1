from django import forms
from django.forms import inlineformset_factory
from profiles.models import Account, UserProfile
from category.models import Category
from store.models import Product, ProductItem, ProductPaket, ProductGallery, Variation
from django.db.models import Q
from django_ckeditor_5.widgets import CKEditor5Widget
# from warehouse.models import Product

from mptt.forms import TreeNodeChoiceField

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

class UserForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ('first_name', 'last_name', 'phone_number')

    def __init__(self, *args, **kwargs):
        super(UserForm,self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

class UserProfileForm(forms.ModelForm):
    profile_picture = forms.ImageField(required=False, error_messages={ 'invalid':("Image files only") }, widget=forms.FileInput)
    class Meta:
        model = UserProfile
        fields = [ 'address_line_1', 'address_line_2', 'city', 'state', 'country', 'profile_picture', 'postcode' ]

    def __init__(self, *args, **kwargs):
        super(UserProfileForm,self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

class UserCategoryForm(forms.ModelForm):
    parent = TreeNodeChoiceField(
        queryset=Category.objects.all(),
        level_indicator='+--',
        required=False,
        empty_label='None',
        help_text='Select the parent category')
    
    class Meta:
        model = Category
        fields = ['category_name', 'description', 'parent']

    def __init__(self, *args, **kwargs):
        super(UserCategoryForm,self).__init__(*args, **kwargs)
        self.fields["description"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Short Description", "required": "True", "rows":"2","cols":"50" }
        )
       
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
            
class ProductForm(forms.ModelForm):
    category = TreeNodeChoiceField(
        queryset=Category.objects.all(),
        level_indicator='--',
        required=True,
        empty_label='Category',
        help_text='Select the parent category')
    
    long_description = forms.CharField(widget = 
           CKEditor5Widget(config_name='extends',
           attrs={"class": "django_ckeditor_5",
           'row': 50,'cols': 50}),
           required=False)
    
    # is_available = forms.BooleanField(
    #     required=True,
    #     disabled = False,
    #     widget=forms.widgets.CheckboxInput( 
    #         attrs={'class': 'checkbox-inline'}  
    #         ), 
    #     help_text = "I accept the terms in the License Agreement", 
    #     error_messages ={'required':'Please check the box'} 
    # )
    # images = forms.ImageField(required=False, error_messages={ 'invalid':("Image files only") }, widget=forms.FileInput)
    
    class Meta:
        model = Product
        fields = ('name', 'category', 'description', 'long_description')
        
    def __init__(self, *args, **kwargs):
        super(ProductForm,self).__init__(*args, **kwargs)
        self.fields["name"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Name", "required": "True" }
        )
        self.fields["description"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Short Description", "required": "True", "rows":"2","cols":"50" }
        )
        
        # self.fields['is_available'].widget = forms. CheckboxInput(initial=True)
        
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

class ProductItemForm(forms.ModelForm):
    class Meta:
        model = ProductItem
        fields = ('price', 'stock', 'is_available', 'is_default',)

    def __init__(self, *args, **kwargs):
        super(ProductItemForm,self).__init__(*args, **kwargs)
        self.fields["price"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Price", "required": "True", "value": "0"}
        )
        self.fields["stock"].widget.attrs.update(
            {"class": "form-control", "placeholder": "Stock", "required": "True" , "value": "0"}
        )
        self.fields["is_available"].widget.attrs.update(
            {"class": "form-check-input", "type": "checkbox", "value": "True"}
        )
        self.fields["is_default"].widget.attrs.update(
            {"class": "form-check-input", "type": "checkbox", "checked": True, "value": "True"}
        )

class ProductPaketForm(forms.ModelForm):

    class Meta:
        model = ProductPaket
        fields = ('weight', 'length', 'width', 'height',)

    def __init__(self, *args, **kwargs):
        super(ProductPaketForm,self).__init__(*args, **kwargs)
        self.fields["weight"].widget.attrs.update(
            {"class": "form-control", "placeholder": "...gram", "required": "True" }
        )
        self.fields["length"].widget.attrs.update(
            {"class": "form-control", "placeholder": "...cm", "required": "True" }
        )
        self.fields["width"].widget.attrs.update(
            {"class": "form-control", "placeholder": "...cm", "required": "True" }
        )
        self.fields["height"].widget.attrs.update(
            {"class": "form-control", "placeholder": "...cm", "required": "True" }
        )

class ProductGaleryForm(forms.ModelForm):
    image = MultipleFileField()
    
    class Meta:
        model = ProductGallery
        fields = ('image', )

    def __init__(self, *args, **kwargs):
        super(ProductGaleryForm,self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
        
class ProductVariationForm(forms.ModelForm):
    class Meta:
        model = Variation
        fields = ('varian_category', 'variation_value')

ItemPorductformset = inlineformset_factory(
    Product, 
    ProductItem, 
    form=ProductItemForm, 
    extra=0, 
    max_num=10, 
    can_delete=False,
)