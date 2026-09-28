# YaCut

Сервис сокращения ссылок с веб-интерфейсом на русском, JSON REST API и загрузкой
файлов на Яндекс Диск — с автоматическим сокращением ссылок на скачивание.

```
POST /api/id/               {"url": "https://example.com/"}
→ 201  {"url": "...", "short_link": "http://127.0.0.1:5000/aB3xY9"}

GET /api/id/aB3xY9/
→ 200  {"url": "https://example.com/"}
```

---

## Стек

`Flask` 3.0.2, `Flask-SQLAlchemy` 3.1.1, `SQLAlchemy` 2.0.21, `WTForms` 3.0.1, `Flask-WTF` 1.2.1
`aiohttp` 3.10.5 — HTTP-клиент для Яндекс Диска
`pytest` 7.1.3, `pytest-asyncio` 0.23.4, `pytest-aiohttp` 1.0.5, `pytest-env`, `flake8` 5.0.4

Требуется **Python 3.9+**. Разрабатывалось и тестировалось на 3.12.

> **Про архитектуру честно:** REST API и работа с базой — синхронные. Асинхронный
> код (`async def`) есть только в загрузке файлов: `yacut/views.py::files_view`,
> `yacut/views.py::upload_files` и клиент `yacut/services/yandex_disk.py`. Слой
> моделей обычный `Flask-SQLAlchemy`, асинхронной БД в проекте нет.

---

## Установка

```bash
git clone https://github.com/mraksdev/async-yacut.git
cd async-yacut
```

```bash
python3 -m venv venv
source venv/bin/activate                    # Linux / macOS
source venv/scripts/activate                # Windows, Git Bash
.\venv\Scripts\Activate.ps1                 # Windows, PowerShell
```

```bash
python3 -m pip install --upgrade pip
pip install -r requirements.txt
```

### Переменные окружения

Скопируйте пример и заполните:

```bash
cp .env.example .env
```

| Переменная | Назначение | По умолчанию |
|---|---|---|
| `SECRET_KEY` | ключ Flask | `yacut-secret-key` |
| `DATABASE_URI` | подключение к БД | `sqlite:///db.sqlite3` |
| `DISK_TOKEN` | OAuth-токен Яндекс Диска | нет — обязателен для загрузки |
| `FLASK_APP` | имя приложения для CLI `flask` | `yacut` |

`.env` читается через `python-dotenv` в `yacut/settings.py`. Файл в `.gitignore`.

> `FLASK_ENV` из `.env.example` можно не задавать: переменная удалена из Flask
> начиная с 2.3, а в проекте закреплён Flask 3.0.2.

### Создание базы данных

Миграций в проекте нет — таблицы создаются напрямую:

```bash
flask shell
```

```
>>> from yacut import db
>>> db.create_all()
>>> exit()
```

При `sqlite:///db.sqlite3` файл создаётся в `instance/db.sqlite3`.

---

## Запуск

```bash
flask run
```

Приложение откроется на `http://127.0.0.1:5000/`. Порт задан по умолчанию во
Flask и не переопределяется — коллекция Postman жёстко использует
`http://127.0.0.1:5000`, так что менять его без правки коллекции не стоит.

---

## Возможности

### Веб-интерфейс

| Маршрут | Назначение |
|---|---|
| `GET, POST /` | форма сокращения, список последних ссылок |
| `GET, POST /files` | загрузка файлов на Яндекс Диск |
| `GET /<short_id>` | редирект на оригинальный адрес |

### REST API

| Метод | Путь | Ответ |
|---|---|---|
| `POST` | `/api/id/` | `201` `{"url", "short_link"}` / `400` `{"message"}` |
| `GET` | `/api/id/<short_id>/` | `200` `{"url"}` / `404` `{"message"}` |

`POST /api/id/` принимает два поля:

```json
{
  "url": "https://example.com/",
  "custom_id": "my-link"
}
```

`url` обязателен. `custom_id` — необязательный, до 16 символов, только латиница
и цифры, должен быть свободен. Если не задан, генерируется случайно: 6 символов
из 62 (`A-Za-z0-9`). Слово `files` зарезервировано и не может стать короткой ссылкой.

Валидация идёт в фиксированном порядке: пустое тело → отсутствие `url` →
недопустимый `custom_id` → занятый `custom_id`.

### Обработка ошибок

`yacut/errorhandlers.py` регистрирует обработчики 404 и 500. Формат ответа выбирается
по пути запроса: пути, начинающиеся с `/api/`, получают JSON
`{"message": ...}`, остальные — HTML-шаблон `errors/error.html`.

