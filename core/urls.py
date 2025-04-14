from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/accounts/", include("accounts.urls", namespace="accounts")),
    path("api/notifications/", include("notification.urls", namespace="notification")),
    # ---------------------------------------------------------------------------------
    #       SWAGGER AND DOCUMENTS URL PARTS
    # ---------------------------------------------------------------------------------
    # path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    # path(
    #     "api/schema/swagger-ui/",
    #     SpectacularSwaggerView.as_view(url_name="schema"),
    #     name="swagger-ui",
    # ),
    # path(
    #     "api/schema/redoc/",
    #     SpectacularRedocView.as_view(url_name="schema"),
    #     name="redoc",
    # ),
]
