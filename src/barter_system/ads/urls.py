from django.urls import path

from ads import views

app_name = 'ads'

urlpatterns = [
    path('barter_system/', views.AdsListView.as_view(), name='list'),
    path('barter_system/add_ad/', views.AdCreateView.as_view(), name='add_ad'),
    path('barter_system/ads/<int:ad_pk>/', views.AdDetailView.as_view(), name='detail_ad'),
    path('barter_system/ads/<int:ad_pk>/edit/', views.AdUpdateView.as_view(), name='update_ad'),
    path(
        'barter_system/ads/<int:ad_pk>/delete/', views.AdDeleteView.as_view(), name='delete_ad'),

    path(
        'barter_system/ads/<int:ad_receiver_pk>/user-available-ads/',
        views.UserAvailableAdsView.as_view(),
        name='user_available_ads'),
    path(
        'barter_system/ads/<int:ad_receiver_pk>/user-available-ads/<int:ad_sender_pk>/',
        views.ExcCreateView.as_view(),
        name='add_exc'),
    path(
        'barter_system/excs/<int:exc_pk>/edit/', views.ExcUpdateView.as_view(),
        name='update_exc'),
    path(
        'barter_system/excs/<int:exc_pk>/delete/', views.ExcDeleteView.as_view(),
        name='delete_exc'),

    path('barter_system/user-ads/', views.UserAdsView.as_view(), name='user_ads'),
    path('barter_system/user-excs/', views.UserExcsView.as_view(), name='user_excs'),

    # path('error/', views.Error.as_view(), name='error')
    ]

