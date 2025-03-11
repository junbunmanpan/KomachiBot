from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import TankaPost, TankaLike, TankaComment, TankaChat
from .forms import TankaChatForm
import random
import time
from django.http import JsonResponse
from tanka.models import TankaStatistics, TankaChat, TankaPost
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib import messages

@login_required
def chat_view(request):
    chats = TankaChat.objects.filter(user=request.user).order_by("created_at")  # 下から表示
    form = TankaChatForm()

    return render(request, "tanka/chat.html", {"chats": chats, "form": form})

@login_required
def send_tanka(request):
    """ 短歌を送信し、AIの反応を返す """
    if request.method == "POST":
        form = TankaChatForm(request.POST)
        if form.is_valid():
            # ユーザーの短歌を保存
            tanka = form.save(commit=False)
            tanka.user = request.user
            tanka.save()

            # AIの感嘆詞（遅延を入れる）
            time.sleep(0.5)  # 0.5秒のラグを追加
            reaction = generate_ai_reaction()

            # AIの返事を `ai_response` に保存
            TankaChat.objects.create(
                user=request.user, 
                is_ai_response=True, 
                ai_response=reaction  # ここに保存
            )

            # AIの反応をDBには保存せず、レスポンスとしてのみ返す
            return JsonResponse({
                "user_tanka": [tanka.line1, tanka.line2, tanka.line3, tanka.line4, tanka.line5], 
                "ai_response": reaction
            })

    return JsonResponse({"error": "Invalid request"}, status=400)

def generate_ai_reaction():
    """AIの感嘆詞を返す関数"""
    reactions = ["もぐもぐ...", "ふむふむ...", "なるほど...", "うむうむ", "ぐぬぬ..."]
    return random.choice(reactions)  # ランダムで1つ選ぶ


def index_view(request):
    # 学習した短歌数（AIの返事を除外）
    learned_tanka_count = TankaChat.objects.filter(is_ai_response=False).count()

    # 生成した短歌数
    generated_tanka_count = TankaPost.objects.count()

    return render(request, "tanka/index.html", {
        "learned_tanka_count": learned_tanka_count,
        "generated_tanka_count": generated_tanka_count,
    })

@login_required
def generate_tanka_view(request):
    """ 短歌を生成し、ユーザーに提示するAPI """
    tanka = TankaChat.generate_tanka()
    return JsonResponse({"tanka": tanka.split(" ")}) # スペースで区切って配列にする

@login_required
def post_tanka_view(request):
    """ 生成された短歌を投稿するAPI """
    if request.method == "POST":
        print("受信したデータ:", request.POST)  # デバッグ

        line1 = request.POST.get("line1")
        line2 = request.POST.get("line2")
        line3 = request.POST.get("line3")
        line4 = request.POST.get("line4")
        line5 = request.POST.get("line5")

        print("取得した短歌:", line1, line2, line3, line4, line5)  # デバッグ

        # 短歌をデータベースに保存
        TankaPost.objects.create(
            user=request.user, line1=line1, line2=line2, line3=line3, line4=line4, line5=line5
        )

        # 生成した短歌数の更新
        stats, created = TankaStatistics.objects.get_or_create(id=1)
        stats.generated_tanka_count = TankaPost.objects.count()
        stats.save()

        return redirect("timeline")

@login_required
def timeline_view(request):
    """ タイムライン表示 """
    posts = TankaPost.objects.all().order_by("-created_at")

    # 各短歌に対して、ユーザーがいいねしているか判定
    liked_posts = set(
        TankaLike.objects.filter(user=request.user).values_list("tanka_id", flat=True)
    )

    return render(request, "tanka/timeline.html", {"posts": posts, "liked_posts": liked_posts})

@login_required
def like_tanka_view(request, tanka_id):
    """ いいねをトグルする """
    tanka = get_object_or_404(TankaPost, id=tanka_id)
    like, created = TankaLike.objects.get_or_create(user=request.user, tanka=tanka)

    if not created:  # 既にいいね済みなら削除
        like.delete()

    return redirect("timeline")

@login_required
def comment_tanka_view(request, tanka_id):
    """ 短歌にコメントを追加する """
    tanka = get_object_or_404(TankaPost, id=tanka_id)

    if request.method == "POST":
        text = request.POST.get("text")
        if text:
            TankaComment.objects.create(user=request.user, tanka=tanka, text=text)

    return redirect("timeline")

def learn_tanka(request):
    if request.method == "POST":
        text = request.POST.get("text")
        if text:
            # 新しい学習データを保存
            TankaChat.objects.create(text=text)

            # 学習した短歌数の更新
            stats, created = TankaStatistics.objects.get_or_create(id=1)
            stats.learned_tanka_count = TankaChat.objects.count()
            stats.save()

    return redirect("index")

def register_view(request):
    """ 新規ユーザー登録 """
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        # 既存のユーザーIDをチェック
        if User.objects.filter(username=username).exists():
            messages.error(request, "このユーザーIDは既に使われています。別のIDをお試しください。")
            return redirect("login")  # ログインページに戻る

        # ユーザー作成
        user = User.objects.create_user(username=username, password=password)
        user.save()

        # 自動ログイン
        login(request, user)
        return redirect("index")  # 登録後に index にリダイレクト

    return redirect("login")