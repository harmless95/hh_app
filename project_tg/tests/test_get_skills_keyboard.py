from handler_tg.handler_keyboard.keyboard_inline import (
    get_skills_keyboard,
    AVAILABLE_SKILLS,
)


def test_get_skills_keyboard_marks_selected():
    """Этот тест проверяет Генератор"""

    # Убедиться, что функция правильно рисует интерфейс
    #   «Если я дам функции сет {"Docker"}, она нарисует плюсик именно на этой кнопке?

    # 1. Допустим, выбран Docker
    selected = {"Docker"}

    # 2. Генерируем клавиатуру
    markup = get_skills_keyboard(selected)

    # 3. Ищем кнопку Docker в разметке
    # inline_keyboard — это список строк (rows), в каждой строке список кнопок
    all_buttons = [btn for row in markup.inline_keyboard for btn in row]
    docker_btn = next(b for b in all_buttons if "Docker" in b.text)
    python_btn = next(b for b in all_buttons if "Python" in b.text)

    # 4. Проверяем наличие плюсика у Docker и отсутствие у Python
    assert docker_btn.text == "+ Docker"
    assert python_btn.text == "Python"
    # Проверяем, что кнопка поиска тоже на месте
    assert any(b.callback_data == "start_search" for b in all_buttons)
