from django import forms
from .models import *


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["author", "text"]

    def clean_author(self):
        author = self.cleaned_data["author"]
        if author:
            if len(author) < 3:
                raise forms.ValidationError("نام باید حداقل 3 کاراکتر باشد")

            else:
                return author

    def clean_text(self):
        text = self.cleaned_data["text"]
        if text:
            if len(text) < 7:
                raise forms.ValidationError("کامنت باید حداقل 7 کاراکتر باشد")

            else:
                return text


class SearchForm(forms.Form):
    query = forms.CharField(max_length=250)


class LoginForm(forms.Form):
    username = forms.CharField(max_length=250)
    password = forms.CharField(widget=forms.PasswordInput)


class RegisterForm(forms.ModelForm):
    password = forms.CharField(max_length=20, widget=forms.PasswordInput)
    password2 = forms.CharField(max_length=20, widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email"]

    def clean_username(self):
        username = self.cleaned_data.get("username")

        if not username:
            raise forms.ValidationError("این فیلد نباید خالی بماند")

        if username.isnumeric():
            raise forms.ValidationError("نام کاربری نباید فقط عدد باشد!")
        elif len(username) < 3:
            raise forms.ValidationError("نام کاربری نباید کمتر از 3 حرف باشد!")

        return username


    def clean_first_name(self):
        first_name = self.cleaned_data.get("first_name")

        if not first_name:
            raise forms.ValidationError("این فیلد نباید خالی بماند")

        if first_name.isnumeric():
            raise forms.ValidationError("نام نباید فقط عدد باشد!")
        elif len(first_name) < 3:
            raise forms.ValidationError("نام نباید کمتر از 3 حرف باشد!")

        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get("last_name")

        if not last_name:
            raise forms.ValidationError("این فیلد نباید خالی بماند")

        if last_name.isnumeric():
            raise forms.ValidationError("نام خانوادگی نباید فقط عدد باشد!")
        elif len(last_name) < 3:
            raise forms.ValidationError("نام خانوادگی نباید کمتر از 3 حرف باشد!")
        return last_name


    def clean_password2(self):
        password = self.cleaned_data.get("password")
        password2 = self.cleaned_data.get("password2")
        if password and password2 and password != password2:
            raise forms.ValidationError("رمز عبور و تکرار آن مطابقت ندارند")
        return password2
    
class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "bio", "photo", "job"]

    def clean_first_name(self):
        first_name = self.cleaned_data.get("first_name")

        if not first_name:
            raise forms.ValidationError("این فیلد نباید خالی بماند")

        if first_name.isnumeric():
            raise forms.ValidationError("نام نباید فقط عدد باشد!")
        elif len(first_name) < 3:
            raise forms.ValidationError("نام نباید کمتر از 3 حرف باشد!")
        
        return first_name
        

    def clean_last_name(self):
        last_name = self.cleaned_data.get("last_name")

        if not last_name:
            raise forms.ValidationError("این فیلد نباید خالی بماند")

        if last_name.isnumeric():
            raise forms.ValidationError("نام خانوادگی نباید فقط عدد باشد!")
        elif len(last_name) < 3:
            raise forms.ValidationError("نام خانوادگی نباید کمتر از 3 حرف باشد!")
        return last_name


    def clean_bio(self):
        bio = self.cleaned_data.get("bio")

        if not bio:
            raise forms.ValidationError("این فیلد نباید خالی بماند")

        if bio.isnumeric():
            raise forms.ValidationError("بایو نباید فقط عدد باشد")
        elif len(bio) < 10:
            raise forms.ValidationError(" بایو نباید کمتر از 10 حرف باشد!")
        return bio


    def clean_job(self):
        job = self.cleaned_data.get("job")

        if not job:
            raise forms.ValidationError("این فیلد نباید خالی بماند")

        if job.isnumeric():
            raise forms.ValidationError("شغل نباید فقط عدد باشد")
        elif len(job) < 3:
            raise forms.ValidationError(" شغل نباید کمتر از 3 حرف باشد!")
        return job




class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "description", "study", "category"]


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ["problem", "subject", "message"]


    def clean_problem(self):
        problem = self.cleaned_data.get("problem")

        if not problem:
            raise forms.ValidationError("این فیلذ نباید خالی بماند")

        if problem.isnumeric():
            raise forms.ValidationError("این فیلذ نباید فقط عدد باشد")
        elif len(problem) < 5:
            raise forms.ValidationError(" این فیلد نباید کمتر از ۵ حرف باشد!")
        return problem

    def clean_message(self):
        message = self.cleaned_data.get("message")

        if not message:
            raise forms.ValidationError("این فیلذ نباید خالی بماند")

        if message.isnumeric():
            raise forms.ValidationError("این فیلذ نباید فقط عدد باشد")
        elif len(message) < 7:
            raise forms.ValidationError(" این فیلد نباید کمتر از ۷ حرف باشد!")
        return message
