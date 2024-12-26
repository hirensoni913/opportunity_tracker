from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.models import AnonymousUser


class JWTAuthenticationMiddleware:
    pass
    # def __init__(self, get_response):
    #     self.get_response = get_response

    # def __call__(self, request):
    #     if request.path.startswith('/admin/'):
    #         return self.get_response(request)

    #     # Check if the cookie is present
    #     token = request.COOKIES.get('access')

    #     if token:
    #         try:
    #             # set token in authorization header
    #             request.META['HTTP_AUTHORIZATION'] = f"Bearer {token}"
    #             # Decode the token
    #             jwt_authentication = JWTAuthentication()
    #             user, token = jwt_authentication.authenticate(request)
    #             if user:
    #                 request.user = user
    #             else:
    #                 request.user = AnonymousUser()
    #         except InvalidToken:
    #             request.user = AnonymousUser()
    #     else:
    #         request.user = AnonymousUser()

    #     return self.get_response(request)
