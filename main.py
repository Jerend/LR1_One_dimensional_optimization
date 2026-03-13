import pygame
import math
import sys
from dataclasses import dataclass
from typing import List, Callable, Optional
import csv
import os
from datetime import datetime

# Глобальные параметры
e: float = 0.001
l: float = 0.2
a: float = -3
b: float = 5

@dataclass
class Iteration:
    """Структура для хранения данных итерации"""
    a: float
    b: float
    lamda: float
    mu: float
    f_lamda: float
    f_mu: float


@dataclass
class ResultInfo:
    """Структура для хранения результатов"""
    select_method: str
    select_f: str
    optimal_x: float
    optimal_f: float
    func_calculations: int


# Функции для оптимизации
def F1(x: float) -> float:
    """Первая тестовая функция"""
    return (x - 4) / (x - 9)


def F2(x: float) -> float:
    """Вторая тестовая функция"""
    result = x * x - 1
    return result if result > 0 else -result


def F3(x: float) -> float:
    """Третья тестовая функция (из лекции)"""
    return x * x + 2 * x


def select_func(number_f: int) -> Optional[Callable[[float], float]]:
    """Выбор функции по номеру"""
    functions = {
        1: F1,
        2: F2,
        3: F3
    }
    return functions.get(number_f)


def dihotomy_search(iterations: List[Iteration], result: ResultInfo, number_f: int) -> None:
    """Метод дихотомического поиска"""
    # Добавляем информацию о методе и функции
    result.select_method = "Дихотомический поиск"
    result.select_f = f"F{number_f}"
    
    k = 0
    func_calc_count = 0
    
    func = select_func(number_f)
    if func is None:
        return
    
    while True:
        current = iterations[k]
        
        if current.b - current.a < l:
            mid = (current.a + current.b) / 2
            result.optimal_x = mid
            result.optimal_f = func(mid)
            result.func_calculations = func_calc_count+1
            return
        
        # Вычисляем точки и значения функций
        lamda = (current.a + current.b) / 2 - e
        mu = (current.a + current.b) / 2 + e
        
        f_lamda = func(lamda)
        f_mu = func(mu)
        func_calc_count += 2
        
        # Обновляем текущую итерацию
        iterations[k].lamda = lamda
        iterations[k].mu = mu
        iterations[k].f_lamda = f_lamda
        iterations[k].f_mu = f_mu
        
        # Создаем новую итерацию
        if f_lamda < f_mu:
            next_iter = Iteration(current.a, mu, 0, 0, 0, 0)
        else:
            next_iter = Iteration(lamda, current.b, 0, 0, 0, 0)
        
        iterations.append(next_iter)
        k += 1
        
        # Проверка на зацикливание
        if k >= 3:
            if (abs(iterations[k-1].a - iterations[k-3].a) < 1e-10 and
                abs(iterations[k-1].b - iterations[k-3].b) < 1e-10 and
                abs(iterations[k-2].a - iterations[k-3].a) < 1e-10 and
                abs(iterations[k-2].b - iterations[k-3].b) < 1e-10):
                
                mid = (iterations[k-1].a + iterations[k-1].b) / 2
                result.optimal_x = mid
                result.optimal_f = func(mid)
                result.func_calculations = func_calc_count+1
                return


def golden_ratio(iterations: List[Iteration], result: ResultInfo, number_f: int) -> None:
    """Метод золотого сечения"""
    # Добавляем информацию о методе и функции
    result.select_method = "Золотое сечение"
    result.select_f = f"F{number_f}"
    
    k = 0
    func_calc_count = 0
    phi = 0.618
    
    func = select_func(number_f)
    if func is None:
        return
    
    # Начальный этап
    iterations[k].lamda = iterations[k].a + (1 - phi) * (iterations[k].b - iterations[k].a)
    iterations[k].mu = iterations[k].a + phi * (iterations[k].b - iterations[k].a)
    
    iterations[k].f_lamda = func(iterations[k].lamda)
    iterations[k].f_mu = func(iterations[k].mu)
    func_calc_count += 2
    
    while True:
        if iterations[k].b - iterations[k].a < l:# ШАГ 1
            mid = (iterations[k].a + iterations[k].b) / 2
            result.optimal_x = mid
            result.optimal_f = func(mid)
            result.func_calculations = func_calc_count
            return
        
        if iterations[k].f_lamda > iterations[k].f_mu:# ШАГ 2   
            
            new_mu = iterations[k].lamda + phi * (iterations[k].b - iterations[k].lamda)
            f_new_mu = func(new_mu)
            func_calc_count += 1
            
            next_iter = Iteration(
                a=iterations[k].lamda,
                b=iterations[k].b,
                lamda=iterations[k].mu,
                mu=new_mu,
                f_lamda=iterations[k].f_mu,
                f_mu=f_new_mu
            )
            
        else:# ШАГ 3
                 
            new_lamda = iterations[k].a + (1 - phi) * (iterations[k].mu - iterations[k].a)
            f_new_lamda = func(new_lamda)
            func_calc_count += 1
            
            next_iter = Iteration(
                a=iterations[k].a,
                b=iterations[k].mu,
                mu=iterations[k].lamda,
                lamda=new_lamda,
                f_mu=iterations[k].f_lamda,
                f_lamda=f_new_lamda
            )
        
        iterations.append(next_iter)
        k += 1
        
        # Проверка на зацикливание
        if k >= 3:
            if (abs(iterations[k-1].a - iterations[k-3].a) < 1e-10 and
                abs(iterations[k-1].b - iterations[k-3].b) < 1e-10 and
                abs(iterations[k-2].a - iterations[k-3].a) < 1e-10 and
                abs(iterations[k-2].b - iterations[k-3].b) < 1e-10):
                
                mid = (iterations[k-1].a + iterations[k-1].b) / 2
                result.optimal_x = mid
                result.optimal_f = func(mid)
                result.func_calculations = func_calc_count
                return


def fibonacci(n: int) -> int:
    """Вычисление числа Фибоначчи"""
    if n <= 1:
        return 1
    
    prev, curr = 1, 1
    for i in range(2, n + 1):
        prev, curr = curr, prev + curr
    return curr

