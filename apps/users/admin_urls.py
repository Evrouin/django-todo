from django.urls import path

from .admin_views import (
    AdminNoteDetailView,
    AdminNoteListView,
    AdminUserDetailView,
    AdminUserListView,
    admin_stats,
)

urlpatterns = [
    path("stats/", admin_stats, name="admin_stats"),
    path("users/", AdminUserListView.as_view(), name="admin_user_list"),
    path("users/<int:pk>/", AdminUserDetailView.as_view(), name="admin_user_detail"),
    path("notes/", AdminNoteListView.as_view(), name="admin_note_list"),
    path("notes/<int:pk>/", AdminNoteDetailView.as_view(), name="admin_note_detail"),
]