### Загрузка файлов на Яндекс Диск

`yacut/services/yandex_disk.py` выполняет три запроса на файл:

1. `GET /v1/disk/resources/upload?path=app:/<имя>&overwrite=true` — получить ссылку для загрузки
2. `PUT <href>` — передать содержимое
3. `GET /v1/disk/resources/download?path=<путь>` — получить ссылку на скачивание

Файл попадает в папку `app:/` на Диске. Прямая ссылка на Диск пользователю не
показывается — вместо неё создаётся короткая ссылка через `create_url_map()`.
Один `aiohttp.ClientSession` переиспользуется для всех файлов; ошибка по
отдельному файлу не прерывает загрузку остальных, итог показывается flash-сообщением.

Токен читается из `DISK_TOKEN` при каждом вызове, а не один раз при импорте.

---

## Тесты

```bash
pytest
```

26 тест-функций, 35 собранных тестов — три параметризованы.

| Файл | Тестов | Что покрывает |
|---|---|---|
| `test_config.py` | 1 | `SECRET_KEY` попадает в конфиг |
| `test_database.py` | 1 | У модели `URLMap` есть `id`, `original`, `short`, `timestamp` |
| `test_errorhandlers.py` | 1 | 404 отдаёт кастомный шаблон, а не стандартный текст Flask |
| `test_endpoints.py` | 16 | Весь API: создание, все варианты 400, автогенерация id, получение, 404, лимит длины |
| `test_shortening_view.py` | 12 | Веб-интерфейс: форма, создание, дубликаты, зарезервированный `files`, редирект, невалидные символы |
| `test_file_upload_view.py` | 4 | Страница загрузки, форма, полный сценарий с моками |

### Мок-сервер вместо Яндекс Диска

Обращения к внешнему API изолированы настоящим мок-сервером на
`aiohttp.web` — `tests/yandex_disk_mock_server.py`. Он поднимается на
случайном порту, эмулирует все три эндпоинта Диска и **обрушивает тест**, если
приложение вызовет что-то не смоделированное.

Трафик перенаправляется подменой `aiohttp.ClientSession`: любой URL,
содержащий `yandex`, заменяется адресом мока. Реальных запросов к Диску
в тестах не происходит.

Тест `test_upload_files` дополнительно проверяет, что все три вызова выполнены и
что прямые ссылки мока не попали в HTML.

Тесты работают на `sqlite:///:memory:` и не требуют настроенной БД.

---

## OpenAPI

В корне лежит [`openapi.yml`](openapi.yml) — спецификация **OpenAPI 3.0.3** с
описанием обоих методов API, схем запросов и ответов и примерами сообщений
об ошибках. Контракт синхронизирован с кодом.

> Файл статический. Маршрута, отдающего Swagger UI или Redoc, в проекте нет —
> спецификацию нужно смотреть в репозитории.

## Postman

[`postman_collection/`](postman_collection) — коллекция из 10 запросов в четырёх
папках: успешные сценарии, ошибки `POST`, получение по ссылке и ошибки `GET`.
Каждый запрос проверяет JSON-схему ответа и точный текст сообщения.

Коллекция ожидает заранее подготовленную запись в БД:

```bash
cd postman_collection
bash set_up_data.sh
cd ..
flask run
```

Скрипт **очищает таблицу** и добавляет одну запись `https://example.com/` →
`example`. Запускайте на локальной базе.

---

## Структура

```
async-yacut/
├── yacut/
│   ├── __init__.py          # app и db, регистрация маршрутов импортами
│   ├── settings.py
│   ├── constants.py         # длины, символы, тексты сообщений
│   ├── models.py            # URLMap
│   ├── short_links.py       # генерация и валидация коротких ссылок
│   ├── api_views.py         # 2 маршрута REST API
│   ├── views.py             # 3 маршрута веба, upload_files
│   ├── errorhandlers.py
│   ├── forms.py             # WTForms
│   ├── services/yandex_disk.py
│   ├── templates/
│   └── static/
├── tests/                   # 26 тест-функций
├── postman_collection/
├── openapi.yml
├── pytest.ini
├── .env.example
└── requirements.txt
```

Маршруты регистрируются напрямую на объекте `app` в `yacut/__init__.py` —
blueprint'ов в проекте нет.

---

## Лицензия

MIT — см. [LICENSE](LICENSE).
