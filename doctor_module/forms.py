from django import forms
from django.core import validators
from .models import Availability


class RegisterForm(forms.Form):
    username = forms.CharField(
        label='',
        widget=forms.TextInput(attrs={
            'placeholder': 'ایمیل یا شماره تلفن خود را وارد کنید',
            'class': 'form-control'
        }),
        validators=[
            validators.MaxLengthValidator(100),
        ]
    )


class GetCodeForm(forms.Form):
    code = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'کد فعال‌سازی را وارد کنید',
                                      'class': 'form-control'}))


class LoginForm(forms.Form):
    email = forms.EmailField(
        label='ایمیل شما',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'ایمیل',
            'required': ''
        }),
        validators=[
            validators.MaxLengthValidator(100),
            validators.EmailValidator
        ]
    )
    password = forms.CharField(
        label='رمزعبور',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'رمزعبور',
            'required': ''
        }),
        validators=[
            validators.MaxLengthValidator(100)
        ]
    )


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(
        label='ایمیل',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'آدرس ایمیل خود را وارد کنید',
            'required': ''
        }),
        validators=[
            validators.MaxLengthValidator(100),
            validators.EmailValidator
        ]
    )


class SetPasswordForm(forms.Form):
    password = forms.CharField(
        label='کلمه عبور',
        widget=forms.PasswordInput(),
        validators=[
            validators.MaxLengthValidator(100),
        ]
    )
    confirm_password = forms.CharField(
        label='تکرار کلمه عبور',
        widget=forms.PasswordInput(),
        validators=[
            validators.MaxLengthValidator(100),
        ]
    )


class ResetPasswordForm(forms.Form):
    code = forms.CharField(

        label='کلمه عبور',
        widget=forms.PasswordInput(),
        validators=[
            validators.MaxLengthValidator(100),
        ])


class DoctorProfileForm(forms.Form):
    phone_number = forms.CharField(
        label='شماره تماس',
        widget=forms.TextInput(attrs={'placeholder': 'شماره تماس شما',
                                      'class': 'form-control'}),
        validators=[
            validators.MaxLengthValidator(15),
        ],
        required=False,

    )

    bio = forms.CharField(
        label='بیوگرافی شما',
        widget=forms.Textarea(attrs={'placeholder': 'بیوگرافی خود را وارد کنید'
            , 'class': 'form-control'}),
        required=False,
    )
    image_profile = forms.ImageField(
        label='عکس',
        widget=forms.FileInput(attrs={'class': 'hidden-input'}),
        required=False
    )

    # def clean_birth_date(self):
    #     date_str = self.cleaned_data['birth_date']
    #     if date_str:
    #         try:
    #             # تبدیل تاریخ شمسی به میلادی
    #             print(date_str)
    #             jalali_date = JalaliDate.strptime(date_str, '%Y-%m-%d')
    #             gregorian_date = jalali_date.to_gregorian()
    #             return gregorian_date
    #         except ValueError:
    #             raise forms.ValidationError('تاریخ وارد شده معتبر نیست.')
    #     return None


class DoctorChangePasswordForm(forms.Form):
    old_password = forms.CharField(
        label='رمز عبور فعلی',
        widget=forms.PasswordInput(attrs={'placeholder': 'رمز عبور فعلی', 'class': 'form-control'}),
        validators=[
            validators.MaxLengthValidator(100),
        ]
        , required=False,

    )

    new_password1 = forms.CharField(
        label='رمز عبور جدید',
        widget=forms.PasswordInput(attrs={'placeholder': 'رمز عبور جدید', 'class': 'form-control'}),
        validators=[
            validators.MaxLengthValidator(100),
        ],
        required=False,

    )

    new_password2 = forms.CharField(
        label='تکرار رمز عبور جدید',
        widget=forms.PasswordInput(attrs={'placeholder': 'تکرار رمز عبور جدید', 'class': 'form-control'}),
        validators=[
            validators.MaxLengthValidator(100),
        ],
        required=False,

    )


class MoreInformationDoctorForm(forms.Form):
    first_name = forms.CharField(
        label='نام',
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        }),
        validators=[
            validators.MaxLengthValidator(100),
        ],
        required=False,

    )

    last_name = forms.CharField(
        label='نام خانوادگی',
        widget=forms.TextInput(attrs={'placeholder': 'نام خانوادگی شما',
                                      'class': 'form-control'}),
        validators=[
            validators.MaxLengthValidator(100),
        ],
        required=False,

    )

    medical_degree_picture = forms.ImageField(
        label='عکس مدرک پزشکی',
        widget=forms.FileInput(attrs={'class': 'hidden-input'}),
        required=False
    )
    password = forms.CharField(
        label='رمز عبور ',
        widget=forms.PasswordInput(attrs={'placeholder': 'رمز عبور جدید', 'class': 'form-control'}),
        validators=[
            validators.MaxLengthValidator(100),
        ],
        required=False,

    )
    proficiency = forms.CharField(
        label='تخصص',
        widget=forms.TextInput(attrs={'placeholder': 'تخصص',
                                      'class': 'form-control'}),

        required=False,

    )


class AvailabilityForm(forms.ModelForm):

    start_time = forms.TimeField(
        required=False,
        widget=forms.TimeInput(attrs={'type': 'time', 'required': False})
    )
    end_time = forms.TimeField(
        required=False,
        widget=forms.TimeInput(attrs={'type': 'time', 'required': False})
    )

    class Meta:
        model = Availability
        fields = ['start_time', 'end_time']


class ChatForm(forms.Form):
    message = forms.CharField(widget=forms.Textarea(attrs={
        'rows': 2,
        'placeholder': 'پیام خود را بنویسید...'
    }))