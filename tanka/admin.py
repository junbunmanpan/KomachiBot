from django.contrib import admin
from .models import TankaPost, TankaLike, TankaComment, TankaChat

# モデルを管理画面に登録
admin.site.register(TankaPost)
admin.site.register(TankaLike)
admin.site.register(TankaComment)
admin.site.register(TankaChat)  # すでに登録済みなら不要
