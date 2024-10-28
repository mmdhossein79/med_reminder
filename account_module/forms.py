from django import forms
from django.core import validators
from django.core.exceptions import ValidationError
import django_jalali.forms as jforms
from persiantools.jdatetime import JalaliDate

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


class UserProfileForm(forms.Form):

    first_name = forms.CharField(
        label='نام',
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        }),
        validators=[
            validators.MaxLengthValidator(100),
        ],
    required = False,

    )

    last_name = forms.CharField(
        label='نام خانوادگی',
        widget=forms.TextInput(attrs={'placeholder': 'نام خانوادگی شما',
                                      'class':'form-control'}),
        validators=[
            validators.MaxLengthValidator(100),
        ],
    required = False,

    )

    # email = forms.EmailField(
    #     label='ایمیل شما',
    #     widget=forms.EmailInput(attrs={'placeholder': 'ایمیل شما'}),
    #     validators=[
    #         validators.EmailValidator(),
    #         validators.MaxLengthValidator(100),
    #     ]
    # )

    phone_number = forms.CharField(
        label='شماره تماس',
        widget=forms.TextInput(attrs={'placeholder': 'شماره تماس شما',
                                      'class':'form-control'}),
        validators=[
            validators.MaxLengthValidator(15),
        ],
    required = False,

    )

    bio = forms.CharField(
        label='بیوگرافی شما',
        widget=forms.Textarea(attrs={'placeholder': 'بیوگرافی خود را وارد کنید'
                                     ,'class':'form-control'}),
        required=False,
    )
    image_profile = forms.ImageField(
        label= 'عکس',
        widget=forms.FileInput(attrs={'class': 'hidden-input'}),
        required = False
    )

    GENDER_CHOICES = [
        ("-",""),
        ('مرد', 'مرد'),
        ('زن', 'زن'),
    ]

    gender = forms.ChoiceField(
        label='جنسیت',
        choices=GENDER_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control',
        }),
        required=False,
    )
    birth_date = forms.CharField(
        label='تاریخ تولد',
        widget=forms.TextInput(attrs={
            'placeholder': 'روز/ماه/سال',
            'class': 'form-control',
        }),
        required=False,
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


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(
        label='رمز عبور فعلی',
        widget=forms.PasswordInput(attrs={'placeholder': 'رمز عبور فعلی','class':'form-control'}),
        validators=[
            validators.MaxLengthValidator(100),
        ]
,    required = False,

    )

    new_password1 = forms.CharField(
        label='رمز عبور جدید',
        widget=forms.PasswordInput(attrs={'placeholder': 'رمز عبور جدید','class':'form-control'}),
        validators=[
            validators.MaxLengthValidator(100),
        ],
        required = False,

    )

    new_password2 = forms.CharField(
        label='تکرار رمز عبور جدید',
        widget=forms.PasswordInput(attrs={'placeholder': 'تکرار رمز عبور جدید','class':'form-control'}),
        validators=[
            validators.MaxLengthValidator(100),
        ],
    required = False,

    )


class MoreInformationPatientForm(forms.Form):
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

    password = forms.CharField(
        label='رمز عبور ',
        widget=forms.PasswordInput(attrs={'placeholder': 'رمز عبور جدید', 'class': 'form-control'}),
        validators=[
            validators.MaxLengthValidator(100),
        ],
        required=False,

    )
