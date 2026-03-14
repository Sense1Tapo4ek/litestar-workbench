from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Article:
    title: str
    content: str
    tags: list[str] | None = None
    published: bool = False
    id: int | None = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


_store: dict[int, Article] = {}
_next_id = 1


def create_article(title: str, content: str, tags: list[str] | None = None) -> Article:
    global _next_id
    article = Article(id=_next_id, title=title, content=content, tags=tags)
    _store[_next_id] = article
    _next_id += 1
    return article


def get_article(article_id: int) -> Article | None:
    return _store.get(article_id)


def update_article(
    article_id: int, title: str, content: str, tags: list[str] | None
) -> Article | None:
    article = _store.get(article_id)
    if article is None:
        return None
    article.title = title
    article.content = content
    article.tags = tags
    return article


def publish_article(article_id: int) -> Article | None:
    article = _store.get(article_id)
    if article is None:
        return None
    article.published = True
    return article
