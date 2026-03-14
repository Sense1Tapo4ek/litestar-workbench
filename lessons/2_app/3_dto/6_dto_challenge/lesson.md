<!-- lang: ru -->
# DTO: реализуй CRUD с разделением write/read

Реализуй полный CRUD для `Product` с тремя DTO-классами:

- **WriteDTO** — для создания (исключает `id`, `created_at`, `internal_cost`)
- **ReadDTO** — для чтения (исключает только `internal_cost` — внутреннее поле)
- **PatchDTO** — для частичного обновления (`partial=True`, те же exclusions что у Write)

```python
class ProductWriteDTO(DataclassDTO[Product]):
    config = DTOConfig(exclude={"id", "created_at", "internal_cost"})
```

Не забудь: `DTOData[Product]` для write/patch хендлеров, `data.create_instance(id=next_id())` для POST, `data.update_instance(product)` для PATCH.

<!-- lang: en -->
# DTO: Implement CRUD with Write/Read Split

Implement full CRUD for `Product` with three DTO classes:

- **WriteDTO** — for creation (excludes `id`, `created_at`, `internal_cost`)
- **ReadDTO** — for reading (excludes only `internal_cost` — internal field)
- **PatchDTO** — for partial updates (`partial=True`, same exclusions as Write)

```python
class ProductWriteDTO(DataclassDTO[Product]):
    config = DTOConfig(exclude={"id", "created_at", "internal_cost"})
```

Remember: use `DTOData[Product]` for write/patch handlers, `data.create_instance(id=next_id())` for POST, `data.update_instance(product)` for PATCH.
