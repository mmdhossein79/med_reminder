# views.py
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.http import HttpResponse, JsonResponse
from account_module.forms import RegisterForm, GetCodeForm, LoginForm, ForgotPasswordForm, ResetPasswordForm, \
    SetPasswordForm, UserProfileForm, ChangePasswordForm, MoreInformationPatientForm
from account_module.models import Users
from account_module.utility import get_random_number, is_valid_email, send_sms_param, check_valid_birth_date, \
    calculate_age, convert_gregorian_to_jalali, DAYS_TRANSLATION
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from account_module.email_service import send_email
from iran_mobile_va import mobile
from django.http import Http404, HttpRequest
from django.contrib.auth import authenticate, login, logout
from khayyam import JalaliDate
from django.conf import settings
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth import update_session_auth_hash
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.core.files import File

from doctor_module.forms import ChatForm
from doctor_module.models import ChatMessage, Doctors
from reminder_module.models import MedicineReminder, ReserveDoctor


class RegisterView(View):
    def get(self, request):
        register_form = RegisterForm()
        context = {
            'register_form': register_form
        }
        return render(request, 'account_module/register.html', context)

    def post(self, request):
        register_form = RegisterForm(request.POST)

        if register_form.is_valid():
            username = register_form.cleaned_data.get('username')
            if is_valid_email(username):
                try:
                    validate_email(username)
                    user_exists = Users.objects.filter(email__iexact=username).exists()
                    if user_exists:
                        register_form.add_error('username', 'ایمیل وارد شده تکراری می‌باشد')
                    else:
                        new_user = Users(
                            email=username,
                            email_code=get_random_number()
                        )
                        new_user.save()
                        send_email('یک نامه از طرف داروخانه', new_user.email, {'user': new_user},
                                   'activate_account.html')
                        return redirect('get_code', username=username)
                except ValidationError:
                    register_form.add_error('username', 'ایمیل وارد شده معتبر نمی‌باشد')
            else:
                if mobile.is_valid("0" + username if username[0] != "0" else username):
                    user_exists = Users.objects.filter(email__iexact=username).exists()
                    if user_exists:
                        register_form.add_error('username', 'شماره وارد شده تکراری می‌باشد')
                    else:
                        new_user = Users(
                            phone_number=username,
                            phone_number_sms=get_random_number(),
                            role='patient'
                        )
                        new_user.save()
                        send_sms_param(str(new_user.phone_number_sms), new_user.phone_number, app="drugstor")
                        return redirect('get_code', username=username)

        context = {
            'register_form': register_form
        }
        return render(request, 'account_module/register.html', context)


class GetCodeView(View):
    def get(self, request, username):
        code_form = GetCodeForm()
        context = {
            'code_form': code_form,
            'username': username
        }
        return render(request, 'account_module/get_code.html', context)

    def post(self, request, username):
        code_form = GetCodeForm(request.POST)
        if code_form.is_valid():
            code = code_form.cleaned_data.get('code')
            try:
                user = Users.objects.get(email__iexact=username)
                if code.isdigit() and user.email_code.isdigit() and code == user.email_code:
                    login(request, user)

                    return redirect('more_information_patient')
                else:
                    code_form.add_error('code', 'کلمه عبور اشتباه است')
            except Users.DoesNotExist:
                code_form.add_error('code', 'کاربری وجود ندارد')

        context = {
            'code_form': code_form,
            'username': username
        }
        return render(request, 'account_module/get_code.html', context)


class LoginView(View):
    def get(self, request):
        login_form = LoginForm()
        context = {
            'login_form': login_form
        }

        return render(request, 'account_module/login.html', context)

    def post(self, request: HttpRequest):
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            user_email = login_form.cleaned_data.get('email')
            user_pass = login_form.cleaned_data.get('password')
            user: Users = Users.objects.filter(email__iexact=user_email).first()
            if user is not None and user.role == "patient":
                is_password_correct = user.check_password(user_pass)
                if is_password_correct:
                    login(request, user)  # لاگین کاربر

                    next_url = request.GET.get('next', 'patient_dashboard')

                    return redirect(next_url)
                else:
                    login_form.add_error('email', 'کلمه عبور اشتباه است')
            else:
                login_form.add_error('email', 'کاربری با مشخصات وارد شده یافت نشد')

        context = {
            'login_form': login_form
        }

        return render(request, 'account_module/login.html', context)


