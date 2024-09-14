'''
---------------------------------------------------
Project:        Braelo
Date:           Aug 14, 2024
Author:         Hamid
---------------------------------------------------

Description:
End points file (abstracted).
All end points will be in Braelo/users/api/
---------------------------------------------------
'''

from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt


# testing
@csrf_exempt
def sign_in(request):
    return render(request, 'sign_in.html')
