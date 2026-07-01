from django.urls import path
from .views import AnalyzeResumeView, ImproveProjectView, LeetCodeProfileView, HistoryListDestroyView, HealthCheckView

urlpatterns = [
    path('analyze/', AnalyzeResumeView.as_view(), name='analyze'),
    path('improve-project/', ImproveProjectView.as_view(), name='improve-project'),
    path('leetcode/', LeetCodeProfileView.as_view(), name='leetcode'),
    path('history/', HistoryListDestroyView.as_view(), name='history'),
    path('history/<int:pk>/', HistoryListDestroyView.as_view(), name='history-detail'),
    path('health/', HealthCheckView.as_view(), name='health'),
]
