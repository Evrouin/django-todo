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
    path("users/<uuid:uuid>/", AdminUserDetailView.as_view(), name="admin_user_detail"),
    path("notes/", AdminNoteListView.as_view(), name="admin_note_list"),
    path("notes/<uuid:uuid>/", AdminNoteDetailView.as_view(), name="admin_note_detail"),
]
