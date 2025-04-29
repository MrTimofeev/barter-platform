from django.contrib import admin
from .models import Ad, ExchangeProposal


class AdAdmin(admin.ModelAdmin):
    """
    Класс для настройки отображения модели Ad в административной панели.
    
    Attributes:
        list_display (tuple): Поля, отображаемые в списке объявлений.
        list_filter (tuple): Поля для фильтрации справа.
        search_fields (tuple): Поля, по которым осуществляется поиск.
        prepopulated_fields (dict): Автозаполняемые поля.
        readonly_fields (tuple): Поля только для чтения.
        fieldsets (tuple): Группировка полей при редактировании.
    """
    
    list_display = ('id', 'title', 'user', 'category', 'condition', 'created_at')
    list_filter = ('category', 'condition')
    search_fields = ('title', 'description', 'user__username')
    prepopulated_fields = {}
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Основное', {
            'fields': ('user', 'title', 'description')
        }),
        ('Детали', {
            'fields': ('category', 'condition', 'image_url')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at')
        }),
    )


class ExchangeProposalAdmin(admin.ModelAdmin):
    """
    Класс для настройки отображения модели ExchangeProposal в административной панели.
    
    Attributes:
        list_display (tuple): Поля, отображаемые в списке предложений.
        list_filter (tuple): Поля для фильтрации справа.
        raw_id_fields (tuple): Поля с виджетом выбора через raw_id.
    """
    
    list_display = ('id', 'ad_sender', 'ad_receiver', 'status', 'created_at')
    list_filter = ('status',)
    raw_id_fields = ('ad_sender', 'ad_receiver')


# Регистрация моделей с кастомными настройками
admin.site.register(Ad, AdAdmin)
admin.site.register(ExchangeProposal, ExchangeProposalAdmin)