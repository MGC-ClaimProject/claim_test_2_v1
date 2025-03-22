from django.urls import path
from insurances.views.views import (InsuranceDetailView, InsuranceListView,
                              UpdateMemberInsurancesView)
from insurances.views.crawling_views import CallCrawlerAPIView, CaptchaCrawlerAPIView, SimpleCallCrawlerAPIView, \
    CrawlerStatusAPIView

app_name = "insurances"
urlpatterns = [
    path("<int:pk>/", InsuranceListView.as_view(), name="insurances"),
    path(
        "<int:pk>/insurance/", InsuranceDetailView.as_view(), name="insurances-detail"
    ),
    path(
        "update/<int:member_id>/",
        UpdateMemberInsurancesView.as_view(),
        name="update-member-insurances",
    ),
    # all
    path("all_call_crawler/<int:member_id>/", CallCrawlerAPIView.as_view(), name="call_crawler"),
    path("captcha/<int:member_id>/", CaptchaCrawlerAPIView.as_view(), name="captcha_crawler"),
    # simple
    path("simple_call_crawler/<int:member_id>/", SimpleCallCrawlerAPIView.as_view(), name="simple_call_crawler"),
    path("crawler_status/<uuid:task_id>/", CrawlerStatusAPIView.as_view(), name="crawler_status"),  # ✅ 크롤러 상태 조회 추가
]
