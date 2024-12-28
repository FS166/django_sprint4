from django.db import models


class StaticPage(models.Model):
    title = models.CharField(max_length=256, verbose_name="Заголовок")
    content = models.TextField(verbose_name="Содержимое")
    slug = models.SlugField(unique=True,
                            verbose_name="URL",
                            help_text="Часть URL для этой страницы")
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True,
                                      verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Статичная страница"
        verbose_name_plural = "Статичные страницы"

    def __str__(self):
        return self.title
