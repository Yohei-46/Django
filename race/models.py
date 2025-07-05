from django.db import models

# Create your models here.
class RaceResult(models.Model):
    race_id = models.CharField(max_length=20)  # レースID（例: 202406120811）
    date = models.DateField(null=True, blank=True)  # レース日
    place = models.CharField(max_length=100)  # 開催場所（例: 東京）
    distance = models.IntegerField(null=True, blank=True)  # 距離（例: 1600）
    #horse_number = models.IntegerField()
    horse_name = models.CharField(max_length=100)
    jockey = models.CharField(max_length=100)
    rank = models.IntegerField(null=True, blank=True)
    time = models.FloatField(null=True, blank=True)  # 走破タイム（例: 94.3秒）

    popularity = models.IntegerField(null=True, blank=True)  # 単勝人気（例: 1, 2, 3位など）
    odds = models.FloatField(null=True, blank=True)  # 単勝オッズ（例: 3.5）

    trainer = models.CharField(max_length=100, null=True, blank=True)  # 調教師名（任意）
    weight = models.FloatField(null=True, blank=True)  # 馬体重（任意）

    horse_number = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = ('race_id', 'horse_number')
        

    def __str__(self):
        return f"{self.date} {self.place} {self.horse_name} 着順:{self.rank}"