def fibonacci_method(iterations: List[Iteration], result: ResultInfo, number_f: int) -> None:
    """Метод Фибоначчи"""
    # Добавляем информацию о методе и функции
    result.select_method = "Метод Фибоначчи"
    result.select_f = f"F{number_f}"
    
    # Находим n
    n = 1
    fib_prev, fib_curr = 1, 1
    
    while fib_curr <= (iterations[0].b - iterations[0].a) / l:
        fib_prev, fib_curr = fib_curr, fib_prev + fib_curr
        n += 1
    
    func = select_func(number_f)
    if func is None:
        return
    
    k = 0
    func_calc_count = 0
    
    # Начальные точки
    iterations[0].lamda = iterations[0].a + (fibonacci(n - 2) / fibonacci(n)) * (iterations[0].b - iterations[0].a)
    iterations[0].mu = iterations[0].a + (fibonacci(n - 1) / fibonacci(n)) * (iterations[0].b - iterations[0].a)
    
    iterations[0].f_lamda = func(iterations[0].lamda)
    iterations[0].f_mu = func(iterations[0].mu)
    func_calc_count += 2
    
    while True:
        if iterations[k].f_lamda > iterations[k].f_mu:
            # Шаг 2
            new_mu = (iterations[k].lamda + (fibonacci(n - k - 1) / fibonacci(n - k)) * (iterations[k].b - iterations[k].lamda))
            
            if k != n - 2:
                f_new_mu = func(new_mu)
                func_calc_count += 1
            else:
                f_new_mu = 0  # Значение не вычисляется на предпоследнем шаге
            
            next_iter = Iteration(
                a=iterations[k].lamda,
                b=iterations[k].b,
                lamda=iterations[k].mu,
                mu=new_mu,
                f_lamda=iterations[k].f_mu,
                f_mu=f_new_mu
            )
            
        else:
            # Шаг 3
            new_lamda = (iterations[k].a + (fibonacci(n - k - 2) / fibonacci(n - k)) * (iterations[k].mu - iterations[k].a))
            
            if k != n - 2:
                f_new_lamda = func(new_lamda)
                func_calc_count += 1
            else:
                f_new_lamda = 0  # Значение не вычисляется на предпоследнем шаге
            
            next_iter = Iteration(
                a=iterations[k].a,
                b=iterations[k].mu,
                mu=iterations[k].lamda,
                lamda=new_lamda,
                f_mu=iterations[k].f_lamda,
                f_lamda=f_new_lamda
            )
        
        iterations.append(next_iter)
        k += 1
        
        if k == n - 2:
            # Шаг 5
            last_lamda = iterations[k].lamda
            last_mu = last_lamda + e
            
            f_last_lamda = func(last_lamda)
            f_last_mu = func(last_mu)
            func_calc_count += 2
            
            last_iter = Iteration(
                a=iterations[k].a,
                b=last_mu,
                lamda=last_lamda,
                mu=last_mu,
                f_lamda=f_last_lamda,
                f_mu=f_last_mu
            )
            
            iterations.append(last_iter)
            
            result.optimal_x = (last_iter.a + last_iter.b) / 2
            result.optimal_f = func(result.optimal_x)
            result.func_calculations = func_calc_count
            return

def save_table_to_csv(iterations: List[Iteration], result: ResultInfo, method_name: str, number_f: int):
    """Сохранение таблицы итераций в CSV файл"""
    # Создаем папку results если её нет
    if not os.path.exists("results"):
        os.makedirs("results")
    
    # Генерируем имя файла с датой и временем
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"results/optimization_{method_name}_F{number_f}_{timestamp}.csv"
    
    valid_iterations = [it for it in iterations if not (it.lamda == 0 and it.mu == 0 and it.f_lamda == 0 and it.f_mu == 0 and  iterations.index(it) == 0)]
    
    # Используем utf-8 с BOM для лучшей совместимости с Excel
    with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.writer(csvfile, delimiter=';')
        
        # Параметры записываем в отдельные поля (каждый параметр в своей колонке)
        writer.writerow(['Параметр', 'Значение'])
        writer.writerow(['e', f'{e:.3f}'])
        writer.writerow(['l', f'{l:.3f}'])
        writer.writerow(['a', f'{a:.2f}'])
        writer.writerow(['b', f'{b:.2f}'])
        writer.writerow(['Метод', method_name])
        writer.writerow(['Функция', f'F{number_f}'])
        writer.writerow([])  # Пустая строка для разделения
        
        # Заголовки колонок таблицы - первый столбец увеличен
        writer.writerow(['K', 'a_k', 'b_k', 'lambda_k', 'mu_k', 'f(lambda_k)', 'f(mu_k)'])
        
        # Данные итераций
        for idx, it in enumerate(valid_iterations):
            is_last = (idx == len(valid_iterations) - 1)
            
            # Заменяем точки на запятые для чисел
            if is_last and "Фибоначчи" not in method_name:
                writer.writerow([
                    idx + 1,
                    f"{it.a:.4f}".replace('.', ','),
                    f"{it.b:.4f}".replace('.', ','),
                    '', '', '', ''
                ])
            else:
                writer.writerow([
                    idx + 1,
                    f"{it.a:.4f}".replace('.', ','),
                    f"{it.b:.4f}".replace('.', ','),
                    f"{it.lamda:.4f}".replace('.', ','),
                    f"{it.mu:.4f}".replace('.', ','),
                    f"{it.f_lamda:.4f}".replace('.', ','),
                    f"{it.f_mu:.4f}".replace('.', ',')
                ])
        
        # Результаты
        writer.writerow([])
        writer.writerow(['РЕЗУЛЬТАТЫ', ''])
        writer.writerow(['x*', f"{result.optimal_x:.4f}"])
        writer.writerow([f'F{number_f}(x*)', f"{result.optimal_f:.4f}"])
        writer.writerow(['Количество вычислений', result.func_calculations])
    
    return filename

