from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import CustomUser, UploadedFile


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = (
            "email",
            "birth_year",
            "address",
            "public_visibility",
            "password1",
            "password2",
        )


class UploadFileForm(forms.ModelForm):
    """Form for uploading books/files."""
    
    class Meta:
        model = UploadedFile
        fields = ['title', 'description', 'file', 'year_published', 'cost', 'visibility']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Book/File Title',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Description or summary of the book'
            }),
            'file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpeg,.jpg',
                'required': True
            }),
            'year_published': forms.NumberInput(attrs={
                'class': 'form-control',
                'type': 'number',
                'min': '1000',
                'max': '2100',
                'placeholder': 'Year published'
            }),
            'cost': forms.NumberInput(attrs={
                'class': 'form-control',
                'type': 'number',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Cost (0 for free)'
            }),
            'visibility': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
    
    def clean_file(self):
        """Validate file extension and size."""
        file = self.cleaned_data.get('file')
        if file:
            # Check file size (max 50MB)
            if file.size > 50 * 1024 * 1024:
                raise forms.ValidationError("File size must not exceed 50MB.")
            
            # Check file extension
            allowed_ext = ['pdf', 'jpeg', 'jpg']
            ext = file.name.split('.')[-1].lower()
            if ext not in allowed_ext:
                raise forms.ValidationError("Only PDF and JPEG files are allowed.")
        
        return file
