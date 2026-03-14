<!-- lang: ru -->
# DTO: найди ошибки

В этом уроке три бага в DTO-конфигурации. Каждый баг — типичная ошибка при работе с `DataclassDTO`.

Подсказки:
1. `DTOConfig(exclude=...)` молча игнорирует несуществующие имена полей
2. Для PATCH-хендлера все поля должны быть необязательными
3. `dto=` принимает входные данные, `return_dto=` сериализует ответ — не перепутай

<!-- lang: en -->
# DTO: Find the Bugs

Three bugs in the DTO configuration. Each is a typical mistake when working with `DataclassDTO`.

Hints:
1. `DTOConfig(exclude=...)` silently ignores unknown field names
2. For PATCH handlers all fields should be optional
3. `dto=` receives input data, `return_dto=` serializes the response — don't swap them
