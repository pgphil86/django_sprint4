import inspect

from conftest import squash_code


def test_static_pages_as_cbv():
    try:
        from pages import urls
    except Exception as e:
        raise AssertionError(
            'Убедитесь, что в файле `pages/urls.py` нет ошибок. '
            'При его импорте возникла ошибка:\n'
            f'{type(e).__name__}: {e}'
        )
    squashed_urls_src = squash_code(inspect.getsource(urls))
    err_msg = (
        'Убедитесь, что в файле `pages/urls.py` подключаете маршруты '
        'статических страниц, используя CBV.'
    )
    for assert_str in (
            'TemplateView', 'as_view', 'pages/about.html', 'pages/rules.html'):
        if assert_str not in squashed_urls_src:
            raise AssertionError(err_msg)
