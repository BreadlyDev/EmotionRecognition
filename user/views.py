import base64
from io import BytesIO

from django.contrib.auth import authenticate, login
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from PIL import Image

from user.forms import LoginForm, RegisterForm
from user.models import User
from .ai import check_photo

def main_view(request):
    user = request.user
    return render(request, 'index.html', {'user': user})

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            photo = form.cleaned_data.get('photo')

            if photo:
                print(f"File received: {photo}")
            else:
                print("No file received")
                return HttpResponse('Status: 403 Bad Request.\n Photo is required field')

            user = User.objects.create_user(email=email, password=password, photo=photo)
            login(request, user)
            return redirect('main')
    else:
        form = RegisterForm()
    return render(request, 'pages/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user:
                login(request, user)
                return redirect('main')
            else:
                form.add_error(None, "Invalid email or password.")
    else:
        form = LoginForm()
    return render(request, 'pages/login.html', {'form': form})

@csrf_exempt
def login_by_photo(request):
    if request.method == 'POST':
        try:
            photo_data = request.POST.get('photo')
            if not photo_data:
                return JsonResponse({'success': False, 'message': 'No photo provided'}, status=400)

            photo_data = photo_data.split(",")[1]
            photo_bytes = base64.b64decode(photo_data)
            input_photo = Image.open(BytesIO(photo_bytes))

            users = User.objects.all()
            for user in users:
                if user.photo:
                    user_photo_path = user.photo.path
                    user_photo = Image.open(user_photo_path)

                    if check_photo(user_photo, input_photo):
                        login(request, user)
                        return JsonResponse({'success': True, 'message': 'Logged in successfully'})

            return JsonResponse({'success': False, 'message': 'No matching user found'}, status=401)

        except Exception as e:
            print(e)
            return JsonResponse({'success': False, 'message': 'An error occurred while processing the photo'},
                                status=500)

    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)