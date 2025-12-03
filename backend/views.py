from django.http import JsonResponse

def root_view(request):
    return JsonResponse({"message": "Backend is running"}, status=200)
