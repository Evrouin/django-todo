from django.urls import path

from .admin_views import (
    AdminTodoDetailView,
    AdminTodoListView,
    AdminUserDetailView,
    AdminUserListView,
    admin_stats,
)

urlpatterns = [
    path("stats/", admin_stats, name="admin_stats"),
    path("users/", AdminUserListView.as_view(), name="admin_user_list"),
    path("users/<int:pk>/", AdminUserDetailView.as_view(), name="admin_user_detail"),
    path("todos/", AdminTodoListView.as_view(), name="admin_todo_list"),
    path("todos/<int:pk>/", AdminTodoDetailView.as_view(), name="admin_todo_detail"),
]
