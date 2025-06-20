from io import StringIO
from lxml import etree
from django.core.exceptions import ValidationError
from django.core.validators import BaseValidator
from django.utils.html import strip_tags
import re

from rest_framework import permissions


class HTMLValidator(BaseValidator):
    def __init__(self, allowed_tags=None):
        self.allowed_tags = allowed_tags or ['a', 'code', 'i', 'strong']
        super().__init__(limit_value=None)

        # Регулярное выражение для поиска всех HTML-тегов
        self.all_tags_pattern = re.compile(r'<(/?)(\w+)([^>]*)>')

        # Регулярное выражение для проверки атрибутов в тегах
        self.attr_pattern = re.compile(
            r'\s+(href|title)="[^"]*"'  # Разрешаем только href и title в кавычках
        )

    def __call__(self, value):
        if not value:
            return value

        # 1. Проверяем все теги в тексте
        self._validate_all_tags(value)

        # 2. Проверяем валидность XHTML с lxml
        try:
            parser = etree.XMLParser()
            etree.parse(StringIO(f"<root>{value}</root>"), parser)
        except etree.XMLSyntaxError as e:
            raise ValidationError(f'Некорректный XHTML: {str(e)}')

        return value

    def _validate_all_tags(self, html):
        """Проверяет, что используются только разрешенные теги."""
        pos = 0
        while True:
            match = self.all_tags_pattern.search(html, pos)
            if not match:
                break

            tag = match.group(2).lower()
            is_closing = match.group(1) == '/'
            attrs = match.group(3) or ''

            # Проверяем, разрешен ли тег
            if tag not in self.allowed_tags:
                raise ValidationError(
                    f'Использован запрещенный тег <{tag}>. '
                    f'Разрешены только: {", ".join(self.allowed_tags)}'
                )

            # Для разрешенных тегов проверяем атрибуты
            if tag == 'a' and not is_closing:
                if not self._validate_anchor_attributes(attrs):
                    raise ValidationError(
                        'Тег <a> должен содержать только атрибуты href и title'
                    )
            elif attrs.strip():  # Другие теги не должны иметь атрибутов
                raise ValidationError(
                    f'Тег <{tag}> не должен содержать атрибутов'
                )

            pos = match.end()

    def _validate_anchor_attributes(self, attrs):
        """Проверяет атрибуты для тега <a>."""
        # Удаляем все разрешенные атрибуты и проверяем, осталось ли что-то
        cleaned_attrs = self.attr_pattern.sub('', attrs)
        # Должны остаться только пробелы или ничего
        return not cleaned_attrs.strip()


def validate_file_size(value):
    """Проверяет, что текстовые файлы не превышают 100KB."""
    limit = 100 * 1024
    if value.size > limit:
        raise ValidationError('Размер файла превышает лимит 100KB.')

class IsAuthor(permissions.BasePermission):
    """Проверяет, является ли пользователь автором объекта."""

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user