class ForgetPasswordView(View):
    def get(self, request: HttpRequest):
        forget_pass_form = ForgotPasswordForm()
        # reset_pass_form = ResetPasswordForm()
        context = {
            'forget_pass_form': forget_pass_form,
            # 'reset_code_form': reset_pass_form,
            'email_sent': False  # وضعیت ارسال ایمیل
        }
        return render(request, 'account_module/forgot_password.html', context)

    def post(self, request: HttpRequest):
        forget_pass_form = ForgotPasswordForm(request.POST)

        if 'email' in request.POST:
            if forget_pass_form.is_valid():
                user_email = forget_pass_form.cleaned_data.get('email')
                user: Users = Users.objects.filter(email__iexact=user_email).first()
                if user is not None and user.role == "patient":
                    user.email_code = get_random_number()
                    user.save()
                    send_email('بازیابی کلمه عبور', user.email, {'user': user}, 'forgot_code_temp.html')

                    return redirect('verify_reset_code', email=user_email)
                else:
                    forget_pass_form.add_error('email', 'کاربری با این ایمیل وجود ندارد.')

        context = {
            'forget_pass_form': forget_pass_form,
            # 'reset_code_form': reset_pass_form,
            'email_sent': False  # اگر ایمیل ارسال نشده باشد
        }
        return render(request, 'account_module/forgot_password.html', context)


class VerifyResetCodeView(View):
    def get(self, request, email):
        form = ResetPasswordForm()
        context = {
            'reset_code_form': form,
            'email': email
        }
        return render(request, 'account_module/verify_reset_code.html', context)

    def post(self, request, email):
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data.get('code')
            user = Users.objects.filter(email__iexact=email).first()
            if user and code.isdigit() and user.email_code.isdigit() and code == user.email_code and user.role == "patient":
                return redirect('set_new_password', email=email)
            else:
                form.add_error('code', 'کد وارد شده صحیح نیست.')
        context = {
            'reset_code_form': form,
            'email': email
        }
        return render(request, 'account_module/verify_reset_code.html', context)


class SetNewPasswordView(View):
    def get(self, request, email):
        form = SetPasswordForm()
        context = {
            'set_pass_form': form,
            'email': email
        }
        return render(request, 'account_module/set_pass.html', context)

    def post(self, request, email):
        form = SetPasswordForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data.get('password')
            confirm_password = form.cleaned_data.get('confirm_password')
            user = Users.objects.filter(email__iexact=email).first()
            if user is not None and user.role == "patient":
                if password == confirm_password:
                    user.set_password(password)
                    user.save()
                    return redirect('reset_password_success')
                else:
                    form.add_error('confirm_password', 'اعداد وارد شده یکی نیست')
            else:
                form.add_error('password', 'یوزر یافت نشد')
        context = {
            'set_pass_form': form,
            'email': email
        }
        return render(request, 'account_module/set_pass.html', context)


def reset_password_success(request):
    return render(request, 'account_module/success_message.html')


