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
Полный прогон: `./scripts/run_tests.ps1`. Скрипт сохраняет прежний allure-results в artifacts перед запуском, чтобы результаты разных прогонов не смешивались. Установите Allure CLI 2 и Java 17+, затем выполните `allure generate allure-results --clean -o allure-report` и `allure open allure-report`.
`scripts/generate_allure.ps1` переносит историю предыдущего реального прогона. Содержимое config/allure-categories.json скопируйте в allure-results/categories.json.

## Архитектура

- app/validators.py: собственные функции валидации и маскирования; их покрытие не является покрытием исходного кода сайта DemoQA.
- support/api.py: requests.Session, таймауты, временные пользователи с UUID, удаление через finally, маскирование паролей и токенов в логах.
- API-фикстура account получает токен, а ui_account только регистрирует пользователя: первый GenerateToken выполняет сама форма. При очистке актуальный токен читается через Login; GenerateToken нужен только при отсутствии токена.
- pages/: все UI-локаторы и ожидания инкапсулированы в Page Object.
- LoginPage проверяет заполнение полей, ожидает реальный ответ GenerateToken до 30 секунд и прикладывает его в Allure с маскированием секретов. Для пустых полей HTTP не ожидается. Успех входа требует Profile и правильного имени пользователя.
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
Итоговый успешный запуск №4: https://github.com/VolodinaAlexandra/qa_automation_module5/actions/runs/41402051352.
Проверенный коммит: `1bd2fa04081c790070dbf19912bf4615a4cc2b0b`. Результат: Unit 40/40, API 12/12, UI+DDT 10/10 и BDD 2/2 в каждом браузере — 76/76 выполнений Passed, 0 Failed, 0 Broken, 0 Skipped; 64 уникальных сценария. Полное время 3 мин 13 с, включая установку зависимостей и браузеров. UI-05 прошёл в Chromium и Firefox. Три задания Success; три ZIP-артефакта скачаны и проверены по SHA256.

Первый запуск №1: https://github.com/VolodinaAlexandra/qa_automation_module5/actions/runs/40211302610 завершился Failed: Chromium не дождался Profile за 5 секунд; страница оставалась Loading. Ожидание URL Profile увеличено до 30 с, имени пользователя — до 15 с; запуск №2 прошёл. Однако запуск №3 https://github.com/VolodinaAlexandra/qa_automation_module5/actions/runs/41400509483 выявил другую ошибку: UI-05 получил GenerateToken HTTP 200 / status Failed при credentials_match=true. До этого фикстура уже выдала токен тому же пользователю. Отдельная диагностика API воспроизвела 2 отказа из 12 быстрых повторных запросов с верными данными; внутреннее устройство сервера не исследовалось. В коммите 1bd2fa0 убрана лишняя предварительная выдача токена для UI/BDD и дублирующая выдача при очистке. Следующий запуск №4 прошёл полностью.

Логи, JUnit и Allure всех четырёх запусков сохранены в `artifacts/ci/run1` — `artifacts/ci/run4`; прежние ошибки не удалены. В ZIP сдаваемого проекта включены скачанные артефакты и метаданные. В Git эти материалы исключены через .gitignore. Автоматических перезапусков, xfail и пропусков для получения успешного статуса нет.

## Selenoid

Раздел опциональный. Основной проект использует Playwright с нативными браузерами. Selenoid принимает Selenium WebDriver, а не Playwright CDP; подключать Playwright к порту 4444 через connect_over_cdp неправильно. Docker/Selenoid в этом проекте не запускались.

## Подсчет и отчетность

Основной набор: 40 Unit + 12 API + 10 UI (включая 5 DDT) + 2 BDD = 64 проверки. DDT и BDD — способы организации, а не отдельные уровни пирамиды. BDD относится к UI. Повторный запуск или второй браузер не увеличивает число уникальных тестов. Время, итоговые статусы и покрытие берутся из artifacts/, а не из демонстрационного отчета.

Даты в оформлении отчета: 26.10.2026. Машинные временные метки сохраняют фактическое время выполнения.

Основная установка выполнена через зеркало GitVerse; для text-unidecode после таймаута использован официальный резервный PyPI. Папка artifacts/calibration содержит первичный прогон до исправления локатора Logout и обновления токена очистки; итоговые метрики относятся к двум прогонам исправленной версии.

Для просмотра уже сформированного Allure без установки Java: `python -m http.server 8000 --bind 127.0.0.1 --directory allure-report`, затем открыть http://127.0.0.1:8000 в браузере.

## Сохраненные результаты

- artifacts/run5 и artifacts/run6: два итоговых полных прогона по 64 Passed из 64, без повторных попыток и пропусков. UI-05 (test_logout) прошёл в обоих. Полное время последнего прогона — 94,74 с.
- artifacts/firefox-fixed.xml: 10 UI-проверок Passed в Firefox 157; основной браузер — Edge 156.0.4314.58.
- artifacts/token-diagnosis.json: самостоятельная диагностика повторной выдачи токена, 10 Success и 2 Failed из 12 запросов; это диагностическая серия, отдельно от итоговых 64 сценариев.
- artifacts/diagnosis-nov02/diagnosis.json: шесть последовательных диагностических входов/выходов Passed; отправленные данные совпали с ожидаемыми.
- artifacts/run1: исторический прогон 64/64; artifacts/run2: исторические 63 Passed и 1 Failed. Их журналы и PNG сохранены.
- artifacts/diagnostic-logout.xml: прежний отдельный контрольный повтор Passed.
- app: 25/25 исполняемых строк и 14/14 ветвей; C0/C1 100%.
- Итоговый Allure показывает run6: Pass Rate 100%; история включает все шесть полных локальных прогонов. Между run5 и run6 смен результата нет (0/64). В старой паре run1/run2 была одна смена (1/64).
- Контрольные суммы исходников и SHA проверенного коммита сохранены в artifacts/run5/provenance.json и artifacts/run6/provenance.json. Записи собраны после выполнения при неизменном дереве исходников. Подход к сверке версии кода при анализе стабильности использован по присланному пользователем примеру; его авторские данные и набор доступности из другого модуля не переносились.

Автоматические перезапуски не используются. Для старого локального run2 сетевой ответ не сохранился, поэтому его точную причину установить нельзя. В CI №3 ответ сохранён, и отказ повторного GenerateToken подтверждён; зависимость подготовки UI/BDD от повторной выдачи токена устранена. Машинные даты журналов сохраняются фактическими; дата оформления работы — 26.10.2026.
