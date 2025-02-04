from django import forms
from django.forms import ModelForm, ValidationError
from .models import Account, UserProfile


class RegistrationForm(ModelForm):
   password = forms.CharField(widget=forms.PasswordInput(attrs={
      'placeholder' : 'Enter Password',
      'class':'form-control'
   }))
   confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
      'placeholder' : 'Confirm Password'
   }))
   
   class Meta:
      model = Account
      fields = ['first_name','last_name','phone_number','email','password']

   def __init__(self, *args, **kwargs):
      super(RegistrationForm, self).__init__(*args, **kwargs)
      self.fields['first_name'].widget.attrs['placeholder'] = 'Enter First Name' 
      self.fields['last_name'].widget.attrs['placeholder'] = 'Enter Last Name' 
      self.fields['phone_number'].widget.attrs['placeholder'] = 'Enter Phone Number'
      self.fields['email'].widget.attrs['placeholder'] = 'Enter Email Address'
      self.fields['email'].widget.attrs['class'] = 'Enter Email Address'    
      for field in self.fields:
         self.fields[field].widget.attrs['class'] = 'form-control'   
        
   def clean(self):
      cleaned_data = super(RegistrationForm,self).clean()
      password = cleaned_data.get('password')
      confirm_password = cleaned_data.get('confirm_password')
      if password != confirm_password:
        self.add_error('confirm_password', "Password does not match")
      
      email = cleaned_data.get('email')

        # بررسی اینکه آیا ایمیل در میان کاربران فعال وجود دارد
      if Account.objects.filter(email=email, is_active=True).exists():
            raise ValidationError('حساب کاربری با این ایمیل وجود دارد و فعال است.')


      return cleaned_data
   
class UserForm(forms.ModelForm):
   class Meta:
      model = Account
      fields = ['first_name','last_name','phone_number']
   def __init__(self, *args, **kwargs):
      super(UserForm, self).__init__(*args, **kwargs)
      for field in self.fields:
         self.fields[field].widget.attrs['class'] = 'form-control'  

class UserProfileFrom(forms.ModelForm):
   profile_picture = forms.ImageField(required=False,error_messages={'Invalid':{'Images file only'}},widget=forms.FileInput)#get rid of currently image path
   class Meta:
      model = UserProfile
      fields = ['address_line_1','address_line_2','city','state','country','profile_picture']
   def __init__(self, *args, **kwargs):
      super(UserProfileFrom, self).__init__(*args, **kwargs)
      for field in self.fields:
         self.fields[field].widget.attrs['class'] = 'form-control'           
      
   
   
      
       