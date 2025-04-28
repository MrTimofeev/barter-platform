from django.db import models
from django.contrib.auth.models import User


class Ad(models.Model):
    # Выбор категории
    CATEGORY_CHOICE = [
        ('electronics',  'Электроника'),
        ('clothing', 'Одежда'),
        ('books', 'Книги'),
        ('home', 'Для дома'),
        ('other', 'Другое'),
    ]

    # Состояние товара
    CONDITION_CHOICE = [
        ('new', 'Новый'),
        ('used', 'Б/у'),
        ('broken', 'Требует ремонта'),
    ]

    # Поля модели
    user = models.ForeignKey(User, on_delete=models.CASCADE) # Связь с пользователем
    title = models.CharField(max_length=200)  # Заголовок объявление
    description = models.TextField() #Описание
    image_url = models.URLField(blank=True, null=True) #Картинка товара
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICE) #категория товара 
    conditio = models.CharField(max_length=50, choices=CONDITION_CHOICE) #Состояние товара
    created_at = models.DateTimeField(auto_created=True) #Дата создания товара (автоматически)
    update_at = models.DateTimeField(auto_now=True) #Дата обновления

    def __str__(self):
        return self.title 
    
class ExchangeProposal(models.Model):
    STATUS_CHOICES = [
        ('',''),
        ('',''),
        ('',''),
    ] 

    ad_sender = models.ForeignKey(Ad, on_delete=models.CASCADE, related_name="sent_proposals")
    ad_receiver = models.ForeignKey(Ad, on_delete=models.CASCADE, related_name="received_proposals")

    comment = models.TextField() #коментарий к предложению
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending') #Статус

    created_at = models.DateTimeField(auto_now_add=True) #Дата создания

    def __str__(self):
        return f"Предложение #{self.id} ({self.status})"
    
    