# @method_decorator(login_required, name='dispatch')
class PatientDashboardView(View):
    def get(self, request, recipient_id=None):
        users = request.user
        if users.is_authenticated:
            today = timezone.now().date()
            week_ago = today - timedelta(days=7)
            reserve = ReserveDoctor.objects.filter(user__email__iexact=users, created_at__gt=week_ago).order_by(
                '-created_at')
            unique_doctors = set(r.doctor for r in reserve)
            for r in reserve:
                r.date = DAYS_TRANSLATION.get(r.date, r.date)
            user_info = Users.objects.filter(email__iexact=users).first()
            med = MedicineReminder.objects.filter(user__email__iexact=users.email).order_by('-create_date')
            name = user_info.first_name if user_info.first_name else "-"
            last_name = user_info.last_name if user_info.last_name else "-"
            phone_number = user_info.phone_number if user_info.phone_number else "-"
            gender = user_info.gender if user_info.gender else "-"
            age = calculate_age(users.birth_date) if users.birth_date else "-"
            birth_date = convert_gregorian_to_jalali(users.birth_date) if users.birth_date else "-"

            for reminder in med:
                reminder.next_dose = self.calculate_next_dose(reminder)
                reminder.stopped_duration = self.calculate_stopped_duration(reminder)
            return render(request, 'account_module/patient_dashboard.html', {'med_form': med
                , 'user_info': user_info, 'name': name, 'last_name': last_name, "phone_number": phone_number,
                                                                             'gender': gender, 'age': age,
                                                                             'birth_date': birth_date
                , 'reserve': reserve,

                                                                             'unique_doctors': unique_doctors
                                                                             })
        else:
            return redirect('login')

    def calculate_next_dose(self, reminder):
        if reminder.stopped_by_datetime:
            now = timezone.now()
            if reminder.stopped_by_datetime > now:
                if reminder.periodic_interval == 'روزانه':
                    interval = timedelta(minutes=(1440 // reminder.dosage_frequency))
                elif reminder.periodic_interval == 'هفتگی':
                    interval = timedelta(minutes=(10080 // reminder.dosage_frequency))  # 168 ساعت * 60 دقیقه
                elif reminder.periodic_interval == 'ماهانه':
                    interval = timedelta(minutes=(43200 // reminder.dosage_frequency))  # 720 ساعت * 60 دقیقه
                else:
                    interval = timedelta(days=1)  # پیش‌فرض به روزانه اگر مشخص نشده باشد

                next_dose_time = reminder.first_time_of_intake + interval

                now = timezone.now()
                time_until_next_dose = next_dose_time - now

                while time_until_next_dose.total_seconds() < 0:
                    next_dose_time += interval
                    time_until_next_dose = next_dose_time - now

                total_seconds = int(time_until_next_dose.total_seconds())
                months, remainder = divmod(total_seconds, 2592000)  # ماه ها (30 روز * 24 ساعت * 60 دقیقه * 60 ثانیه)
                days, remainder = divmod(remainder, 86400)  # روزها (24 ساعت * 60 دقیقه * 60 ثانیه)
                hours, remainder = divmod(remainder, 3600)  # ساعت‌ها (60 دقیقه * 60 ثانیه)
                minutes, seconds = divmod(remainder, 60)  # دقیقه‌ها
                formatted_next_dose = f"{months} ماه، {days} روز، {hours} ساعت، {minutes}، دقیقه{seconds} ثانیه، "
            else:
                formatted_next_dose = "زمان آن گذشته است"
        else:
            formatted_next_dose = "زمان نهایی را وارد نکردین"
        return formatted_next_dose

    def calculate_stopped_duration(self, reminder):
        if reminder.stopped_by_datetime:
            now = timezone.now()
            if reminder.stopped_by_datetime > now:
                stopped_duration = reminder.stopped_by_datetime - now  # زمان سپری شده از توقف

                # اختلاف زمان را محاسبه کنید
                total_seconds = int(stopped_duration.total_seconds())

                # تبدیل زمان به ماه، روز، ساعت، دقیقه و ثانیه
                days, seconds = divmod(total_seconds, 86400)
                months, days = divmod(days, 30)  # به طور تقریبی هر ماه 30 روز در نظر گرفته می‌شود.
                hours, seconds = divmod(seconds, 3600)
                minutes, seconds = divmod(seconds, 60)

                # فرمت کردن خروجی
                formatted_stopped_duration = f"{months} ماه {days} روز {hours} ساعت {minutes} دقیقه {seconds} ثانیه"

                return formatted_stopped_duration
            else:
                return "زمان آن گذشته است"

        return None


@method_decorator(login_required, name='dispatch')
class UserProfileView(View):
    def get(self, request):
        profile_form = UserProfileForm()
        change_password_form = ChangePasswordForm()
        user = Users.objects.filter(email__iexact=request.user).first()
        age = calculate_age(user.birth_date) if user.birth_date else "-"
        phone = user.phone_number if user.phone_number else "-"
        birth_date = convert_gregorian_to_jalali(user.birth_date) if user.birth_date else "-"
        gender = user.gender if user.gender else "-"
        context = {
            'profile_form': profile_form,
            'change_password_form': change_password_form,
            'show_profile': user,
            'age': age,
            'phone': phone,
            'birth_date': birth_date,
            'gender': gender
        }
        return render(request, 'account_module/profile_view_patient.html', context)

    def post(self, request):
        profile_form = UserProfileForm(request.POST, request.FILES)
        change_password_form = ChangePasswordForm(request.POST)
        if profile_form.is_valid():
            user: Users = Users.objects.filter(email__iexact=request.user).first()
            if profile_form.cleaned_data.get('first_name'):
                user.first_name = profile_form.cleaned_data.get('first_name')
            if profile_form.cleaned_data.get('last_name'):
                user.last_name = profile_form.cleaned_data.get('last_name')
            if profile_form.cleaned_data.get('phone_number'):
                user.phone_number = profile_form.cleaned_data.get('phone_number')
            if profile_form.cleaned_data.get('bio'):
                user.bio = profile_form.cleaned_data.get('bio')
            if profile_form.cleaned_data.get('image_profile'):
                user.profile_picture = profile_form.cleaned_data.get('image_profile')

            if profile_form.cleaned_data.get('gender'):
                user.gender = profile_form.cleaned_data.get('gender')
            if profile_form.cleaned_data.get('birth_date') != "-":
                birth_date_shamsi = profile_form.cleaned_data.get('birth_date')
                check_valid_date = check_valid_birth_date(birth_date_shamsi)
                if check_valid_date:
                    year, month, day = map(int, birth_date_shamsi.split('/'))
                    birth_date_miladi = JalaliDate(year, month, day).todate().strftime('%Y-%m-%d')
                    user.birth_date = birth_date_miladi
                else:
                    profile_form.add_error('birth_date', 'فرمت را با توجه به روز/ماه/سال وارد کنید')

            user.save()
            profile_form.add_error(None, 'تغییرات پروفایل با موفقیت ذخیره شد.')
        else:
            profile_form.add_error(None, 'خطایی در ذخیره پروفایل رخ داده است.')

        if change_password_form.is_valid():
            old_password = change_password_form.cleaned_data['old_password']
            new_password1 = change_password_form.cleaned_data['new_password1']
            new_password2 = change_password_form.cleaned_data['new_password2']

            if not request.user.check_password(old_password):
                change_password_form.add_error('old_password', 'رمز عبور فعلی نادرست است.')
            elif new_password1 != new_password2:
                change_password_form.add_error('new_password2', 'رمز عبور جدید و تکرار آن مطابقت ندارند.')
            else:
                request.user.set_password(new_password1)
                request.user.save()
                update_session_auth_hash(request, request.user)
                change_password_form.add_error(None, 'رمز عبور با موفقیت تغییر کرد.')
        else:
            change_password_form.add_error(None, 'خطایی در تغییر رمز عبور رخ داده است.')
        user = Users.objects.filter(email__iexact=request.user).first()
        age = calculate_age(user.birth_date) if user.birth_date else "-"
        phone = user.phone_number if user.phone_number else "-"
        birth_date = convert_gregorian_to_jalali(user.birth_date) if user.birth_date else "-"
        gender = user.gender if user.gender else "-"
        context = {
            'profile_form': profile_form,
            'change_password_form': change_password_form,
            'show_profile': user,
            'age': age,
            'phone': phone,
            'birth_date': birth_date,
            'gender': gender
        }
        return render(request, 'account_module/profile_view_patient.html', context)


@login_required()
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        print(user)
        user.delete()
        return redirect('login')
    return render(request, 'account_module/profile_view_patient.html')


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('login')


class PatientChatView(View):
    @method_decorator(login_required)
    def get(self, request, recipient_id=None):
        if request.user.is_authenticated:
            user = request.user
            users = Users.objects.filter(email__iexact=user).first()
            first_name = users.first_name if users.first_name else "_"
            last_name = users.last_name if users.last_name else "_"
            today = timezone.now().date()
            week_ago = today - timedelta(days=7)
            p_reserve = ReserveDoctor.objects.filter(
                user__email__iexact=user,
                created_at__gt=week_ago
            ).select_related('doctor').distinct()
            unique_doctors = {}
            for reserve in p_reserve:
                unique_doctors[reserve.doctor.user_id] = reserve
            p_reserve_unique = list(unique_doctors.values())

            if recipient_id:
                recipient = get_object_or_404(Users, id=recipient_id)
                chat_messages = ChatMessage.objects.filter(
                    Q(sender=user, recipient=recipient) |
                    Q(sender=recipient, recipient=user)
                ).order_by('timestamp')
            else:
                recipient = None
                chat_messages = None

            form = ChatForm()

            context = {
                'first_name': first_name,
                'last_name': last_name,
                'dr_users': users,
                'recipient': recipient,
                'chat_messages': chat_messages,
                'form': form,
                'reserve': p_reserve_unique
            }
            return render(request, 'account_module/patient_chat.html', context)
        else:
            return redirect('login_doctor')

    @method_decorator(login_required)
    def post(self, request, recipient_id=None):
        user = request.user
        recipient = get_object_or_404(Users, id=recipient_id)

        form = ChatForm(request.POST)
        if form.is_valid():
            message = form.cleaned_data['message']
            ChatMessage.objects.create(sender=user, recipient=recipient, message=message)
            return redirect('chat_view_patient', recipient_id=recipient.id)

        # If form is invalid, re-render the page with the form errors
        users = Users.objects.filter(email__iexact=user).first()
        first_name = users.first_name if users.first_name else "_"
        last_name = users.last_name if users.last_name else "_"

        chat_messages = ChatMessage.objects.filter(
            Q(sender=user, recipient=recipient) |
            Q(sender=recipient, recipient=user)
        ).order_by('timestamp')

        context = {
            'first_name': first_name,
            'last_name': last_name,
            'dr_users': users,
            'recipient': recipient,
            'chat_messages': chat_messages,
            'form': form,
        }
        return render(request, 'account_module/patient_chat.html', context)


class CancelAppointmentPatientView(View):
    def post(self, request, reserve_id):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.user.is_authenticated:
            try:
                reserve = ReserveDoctor.objects.get(id=reserve_id, user=request.user)
                reserve.delete()
                return JsonResponse({'status': 'success', 'message': 'رزرو با موفقیت حذف شد'})
            except ReserveDoctor.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'رزرو یافت نشد'})
        return JsonResponse({'status': 'error', 'message': 'خطای احراز هویت یا درخواست غیرمجاز'})


class CancelMedicinePatientView(View):
    def post(self, request, med_id):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest' and request.user.is_authenticated:
            try:
                reserve = MedicineReminder.objects.get(id=med_id, user=request.user)
                reserve.delete()
                return JsonResponse({'status': 'success', 'message': 'رزرو با موفقیت حذف شد'})
            except ReserveDoctor.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'رزرو یافت نشد'})
        return JsonResponse({'status': 'error', 'message': 'خطای احراز هویت یا درخواست غیرمجاز'})


class MoreInformationPatientView(View):
    def get(self, request):
        more_info = MoreInformationPatientForm()
        return render(request, 'account_module/more_information_patient.html', {'more_info': more_info})

    def post(self, request):
        users = request.user
        more_info = MoreInformationPatientForm(request.POST)
        if users.is_authenticated:
            if more_info.is_valid():
                user= Users.objects.filter(email__iexact=users).first()
                name = more_info.cleaned_data.get('first_name')
                last_name = more_info.cleaned_data.get('last_name')
                password = more_info.cleaned_data.get('password')
                user.set_password(password)
                user.first_name = name
                user.last_name = last_name
                login(request, user)

                user.save()
                return redirect('patient_dashboard')
        else:
            return redirect('login')

        context = {
            "more_info": more_info
        }
        return render(request, 'account_module/more_information_patient.html', context)