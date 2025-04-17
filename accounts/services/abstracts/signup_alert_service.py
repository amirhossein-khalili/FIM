from abc import ABC, abstractmethod


class AbstractAdminAlertService(ABC):
    @abstractmethod
    def send_signup_notification(self, user_name: str) -> bool:
        """
        send notification of sign up to admin.
        """
        pass

