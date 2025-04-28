from django.db import models
from django.contrib.auth.models import User


class Ad(models.Model):
    """
    Модель объявления для обмена товарами.

    Attributes:
        CATEGORY_CHOICE (list): Варианты категорий товаров.
        CONDITION_CHOICE (list): Варианты состояний товаров.
        user (ForeignKey): Связь с пользователем, создавшим объявление.
        title (CharField): Заголовок объявления.
        description (TextField): Подробное описание товара.
        image_url (URLField): Ссылка на изображение товара (необязательное).
        category (CharField): Категория товара.
        condition (CharField): Состояние товара.
        created_at (DateTimeField): Дата создания объявления (автоматически).
        updated_at (DateTimeField): Дата последнего обновления (автоматически).
    """

    # Выбор категории
    CATEGORY_CHOICE = [
        ('electronics', 'Электроника'),
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
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    title = models.CharField(
        max_length=200,
        verbose_name='Заголовок'
    )
    description = models.TextField(
        verbose_name='Описание'
    )
    image_url = models.URLField(
        blank=True,
        null=True,
        verbose_name='Ссылка на изображение'
    )
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICE,
        verbose_name='Категория'
    )
    condition = models.CharField(
        max_length=50,
        choices=CONDITION_CHOICE,
        verbose_name='Состояние товара'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Объявление'
        verbose_name_plural = 'Объявления'
        ordering = ['-created_at']


class ExchangeProposal(models.Model):
    """
    Модель предложения обмена между объявлениями.

    Attributes:
        STATUS_CHOICES (list): Варианты статусов предложения.
        ad_sender (ForeignKey): Объявление отправителя.
        ad_receiver (ForeignKey): Объявление получателя.
        comment (TextField): Комментарий к предложению.
        status (CharField): Текущий статус предложения.
        created_at (DateTimeField): Дата создания предложения (автоматически).
    """

    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('accepted', 'Принята'),
        ('rejected', 'Отклонена'),
    ]

    ad_sender = models.ForeignKey(
        Ad,
        on_delete=models.CASCADE,
        related_name='sent_proposals',
        verbose_name='Объявление отправителя'
    )
    ad_receiver = models.ForeignKey(
        Ad,
        on_delete=models.CASCADE,
        related_name='received_proposals',
        verbose_name='Объявление получателя'
    )
    comment = models.TextField(
        verbose_name='Комментарий'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Статус'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )

    def __str__(self):
        return f'Предложение #{self.id} ({self.status})'

    class Meta:
        verbose_name = 'Предложение обмена'
        verbose_name_plural = 'Предложения обмена'
        ordering = ['-created_at']
