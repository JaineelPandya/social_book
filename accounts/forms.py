from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, UploadedFile

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    # optional public display name (not the same as username)
    display_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Display name (optional)'})
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'})
    )

    class Meta:
        model = CustomUser
        # if your model doesn't have display_name, remove it from the tuple
        fields = ("email", "display_name", "birth_year", "address", "public_visibility", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if 'display_name' in self.cleaned_data and hasattr(user, 'display_name'):
            user.display_name = self.cleaned_data['display_name']
        if commit:
            user.save()
        return user


class UploadFileForm(forms.ModelForm):
    # (same as Option A - your upload form)
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
        file = self.cleaned_data.get('file')
        if file:
            if file.size > 50 * 1024 * 1024:
                raise forms.ValidationError("File size must not exceed 50MB.")
            allowed_ext = ['pdf', 'jpeg', 'jpg']
            ext = file.name.split('.')[-1].lower()
            if ext not in allowed_ext:
                raise forms.ValidationError("Only PDF and JPEG files are allowed.")
        return file


class ProfileUpdateForm(forms.ModelForm):
    """Form for updating user profile settings including visibility."""
    
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'bio', 'public_visibility', 'birth_year', 'address']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'birth_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'public_visibility': forms.CheckboxInput(attrs={'class': 'custom-control-input'}),
        }
        help_texts = {
            'public_visibility': 'If enabled, your profile and public books will be visible to all users in the Authors section.',
        }
