from django.urls import path

from .views import TodoDetailView, TodoListCreateView, bulk_delete_todos, bulk_pin_todos, bulk_restore_todos

urlpatterns = [
    path("", TodoListCreateView.as_view(), name="todo_list_create"),
    path("bulk-delete/", bulk_delete_todos, name="todo_bulk_delete"),
    path("bulk-pin/", bulk_pin_todos, name="todo_bulk_pin"),
    path("bulk-restore/", bulk_restore_todos, name="todo_bulk_restore"),
    path("<int:pk>/", TodoDetailView.as_view(), name="todo_detail"),
]
