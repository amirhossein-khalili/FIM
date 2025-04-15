# from django.test import TestCase

# from accounts.models import User
# from accounts.services.user_validation_impl import UserValidationServiceImpl


# class UserValidationServiceImplTest(TestCase):

#     def setUp(self):
#         # Create a user for validation tests
#         self.phone = "1234567890"
#         self.user = User.objects.create_user(phone=self.phone)
#         self.user_validation = UserValidationServiceImpl()

#     def test_user_exists(self):
#         # Test user exists
#         self.assertTrue(self.user_validation.user_exists(self.phone))

#         # Test non-existing user
#         self.assertFalse(self.user_validation.user_exists("nonexistent_phone"))

#     def test_has_user_access(self):
#         # Test if the user has access
#         self.assertTrue(self.user_validation.has_user_access(self.user))

#         # Test if the user is inactive (simulating a deactivated user)
#         self.user.is_active = False
#         self.user.save()
#         self.assertFalse(self.user_validation.has_user_access(self.user))
