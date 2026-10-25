# Модуль 5 Автоматизация Book Store Login

Выполнила Володина Александра Александровна, ПКТб-23-1. Дата оформления: 26.10.2026.
Объект: https://demoqa.com/login. Все интеграционные проверки обращаются к настоящему DemoQA; подмена ответов не используется.

## Установка Windows PowerShell

```powershell
python -m venv .venv
.venv/Scripts/Activate.ps1
$env:PIP_CONFIG_FILE = (Resolve-Path config/pip.ini).Path
python -m pip install -r requirements.txt
python -m playwright install chromium firefox
```

Локальная конфигурация pip применяется только к этому процессу. Файл config/daemon.json содержит настройку зеркала Docker Hub; объедините registry-mirrors со своей конфигурацией Docker Engine, затем перезапустите Docker. Системные конфигурации автоматически не изменяются.

## Запуск

```powershell
python -m pytest tests/unit --cov=app --cov-branch --cov-report=html:artifacts/htmlcov --cov-report=json:artifacts/coverage.json --junitxml=artifacts/unit.xml --alluredir=allure-results
python -m pytest tests/api --junitxml=artifacts/api.xml --alluredir=allure-results
python -m pytest tests/ui --browser chromium --junitxml=artifacts/ui.xml --alluredir=allure-results
python -m pytest tests/ui --browser firefox --junitxml=artifacts/firefox.xml --alluredir=allure-results
python -m behave -f pretty -o - -f allure_behave.formatter:AllureFormatter -o allure-results features
```

Для установленного Microsoft Edge: добавьте `--browser-channel msedge` к pytest; для Behave установите `$env:BROWSER_CHANNEL = 'msedge'`.
Полный прогон: `./scripts/run_tests.ps1`. Установите Allure CLI 2 и Java 17+, затем выполните `allure generate allure-results --clean -o allure-report` и `allure open allure-report`.
`scripts/generate_allure.ps1` переносит историю предыдущего реального прогона. Содержимое config/allure-categories.json скопируйте в allure-results/categories.json.

## Архитектура

- app/validators.py: собственные функции валидации и маскирования; их покрытие не является покрытием исходного кода сайта DemoQA.
- support/api.py: requests.Session, таймауты, временные пользователи с UUID, удаление через finally, маскирование паролей и токенов в логах.
- pages/: все UI-локаторы и ожидания инкапсулированы в Page Object.
- tests/unit/: 40 параметризованных проверок и фикстура учетных данных.
- tests/api/: 12 проверок Books, Book, User, Login, GenerateToken, Authorized.
- tests/ui/: 5 основных тестов и 5 наборов CSV.
- features/: 2 русскоязычных BDD-сценария, независимые браузерные контексты и пользователи.
- artifacts/: фактические JUnit XML, покрытие, журналы и снимки экрана.

## Контракт DemoQA

Невалидный POST /Account/v1/Login возвращает 200 с пустым телом. Успешность входа определяется userId/token и переходом в профиль; HTTP 200 сам по себе не является доказательством авторизации. Форма вызывает GenerateToken перед Login. Регистрация через UI с CAPTCHA не автоматизируется; временные пользователи создаются через API и удаляются после проверки.

## CI/CD

Выбран допустимый заданием GitHub Actions. `.github/workflows/tests.yml` запускается по push, pull_request и вручную. Сначала выполняются Unit/API, затем UI+BDD в Chromium/Firefox. JUnit и Allure сохраняются даже при ошибке.

Проект опубликован: https://github.com/VolodinaAlexandra/qa_automation_module5.
Реальный успешный запуск №2: https://github.com/VolodinaAlexandra/qa_automation_module5/actions/runs/40211767783.
Проверенный коммит: `759b9739d42f194af7734e41e6bc5b3d745cee30`. Результат: Unit 40/40, API 12/12, UI+DDT 10/10 и BDD 2/2 в каждом браузере — 76/76 выполнений Passed, 64 уникальных сценария. Полное время 3 мин 48 с, включая установку зависимостей и браузеров.

Первый запуск №1: https://github.com/VolodinaAlexandra/qa_automation_module5/actions/runs/40211302610 завершился Failed: Chromium не дождался Profile за 5 секунд; страница оставалась Loading. Ожидание URL Profile увеличено до 30 с, имени пользователя — до 15 с. Автоматические перезапуски не добавлялись. Исходное падение, логи, JUnit и Allure обоих запусков включены в архив в `artifacts/ci/run1` и `artifacts/ci/run2`. Удаленные статусы проверены по метаданным GitHub Actions и скачанным артефактам; SHA256 ZIP-артефактов проверены по метаданным GitHub. Эти материалы доступны также на странице Actions, в репозитории Git они исключены через .gitignore.

## Selenoid

Раздел опциональный. Основной проект использует Playwright с нативными браузерами. Selenoid принимает Selenium WebDriver, а не Playwright CDP; подключать Playwright к порту 4444 через connect_over_cdp неправильно. Docker/Selenoid в этом проекте не запускались.

## Подсчет и отчетность

Основной набор: 40 Unit + 12 API + 10 UI (включая 5 DDT) + 2 BDD = 64 проверки. DDT и BDD — способы организации, а не отдельные уровни пирамиды. BDD относится к UI. Повторный запуск или второй браузер не увеличивает число уникальных тестов. Время, итоговые статусы и покрытие берутся из artifacts/, а не из демонстрационного отчета.

Даты в оформлении отчета: 26.10.2026. Машинные временные метки сохраняют фактическое время выполнения.

Основная установка выполнена через зеркало GitVerse; для text-unidecode после таймаута использован официальный резервный PyPI. Папка artifacts/calibration содержит первичный прогон до исправления локатора Logout и обновления токена очистки; итоговые метрики относятся к двум прогонам исправленной версии.

Для просмотра уже сформированного Allure без установки Java: `python -m http.server 8000 --bind 127.0.0.1 --directory allure-report`, затем открыть http://127.0.0.1:8000 в браузере.

## Сохраненные результаты

- artifacts/run1: 64 Passed из 64.
- artifacts/run2: 63 Passed, 1 Failed из 64; в test_logout предварительный вход с валидными данными был отклонен стендом.
- artifacts/diagnostic-logout.xml: отдельный контрольный повтор прошел; исходное падение из метрик не исключалось.
- artifacts/firefox.xml: 10 UI-проверок Passed.
- app: 25/25 исполняемых строк и 14/14 ветвей; C0/C1 100%.
- Итоговый Allure показывает второй полный прогон и историю первого; Pass Rate 98,4375%, наблюдаемая смена результата 1/64.

Автоматические перезапуски не используются. Причина единичного отказа входа не установлена. Машинные даты исходных журналов сохраняются фактическими; дата оформления работы — 26.10.2026.
