from django.db import models
from django.contrib.auth.models import User
import random

class TankaChat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    line1 = models.CharField(max_length=50)  # 1句目（5音想定）
    line2 = models.CharField(max_length=50)  # 2句目（7音想定）
    line3 = models.CharField(max_length=50)  # 3句目（5音想定）
    line4 = models.CharField(max_length=50)  # 4句目（7音想定）
    line5 = models.CharField(max_length=50)  # 5句目（7音想定）
    is_ai_response = models.BooleanField(default=False)  # AIの返事かどうかを区別
    ai_response = models.TextField(blank=True, null=True)  # AIの返事専用カラム
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.line1} {self.line2} {self.line3} {self.line4} {self.line5}"

    def generate_response(self):
        """ 小町の応答（感嘆詞 or 返歌） """
        reactions = ["うむうむ…", "もぐもぐ…", "なるほど…", "すごい！"]
        if random.random() < 0.3:  # 30%の確率で返歌
            return self.generate_tanka()
        return random.choice(reactions)
    
    @classmethod
    def generate_tanka(cls):
        """ ランダムに短歌を生成する """
        """ ランダムに短歌を生成する（AIの返事を除外） """
        # AIの返事を除外して学習データを取得
        line1_choices = list(cls.objects.filter(is_ai_response=False).values_list('line1', flat=True).distinct())
        line2_choices = list(cls.objects.filter(is_ai_response=False).values_list('line2', flat=True).distinct())
        line3_choices = list(cls.objects.filter(is_ai_response=False).values_list('line3', flat=True).distinct())
        line4_choices = list(cls.objects.filter(is_ai_response=False).values_list('line4', flat=True).distinct())
        line5_choices = list(cls.objects.filter(is_ai_response=False).values_list('line5', flat=True).distinct())
        # データがない場合のデフォルト
        if not line1_choices: line1_choices = ["空腹で"]
        if not line2_choices: line2_choices = ["のたうちまわる"]
        if not line3_choices: line3_choices = ["冷蔵庫"]
        if not line4_choices: line4_choices = ["プラチナディスコ"]
        if not line5_choices: line5_choices = ["ちょっと寂しい"]

        # 各句をランダムに選択
        line1 = random.choice(line1_choices)
        line2 = random.choice(line2_choices)
        line3 = random.choice(line3_choices)
        line4 = random.choice(line4_choices)
        line5 = random.choice(line5_choices)

        return f"{line1} {line2} {line3} {line4} {line5}"

class TankaPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    line1 = models.CharField(max_length=50)
    line2 = models.CharField(max_length=50)
    line3 = models.CharField(max_length=50)
    line4 = models.CharField(max_length=50)
    line5 = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.line1} {self.line2} {self.line3} {self.line4} {self.line5}"


class TankaLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tanka = models.ForeignKey(TankaPost, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "tanka")  # 一人一回のみ

class TankaComment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tanka = models.ForeignKey(TankaPost, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class TankaStatistics(models.Model):
    learned_tanka_count = models.IntegerField(default=0)  # 学習した短歌数
    generated_tanka_count = models.IntegerField(default=0)  # 生成した短歌数

    def __str__(self):
        return f"学習: {self.learned_tanka_count}, 生成: {self.generated_tanka_count}"