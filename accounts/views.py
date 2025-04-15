from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.serializers import UserSignupSerializer
from accounts.services.authentication_facade import AuthenticationFacade


class UserSignupView(APIView):
    def __init__(self):
        self.auth_facade = AuthenticationFacade()

    def post(self, request):
        serializer = UserSignupSerializer(data=request.data)

        # Validate the serializer
        if serializer.is_valid():
            # Call the signup method with the valid data
            username = serializer.validated_data["username"]
            password = serializer.validated_data["password"]
            result = self.auth_facade.signup(username, password)
            return Response(result, status=status.HTTP_201_CREATED)

        # If validation fails, return the error response
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    def __init__(self):
        self.auth_facade = AuthenticationFacade()

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        result = self.auth_facade.login(username, password)
        if "tokens" in result:
            return Response(result, status=status.HTTP_200_OK)
        return Response(result, status=status.HTTP_400_BAD_REQUEST)


class AdminApproveUserView(APIView):
    def __init__(self):
        self.auth_facade = AuthenticationFacade()

    def post(self, request, user_id):
        result = self.auth_facade.approve_user(user_id)
        return Response(result, status=status.HTTP_200_OK)