def show_results(screen: pygame.Surface, font: pygame.font.Font, iterations: List[Iteration], result: ResultInfo, number_f: int, method_name: str) -> None:
    """Отображение результатов в pygame окне с графиком справа"""
    global save_button_rect
    
    screen.fill((255, 255, 255))
   
    width, height = 1400, 800

    # Разделительные линии (левая область уменьшена до 300px)
    pygame.draw.line(screen, (0, 0, 0), (300, 0), (300, height), 2)  # Левая граница
    pygame.draw.line(screen, (0, 0, 0), (800, 0), (800, height), 2)  # Центральная граница
    pygame.draw.line(screen, (0, 0, 0), (0, 400), (300, 400), 2)      # Горизонтальная слева
    
    # ========== ЛЕВАЯ ВЕРХНЯЯ ОБЛАСТЬ - Параметры ==========
    pygame.draw.rect(screen, (220, 220, 220), (10, 10, 280, 380), 1)
    params_title = font.render("ПАРАМЕТРЫ", True, (0, 0, 255))
    screen.blit(params_title, (20, 20))
    
    params = [
        ("e:", f"{e:.3f}"),
        ("l:", f"{l:.3f}"),
        ("[a;b]:", f"[{a:.2f}; {b:.2f}]")
    ]
    
    y_offset = 60
    for i, (label, value) in enumerate(params):
        pygame.draw.rect(screen, (0, 0, 0), (20, y_offset + i*40, 250, 30), 1)
        label_text = font.render(label, True, (0, 0, 0))
        value_text = font.render(value, True, (0, 0, 0))
        screen.blit(label_text, (25, y_offset + i*40 + 5))
        screen.blit(value_text, (150, y_offset + i*40 + 5))
    
    # ========== ЛЕВАЯ НИЖНЯЯ ОБЛАСТЬ - Действия ==========
    pygame.draw.rect(screen, (220, 220, 220), (10, 410, 280, 380), 1)
    actions_title = font.render("ДЕЙСТВИЯ", True, (0, 0, 255))
    screen.blit(actions_title, (20, 420))
    
    actions = [
        "1 - Дихотомический поиск",
        "2 - Золотое сечение",
        "3 - Метод Фибоначчи",
        "4 - Изменить e",
        "5 - Изменить l",
        "6 - Изменить [a;b]",
        "7 - Выход"
    ]
    
    for i, action in enumerate(actions):
        color = (0, 100, 0) if i < 3 else (0, 0, 0)
        action_text = font.render(action, True, color)
        screen.blit(action_text, (30, 460 + i*25))
    
    # Текущий метод и функция
    if method_name:
        method_text = font.render(f"Метод: {method_name}", True, (255, 0, 0))
        func_text = font.render(f"Функция: F{number_f}", True, (255, 0, 0))
        screen.blit(method_text, (30, 650))
        screen.blit(func_text, (30, 675))
    
    # ========== ЦЕНТРАЛЬНАЯ ОБЛАСТЬ - Таблица и результаты ==========
    # Таблица
    table_title = font.render("ТАБЛИЦА ИТЕРАЦИЙ", True, (0, 0, 255))
    screen.blit(table_title, (350, 20))
    
    headers = ["K", "a_k", "b_k", "λ_k", "μ_k", "f(λ_k)", "f(μ_k)"]
    col_widths = [35, 70, 70, 70, 70, 70, 70]
    x_start = 320
    
    for i, header in enumerate(headers):
        x_pos = x_start + sum(col_widths[:i])
        pygame.draw.rect(screen, (200, 200, 255), (x_pos, 50, col_widths[i], 30), 1)
        pygame.draw.rect(screen, (0, 0, 0), (x_pos, 50, col_widths[i], 30), 1)
        text = font.render(header, True, (0, 0, 0))
        text_rect = text.get_rect(center=(x_pos + col_widths[i]//2, 70))
        screen.blit(text, text_rect)
    
    y_offset = 85
    row_height = 25

    valid_iterations = [it for it in iterations if not (it.lamda == 0 and it.mu == 0 and it.f_lamda == 0 and it.f_mu == 0 and iterations.index(it) == 0)]
    
    for idx, it in enumerate(valid_iterations):
        if y_offset > 450:
            more_text = font.render("...", True, (255, 0, 0))
            screen.blit(more_text, (350, y_offset))
            break
        
        is_last = (idx == len(valid_iterations) - 1)
        
        if is_last and "Фибоначчи" not in method_name:
            values = [
                str(idx + 1),
                f"{it.a:.4f}",
                f"{it.b:.4f}",
                "", "", "", ""
            ]
        else:
            values = [
                str(idx + 1),
                f"{it.a:.4f}",
                f"{it.b:.4f}",
                f"{it.lamda:.4f}",
                f"{it.mu:.4f}",
                f"{it.f_lamda:.4f}",
                f"{it.f_mu:.4f}"
            ]
        
        row_color = (255, 255, 255) if idx % 2 == 0 else (245, 245, 255)
        
        for i, value in enumerate(values):
            x_pos = x_start + sum(col_widths[:i])
            pygame.draw.rect(screen, row_color, (x_pos, y_offset, col_widths[i], row_height))
            pygame.draw.rect(screen, (0, 0, 0), (x_pos, y_offset, col_widths[i], row_height), 1)
            
            if value:
                text = font.render(value, True, (0, 0, 0))
                text_rect = text.get_rect(center=(x_pos + col_widths[i]//2, y_offset + row_height//2))
                screen.blit(text, text_rect)
        
        y_offset += row_height
    
    # Результаты (под таблицей)
    result_y = 500
    result_title = font.render("РЕЗУЛЬТАТЫ ВЫЧИСЛЕНИЙ", True, (0, 0, 255))
    screen.blit(result_title, (350, result_y))
    
    pygame.draw.rect(screen, (0, 0, 0), (320, result_y + 25, 450, 100), 2)
    
    if result.optimal_x != 0 or result.optimal_f != 0:
        result_texts = [
            f"x* = {result.optimal_x:.4f}",
            f"F{number_f}(x*) = {result.optimal_f:.4f}",
            f"Вычислений: {result.func_calculations}"
        ]
        
        for i, text in enumerate(result_texts):
            rendered = font.render(text, True, (0, 0, 0))
            screen.blit(rendered, (340, result_y + 40 + i*30))
    
    
    # ========== КНОПКА СОХРАНЕНИЯ ==========
    if valid_iterations:  # Появляется только когда есть таблица
        button_rect = pygame.Rect(550, 580, 200, 30)  # x, y, width, height
        
        # Проверяем, наведена ли мышь на кнопку
        mouse_pos = pygame.mouse.get_pos()
        button_color = (0, 150, 0) if button_rect.collidepoint(mouse_pos) else (0, 100, 0)
        
        pygame.draw.rect(screen, button_color, button_rect)
        pygame.draw.rect(screen, (0, 0, 0), button_rect, 2)  # Рамка
        
        save_text = font.render("💾 Сохранить в Excel", True, (255, 255, 255))
        text_rect = save_text.get_rect(center=button_rect.center)
        screen.blit(save_text, text_rect)
        
        # Сохраняем позицию кнопки для обработки нажатий
        global save_button_rect
        save_button_rect = button_rect
    
    # ========== ПРАВАЯ ОБЛАСТЬ - График (увеличенная) ==========
    graph_title = font.render("ГРАФИК ФУНКЦИИ", True, (0, 0, 255))
    screen.blit(graph_title, (900, 20))
    
    # Область графика (увеличенная ширина)
    graph_rect = pygame.Rect(870, 50, 500, 500)
    pygame.draw.rect(screen, (0, 0, 0), graph_rect, 2)
    pygame.draw.rect(screen, (255, 255, 255), graph_rect.inflate(-2, -2))
    
    if valid_iterations and result.optimal_x != 0:
        func = select_func(number_f)
        if func:
            # Определяем границы для графика
            x_min = min(iterations[0].a, valid_iterations[-1].a)
            x_max = max(iterations[0].b, valid_iterations[-1].b)
            padding = (x_max - x_min) * 0.2
            x_min -= padding
            x_max += padding
            
            # Вычисляем значения функции
            step = (x_max - x_min) / 400
            
            # Находим min и max функции
            y_min = float('inf')
            y_max = float('-inf')
            test_points = []
            
            x = x_min
            while x <= x_max:
                try:
                    y = func(x)
                    if not math.isinf(y) and not math.isnan(y):
                        test_points.append((x, y))
                        y_min = min(y_min, y)
                        y_max = max(y_max, y)
                except:
                    pass
                x += step
            
            if y_min == float('inf'):
                y_min, y_max = -10, 10
            
            # Добавляем отступ по y
            y_padding = (y_max - y_min) * 0.2
            y_min -= y_padding
            y_max += y_padding
            
            # Масштабирование и отрисовка
            graph_width, graph_height = 496, 496
            graph_x, graph_y = 871, 51
            
            # Рисуем оси
             # Рисуем оси
            pygame.draw.line(screen, (100, 100, 100), (graph_x, graph_y), (graph_x, graph_y + graph_height), 1)
            pygame.draw.line(screen, (100, 100, 100), (graph_x, graph_y + graph_height), (graph_x + graph_width, graph_y + graph_height), 1)
            
                        # Рисуем деления и подписи по оси X
            num_ticks_x = 8
            x_step = (x_max - x_min) / num_ticks_x
            for i in range(num_ticks_x + 1):
                x_val = x_min + i * x_step
                x_screen = graph_x + int((x_val - x_min) / (x_max - x_min) * graph_width)
                
                # Вертикальная линия деления
                pygame.draw.line(screen, (200, 200, 200), (x_screen, graph_y),  (x_screen, graph_y + graph_height), 1)
                
                label = font.render(f"{x_val:.1f}", True, (0, 0, 0))
                label_rect = label.get_rect(center=(x_screen, graph_y + graph_height + 15))
                screen.blit(label, label_rect)
            
            # Рисуем деления и подписи по оси Y
            num_ticks_y = 6
            y_step = (y_max - y_min) / num_ticks_y
            for i in range(num_ticks_y + 1):
                y_val = y_min + i * y_step
                y_screen = graph_y + graph_height - int((y_val - y_min) / (y_max - y_min) * graph_height)
                
                # Горизонтальная линия деления
                pygame.draw.line(screen, (200, 200, 200), (graph_x, y_screen), (graph_x + graph_width, y_screen), 1)
                
                # Подпись значения
                label = font.render(f"{y_val:.1f}", True, (0, 0, 0))
                label_rect = label.get_rect(right=graph_x - 5, centery=y_screen)
                screen.blit(label, label_rect)
            
            # Рисуем интервалы (полупрозрачными)
            # Начальный интервал - светло-зеленый полупрозрачный
            start_a = iterations[0].a
            start_b = iterations[0].b
            a1_x = graph_x + int((start_a - x_min) / (x_max - x_min) * graph_width)
            a2_x = graph_x + int((start_b - x_min) / (x_max - x_min) * graph_width)
            
            if graph_x <= a1_x <= graph_x + graph_width:
                # Создаем полупрозрачную поверхность для заливки интервала
                interval_surface = pygame.Surface((a2_x - a1_x, graph_height), pygame.SRCALPHA)
                interval_surface.fill((0, 255, 0, 30))  # Полупрозрачный зеленый
                screen.blit(interval_surface, (a1_x, graph_y))
                
                # Рисуем границы интервала
                pygame.draw.line(screen, (0, 255, 0), (a1_x, graph_y), (a1_x, graph_y + graph_height), 2)
                pygame.draw.line(screen, (0, 255, 0), (a2_x, graph_y), (a2_x, graph_y + graph_height), 2)
            
            # Конечный интервал - светло-красный полупрозрачный
            if valid_iterations:
                last_a = valid_iterations[-1].a
                last_b = valid_iterations[-1].b
                b1_x = graph_x + int((last_a - x_min) / (x_max - x_min) * graph_width)
                b2_x = graph_x + int((last_b - x_min) / (x_max - x_min) * graph_width)
                
                if graph_x <= b1_x <= graph_x + graph_width:
                    # Создаем полупрозрачную поверхность для заливки интервала
                    interval_surface = pygame.Surface((b2_x - b1_x, graph_height), pygame.SRCALPHA)
                    interval_surface.fill((255, 0, 0, 30))  # Полупрозрачный красный
                    screen.blit(interval_surface, (b1_x, graph_y))
                    
                    # Рисуем границы интервала
                    pygame.draw.line(screen, (255, 0, 0), (b1_x, graph_y), (b1_x, graph_y + graph_height), 2)
                    pygame.draw.line(screen, (255, 0, 0), (b2_x, graph_y), (b2_x, graph_y + graph_height), 2)
            
            # Рисуем функцию (синим, но более ярко)
            for x, y in test_points:
                if y_min != y_max:
                    screen_x = graph_x + int((x - x_min) / (x_max - x_min) * graph_width)
                    screen_y = graph_y + graph_height - int((y - y_min) / (y_max - y_min) * graph_height)
                    
                    if graph_x <= screen_x <= graph_x + graph_width and graph_y <= screen_y <= graph_y + graph_height:
                        pygame.draw.circle(screen, (0, 0, 255), (screen_x, screen_y), 3)  # Чуть крупнее точки
            
            # ===== ТЕПЕРЬ РИСУЕМ ТОЧКИ И ПОДПИСИ НА ПЕРЕДНЕМ ПЛАНЕ =====
            
            # Точка оптимального значения на начальном интервале
            start_opt_x = (start_a + start_b) / 2
            start_opt_y = func(start_opt_x)
            
            start_opt_screen_x = graph_x + int((start_opt_x - x_min) / (x_max - x_min) * graph_width)
            start_opt_screen_y = graph_y + graph_height - int((start_opt_y - y_min) / (y_max - y_min) * graph_height)
            
            if (graph_x <= start_opt_screen_x <= graph_x + graph_width and 
                graph_y <= start_opt_screen_y <= graph_y + graph_height):
                # Белая обводка для точки, чтобы она была видна на любом фоне
                pygame.draw.circle(screen, (255, 255, 255), (start_opt_screen_x, start_opt_screen_y), 8)
                pygame.draw.circle(screen, (0, 150, 0), (start_opt_screen_x, start_opt_screen_y), 6)
                pygame.draw.circle(screen, (0, 0, 0), (start_opt_screen_x, start_opt_screen_y), 6, 1)
                
                # Белый фон для подписей
                label1 = font.render(f"x*={start_opt_x:.2f}", True, (0, 150, 0))
                label2 = font.render(f"F(x*)={start_opt_y:.2f}", True, (0, 150, 0))
                
                # Позиция подписи
                label_x = start_opt_screen_x - 50
                label_y = start_opt_screen_y - 45
                
                # Белый прямоугольник под текст
                pygame.draw.rect(screen, (255, 255, 255), (label_x-2, label_y-2, 100, 42))
                pygame.draw.rect(screen, (0, 150, 0), (label_x-2, label_y-2, 100, 42), 1)
                
                screen.blit(label1, (label_x, label_y))
                screen.blit(label2, (label_x, label_y + 20))
            
            # Точка оптимального значения на конечном интервале
            if valid_iterations:
                end_opt_x = (last_a + last_b) / 2
                end_opt_y = func(end_opt_x)
                
                end_opt_screen_x = graph_x + int((end_opt_x - x_min) / (x_max - x_min) * graph_width)
                end_opt_screen_y = graph_y + graph_height - int((end_opt_y - y_min) / (y_max - y_min) * graph_height)
                
                if (graph_x <= end_opt_screen_x <= graph_x + graph_width and 
                    graph_y <= end_opt_screen_y <= graph_y + graph_height):
                    # Белая обводка для точки
                    pygame.draw.circle(screen, (255, 255, 255), (end_opt_screen_x, end_opt_screen_y), 8)
                    pygame.draw.circle(screen, (200, 0, 0), (end_opt_screen_x, end_opt_screen_y), 6)
                    pygame.draw.circle(screen, (0, 0, 0), (end_opt_screen_x, end_opt_screen_y), 6, 1)
                    
                    # Белый фон для подписей
                    label1 = font.render(f"x*={end_opt_x:.2f}", True, (200, 0, 0))
                    label2 = font.render(f"F(x*)={end_opt_y:.2f}", True, (200, 0, 0))
                    
                    # Позиция подписи
                    label_x = end_opt_screen_x - 50
                    label_y = end_opt_screen_y - 45
                    
                    # Белый прямоугольник под текст
                    pygame.draw.rect(screen, (255, 255, 255), (label_x-2, label_y-2, 100, 42))
                    pygame.draw.rect(screen, (200, 0, 0), (label_x-2, label_y-2, 100, 42), 1)
                    
                    screen.blit(label1, (label_x, label_y))
                    screen.blit(label2, (label_x, label_y + 20))
    
    pygame.display.flip()
       
def menu_screen(screen: pygame.Surface, font: pygame.font.Font) -> Optional[tuple]:
    """Экран меню"""
    screen.fill((255, 255, 255))  # Полностью белый фон
    
    # Разделительные линии
    pygame.draw.line(screen, (0, 0, 0), (300, 0), (300, 800), 2)
    pygame.draw.line(screen, (0, 0, 0), (800, 0), (800, 800), 2)
    pygame.draw.line(screen, (0, 0, 0), (0, 400), (300, 400), 2)
    
    # Параметры с 2 знаками после запятой
    pygame.draw.rect(screen, (220, 220, 220), (10, 10, 280, 380), 1)
    params_title = font.render("ПАРАМЕТРЫ", True, (0, 0, 255))
    screen.blit(params_title, (20, 20))
    
    params = [
        ("e:", f"{e:.3f}"),
        ("l:", f"{l:.3f}"),
        ("[a;b]:", f"[{a:.2f}; {b:.2f}]")
    ]
    
    y_offset = 60
    for i, (label, value) in enumerate(params):
        pygame.draw.rect(screen, (0, 0, 0), (20, y_offset + i*40, 250, 30), 1)
        label_text = font.render(label, True, (0, 0, 0))
        value_text = font.render(value, True, (0, 0, 0))
        screen.blit(label_text, (25, y_offset + i*40 + 5))
        screen.blit(value_text, (150, y_offset + i*40 + 5))
    
    # Действия
    pygame.draw.rect(screen, (220, 220, 220), (10, 410, 280, 380), 1)
    actions_title = font.render("ДЕЙСТВИЯ", True, (0, 0, 255))
    screen.blit(actions_title, (20, 420))
    
    actions = [
        "1 - Дихотомический поиск",
        "2 - Золотое сечение",
        "3 - Метод Фибоначчи",
        "4 - Изменить e",
        "5 - Изменить l",
        "6 - Изменить [a;b]",
        "7 - Выход"
    ]
    
    for i, action in enumerate(actions):
        color = (0, 100, 0) if i < 3 else (0, 0, 0)
        action_text = font.render(action, True, color)
        screen.blit(action_text, (30, 460 + i*30))
    
    pygame.display.flip()
    
    # Обработка ввода (без изменений)
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return ("method", 1)
                elif event.key == pygame.K_2:
                    return ("method", 2)
                elif event.key == pygame.K_3:
                    return ("method", 3)
                elif event.key == pygame.K_4:
                    return ("param", "e")
                elif event.key == pygame.K_5:
                    return ("param", "l")
                elif event.key == pygame.K_6:
                    return ("param", "ab")
                elif event.key == pygame.K_7:
                    pygame.quit()
                    sys.exit()

def input_parameter_in_actions(screen: pygame.Surface, font: pygame.font.Font, param_name: str, current_value: float) -> float:
    """Ввод параметра в области действий"""
    global e, l  # Объявляем глобальные переменные
    input_text = ""
    error_message = ""
    error_time = 0
    
    while True:
        # Рисуем основное окно с параметрами и действиями
        screen.fill((255, 255, 255))
        
        # Разделительные линии
        pygame.draw.line(screen, (0, 0, 0), (300, 0), (300, 800), 2)
        pygame.draw.line(screen, (0, 0, 0), (800, 0), (800, 800), 2)
        pygame.draw.line(screen, (0, 0, 0), (0, 400), (300, 400), 2)
        
        # ========== ЛЕВАЯ ВЕРХНЯЯ ОБЛАСТЬ - Параметры ==========
        pygame.draw.rect(screen, (220, 220, 220), (10, 10, 280, 380), 1)
        params_title = font.render("ПАРАМЕТРЫ", True, (0, 0, 255))
        screen.blit(params_title, (20, 20))
        
        params = [
            ("e:", f"{e:.3f}"),
            ("l:", f"{l:.3f}"),
            ("[a;b]:", f"[{a:.2f}; {b:.2f}]")
        ]
        
        y_offset = 60
        for i, (label, value) in enumerate(params):
            pygame.draw.rect(screen, (0, 0, 0), (20, y_offset + i*40, 250, 30), 1)
            label_text = font.render(label, True, (0, 0, 0))
            value_text = font.render(value, True, (0, 0, 0))
            screen.blit(label_text, (25, y_offset + i*40 + 5))
            screen.blit(value_text, (150, y_offset + i*40 + 5))
        
        # ========== ЛЕВАЯ НИЖНЯЯ ОБЛАСТЬ - Ввод параметра ==========
        pygame.draw.rect(screen, (220, 220, 220), (10, 410, 280, 380), 1)
        input_title = font.render(f"ВВОД ПАРАМЕТРА {param_name}", True, (255, 0, 0))
        screen.blit(input_title, (20, 420))
        
        # Текущее значение
        current_text = font.render(f"Текущее: {current_value:.3f}", True, (0, 0, 0))
        screen.blit(current_text, (30, 460))
        
        # Поле ввода
        input_label = font.render("Новое значение:", True, (0, 0, 0))
        screen.blit(input_label, (30, 500))
        
        # Рамка для ввода
        pygame.draw.rect(screen, (0, 0, 0), (30, 530, 220, 30), 2)
        input_surface = font.render(input_text, True, (0, 0, 0))
        screen.blit(input_surface, (35, 535))
        
        # Условия для параметров
        y_cond = 570
        if param_name == "e":
            cond_text = font.render("Условие: e > 0 и 2e < l", True, (100, 100, 100))
            screen.blit(cond_text, (30, y_cond))
            current_l = font.render(f"Текущее l = {l:.3f}", True, (100, 100, 100))
            screen.blit(current_l, (30, y_cond + 25))
            max_e = l / 2
            max_e_text = font.render(f"Максимальное e: {max_e:.3f}", True, (100, 100, 100))
            screen.blit(max_e_text, (30, y_cond + 50))
        elif param_name == "l":
            cond_text = font.render("Условие: l > 0 и 2e < l", True, (100, 100, 100))
            screen.blit(cond_text, (30, y_cond))
            current_e = font.render(f"Текущее e = {e:.3f}", True, (100, 100, 100))
            screen.blit(current_e, (30, y_cond + 25))
            min_l = 2 * e
            min_l_text = font.render(f"Минимальное l: {min_l:.3f}", True, (100, 100, 100))
            screen.blit(min_l_text, (30, y_cond + 50))
        
        # Сообщение об ошибке
        if error_message and pygame.time.get_ticks() - error_time < 3000:  # Показываем 3 секунды
            error_text = font.render(error_message, True, (255, 0, 0))
            screen.blit(error_text, (30, y_cond + 80))
        
        # Инструкция
        instr1 = font.render("Enter - подтвердить", True, (0, 100, 0))
        instr2 = font.render("Esc - отмена", True, (255, 0, 0))
        screen.blit(instr1, (30, y_cond + 110))
        screen.blit(instr2, (30, y_cond + 135))
        
        pygame.display.flip()
        
        # Обработка ввода
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and input_text:
                    try:
                        new_value = float(input_text)
                        
                        # Проверка условий
                        valid = True
                        if param_name == "e":
                            if new_value <= 0:
                                error_message = f"Ошибка: e должно быть > 0"
                                valid = False
                            elif 2 * new_value >= l:
                                error_message = f"Ошибка: 2e ({2*new_value:.3f}) должно быть < l ({l:.3f})"
                                valid = False
                        elif param_name == "l":
                            if new_value <= 0:
                                error_message = f"Ошибка: l должно быть > 0"
                                valid = False
                            elif 2 * e >= new_value:
                                error_message = f"Ошибка: 2e ({2*e:.3f}) должно быть < l ({new_value:.3f})"
                                valid = False
                        
                        if valid:
                            # Обновляем глобальную переменную
                            if param_name == "e":
                                e = new_value
                            else:
                                l = new_value
                            return new_value
                        else:
                            error_time = pygame.time.get_ticks()
                            input_text = ""
                    except ValueError:
                        error_message = "Ошибка: введите число"
                        error_time = pygame.time.get_ticks()
                        input_text = ""
                elif event.key == pygame.K_ESCAPE:
                    return current_value
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                elif event.unicode.isdigit() or event.unicode == '.' or (event.unicode == '-' and not input_text):
                    input_text += event.unicode

def input_two_parameters_in_actions(screen: pygame.Surface, font: pygame.font.Font) -> tuple:
    """Ввод двух параметров a и b в области действий"""
    inputs = ["", ""]
    current_input = 0
    param_names = ["a", "b"]
    
    while current_input < 2:
        screen.fill((255, 255, 255))
        
        # Разделительные линии
        pygame.draw.line(screen, (0, 0, 0), (300, 0), (300, 800), 2)
        pygame.draw.line(screen, (0, 0, 0), (800, 0), (800, 800), 2)
        pygame.draw.line(screen, (0, 0, 0), (0, 400), (300, 400), 2)
        
        # ========== ЛЕВАЯ ВЕРХНЯЯ ОБЛАСТЬ - Параметры ==========
        pygame.draw.rect(screen, (220, 220, 220), (10, 10, 280, 380), 1)
        params_title = font.render("ПАРАМЕТРЫ", True, (0, 0, 255))
        screen.blit(params_title, (20, 20))
        
        params = [
            ("e:", f"{e:.3f}"),
            ("l:", f"{l:.3f}"),
            ("[a;b]:", f"[{a:.2f}; {b:.2f}]")
        ]
        
        y_offset = 60
        for i, (label, value) in enumerate(params):
            pygame.draw.rect(screen, (0, 0, 0), (20, y_offset + i*40, 250, 30), 1)
            label_text = font.render(label, True, (0, 0, 0))
            value_text = font.render(value, True, (0, 0, 0))
            screen.blit(label_text, (25, y_offset + i*40 + 5))
            screen.blit(value_text, (150, y_offset + i*40 + 5))
        
        # ========== ЛЕВАЯ НИЖНЯЯ ОБЛАСТЬ - Ввод параметров ==========
        pygame.draw.rect(screen, (220, 220, 220), (10, 410, 280, 380), 1)
        input_title = font.render(f"ВВОД ПАРАМЕТРА {param_names[current_input]}", True, (255, 0, 0))
        screen.blit(input_title, (20, 420))
        
        # Текущие значения
        current_text = font.render(f"Текущее a: {a:.2f}, b: {b:.2f}", True, (0, 0, 0))
        screen.blit(current_text, (30, 460))
        
        # Поле ввода
        input_label = font.render(f"Новое значение {param_names[current_input]}:", True, (0, 0, 0))
        screen.blit(input_label, (30, 500))
        
        # Рамка для ввода
        pygame.draw.rect(screen, (0, 0, 0), (30, 530, 220, 30), 2)
        input_surface = font.render(inputs[current_input], True, (0, 0, 0))
        screen.blit(input_surface, (35, 535))
        
        # Инструкция
        instr1 = font.render("Enter - подтвердить", True, (0, 100, 0))
        instr2 = font.render("Esc - отмена", True, (255, 0, 0))
        screen.blit(instr1, (30, 570))
        screen.blit(instr2, (30, 600))
        
        pygame.display.flip()
        
        # Обработка ввода
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and inputs[current_input]:
                    try:
                        value = float(inputs[current_input])
                        if current_input == 0:
                            a_new = value
                            current_input = 1
                        else:
                            b_new = value
                            return a_new, b_new
                    except ValueError:
                        inputs[current_input] = ""
                elif event.key == pygame.K_ESCAPE:
                    return a, b
                elif event.key == pygame.K_BACKSPACE:
                    inputs[current_input] = inputs[current_input][:-1]
                elif event.unicode.isdigit() or event.unicode == '.' or (event.unicode == '-' and not inputs[current_input]):
                    inputs[current_input] += event.unicode
                    
def wait_for_input_in_results(screen: pygame.Surface, font: pygame.font.Font) -> None:
    """Ожидание ввода в режиме отображения результатов"""
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    waiting = False
                    
def select_function_for_method(screen: pygame.Surface, font: pygame.font.Font, method_name: str) -> int:
    """Отображение выбора функции и ожидание ввода"""
    while True:
        screen.fill((255, 255, 255))
        
        # Разделительные линии
        pygame.draw.line(screen, (0, 0, 0), (300, 0), (300, 800), 2)  # Левая граница
        pygame.draw.line(screen, (0, 0, 0), (800, 0), (800, 800), 2)  # Центральная граница
        pygame.draw.line(screen, (0, 0, 0), (0, 400), (300, 400), 2)   # Горизонтальная слева
        
        # Параметры
        pygame.draw.rect(screen, (220, 220, 220), (10, 10, 280, 380), 1)
        params_title = font.render("ПАРАМЕТРЫ", True, (0, 0, 255))
        screen.blit(params_title, (20, 20))
        
        params = [
            ("e:", f"{e:.3f}"),
            ("l:", f"{l:.3f}"),
            ("[a;b]:", f"[{a:.2f}; {b:.2f}]")
        ]
        
        y_offset = 60
        for i, (label, value) in enumerate(params):
            pygame.draw.rect(screen, (0, 0, 0), (20, y_offset + i*40, 250, 30), 1)
            label_text = font.render(label, True, (0, 0, 0))
            value_text = font.render(value, True, (0, 0, 0))
            screen.blit(label_text, (25, y_offset + i*40 + 5))
            screen.blit(value_text, (150, y_offset + i*40 + 5))
        
        # Действия - МЕНЮ ВЫБОРА ФУНКЦИИ
        pygame.draw.rect(screen, (220, 220, 220), (10, 410, 280, 380), 1)
        actions_title = font.render(f"ВЫБЕРИТЕ ФУНКЦИЮ", True, (255, 0, 0))
        screen.blit(actions_title, (20, 420))
        
        functions = [
            f"Метод: {method_name}",
            "",
            "1 - F1(x) = (x-4)/(x-9)",
            "2 - F2(x) = |x² - 1|",
            "3 - F3(x) = x² + 2x",
            "",
            "ESC - отмена"
        ]
        
        for i, func in enumerate(functions):
            if i == 0:
                color = (0, 0, 255)
            elif 2 <= i <= 4:
                color = (0, 100, 0)
            else:
                color = (255, 0, 0)
            func_text = font.render(func, True, color)
            screen.blit(func_text, (30, 460 + i*30))
        
        pygame.display.flip()
        
        # Ожидание выбора функции
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return 1
                elif event.key == pygame.K_2:
                    return 2
                elif event.key == pygame.K_3:
                    return 3
                elif event.key == pygame.K_ESCAPE:
                    return 0

def main():
    """Главная функция программы"""
    global e, l, a, b, save_button_rect  # Добавьте save_button_rect
    save_button_rect = None
    # Инициализация pygame
    pygame.init()
    screen = pygame.display.set_mode((1400, 800))
    pygame.display.set_caption("Методы оптимизации")
    font = pygame.font.Font(None, 24)
    
    clock = pygame.time.Clock()
    
    # Словарь методов
    methods = {
        1: (dihotomy_search, "Дихотомический поиск"),
        2: (golden_ratio, "Золотое сечение"),
        3: (fibonacci_method, "Метод Фибоначчи")
    }
    
    # Переменные для хранения текущих результатов
    current_iterations = []
    current_result = ResultInfo("", "", 0, 0, 0)
    current_method_name = ""
    current_func_num = 0
    results_available = False
    save_button_rect = None  # Инициализируем здесь
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # Обработка клика мыши
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if results_available and save_button_rect:
                    if save_button_rect.collidepoint(event.pos):
                        filename = save_table_to_csv(current_iterations, current_result, current_method_name, current_func_num)
                        print(f"Таблица сохранена в файл: {filename}")
            
            # Обработка клавиш
            if event.type == pygame.KEYDOWN:
                if results_available:
                    if event.key == pygame.K_4:
                        e = input_parameter_in_actions(screen, font, "e", e)
                        # Пересчитываем с новыми параметрами
                        if current_method_name and current_func_num:
                            iterations = [Iteration(a, b, 0, 0, 0, 0)]
                            result = ResultInfo("", "", 0, 0, 0)
                            
                            # Находим метод по имени
                            for num, (func, name) in methods.items():
                                if name == current_method_name:
                                    methods[num][0](iterations, result, current_func_num)
                                    break
                            
                            current_iterations = iterations
                            current_result = result
                    
                    elif event.key == pygame.K_5:
                        l = input_parameter_in_actions(screen, font, "l", l)
                        # Пересчитываем с новыми параметрами
                        if current_method_name and current_func_num:
                            iterations = [Iteration(a, b, 0, 0, 0, 0)]
                            result = ResultInfo("", "", 0, 0, 0)
                            
                            for num, (func, name) in methods.items():
                                if name == current_method_name:
                                    methods[num][0](iterations, result, current_func_num)
                                    break
                            
                            current_iterations = iterations
                            current_result = result
                    
                    elif event.key == pygame.K_6:
                        a, b = input_two_parameters_in_actions(screen, font)
                        # Пересчитываем с новыми параметрами
                        if current_method_name and current_func_num:
                            iterations = [Iteration(a, b, 0, 0, 0, 0)]
                            result = ResultInfo("", "", 0, 0, 0)
                            
                            for num, (func, name) in methods.items():
                                if name == current_method_name:
                                    methods[num][0](iterations, result, current_func_num)
                                    break
                            
                            current_iterations = iterations
                            current_result = result
                    
                    elif event.key == pygame.K_7:
                        pygame.quit()
                        sys.exit()
                
                # Эти клавиши работают всегда
                if event.key == pygame.K_1 or event.key == pygame.K_2 or event.key == pygame.K_3:
                    # Выбор нового метода
                    method_num = event.key - pygame.K_0
                    selected_func = select_function_for_method(screen, font, methods[method_num][1])
                    
                    if selected_func > 0:
                        iterations = [Iteration(a, b, 0, 0, 0, 0)]
                        result = ResultInfo("", "", 0, 0, 0)
                        
                        methods[method_num][0](iterations, result, selected_func)
                        
                        current_iterations = iterations
                        current_result = result
                        current_method_name = methods[method_num][1]
                        current_func_num = selected_func
                        results_available = True
        
        # Всегда показываем последние результаты (если они есть)
        if results_available:
            show_results(screen, font, current_iterations, current_result, current_func_num, current_method_name)
        else:
            # Если результатов нет, показываем меню
            action = menu_screen(screen, font)
            
            if action[0] == "method":
                method_num = action[1]
                
                # Выбор функции
                selected_func = select_function_for_method(screen, font, methods[method_num][1])
                
                if selected_func > 0:  # Если функция выбрана
                    # Запускаем метод
                    iterations = [Iteration(a, b, 0, 0, 0, 0)]
                    result = ResultInfo("", "", 0, 0, 0)
                    
                    methods[method_num][0](iterations, result, selected_func)
                    
                    # Сохраняем результаты
                    current_iterations = iterations
                    current_result = result
                    current_method_name = methods[method_num][1]
                    current_func_num = selected_func
                    results_available = True
            
            elif action[0] == "param":
                if action[1] == "e":
                    e = input_parameter_in_actions(screen, font, "e", e)
                elif action[1] == "l":
                    l = input_parameter_in_actions(screen, font, "l", l)
                elif action[1] == "ab":
                    a, b = input_two_parameters_in_actions(screen, font)
        
        clock.tick(60)
    
    pygame.quit()
    sys.exit()
    
if __name__ == "__main__":
    main()