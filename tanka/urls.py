from django.urls import path
from django.contrib.auth.views import LoginView
from .views import chat_view, index_view, send_tanka, generate_tanka_view, post_tanka_view, timeline_view, like_tanka_view, comment_tanka_view, register_view  # ここを修正

urlpatterns = [
    path("", index_view, name="index"),  # トップページ
    path("chat/", chat_view, name="chat"),  # チャットページ
    path("send_tanka/", send_tanka, name="send_tanka"),
    path("generate_tanka/", generate_tanka_view, name="generate_tanka"),
    path("post_tanka/", post_tanka_view, name="post_tanka"),
    path("timeline/", timeline_view, name="timeline"),
    path("like_tanka/<int:tanka_id>/", like_tanka_view, name="like_tanka"),
    path("comment_tanka/<int:tanka_id>/", comment_tanka_view, name="comment_tanka"),
    path('login/', LoginView.as_view(template_name='registration/login.html'), name='login'),
    path("register/", register_view, name="register"),  # 新規登録のURL
]
