# Бартерная платформа

Веб-приложение на Django для размещения объявлений и обмена вещами между пользователями. Поддерживает веб-интерфейс и REST API.

## 🚀 Возможности

- Регистрация и вход
- Создание, редактирование, удаление объявлений
- Поиск и фильтрация по категории, состоянию и ключевым словам
- Обменные предложения между пользователями
- Отказ или принятие предложений
- REST API с документацией (Swagger, Redoc)

## 🛠️ Установка и запуск

### 1. Клонировать репозиторий

```bash
git clone https://github.com/MrTimofeev/barter-platform.git
cd barter-platform
````

### 2. Создать виртуальное окружение

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. Установить зависимости

```bash
pip install -r requirements.txt
```

### 4. Настроить переменные окружения

Создайте `.env` файл:

```
SECRET_KEY=your_secret_key
DEBUG=True
```

### 5. Применить миграции и создать суперпользователя

```bash
python manage.py migrate
python manage.py createsuperuser
```

### 6. Запустить сервер

```bash
python manage.py runserver
```

Откройте [http://127.0.0.1:8000](http://127.0.0.1:8000)

## 🧪 Тестирование

```bash
python manage.py test
```

## 📦 API

* Swagger UI: [http://localhost:8000/swagger/](http://localhost:8000/swagger/)
* ReDoc: [http://localhost:8000/redoc/](http://localhost:8000/redoc/)

## 👤 Автор

* \[MrTimofeev] — Telegram: @[Mr_Timofeev](https://t.me/Mr_Timofeev)