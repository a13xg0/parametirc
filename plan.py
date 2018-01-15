# -*- coding: utf-8 -*-
from __future__ import division
import sys
import copy
from task import Task


class Plan:
    """ Класс-контейнер для текущего плана"""

    def __init__(self, source=None):
        """
        Конструктор класса плана

        Если указан параметер source, то выполнятеся копирование если источник был типа Plan
        :param source: исходный план для копирования значений
        :type source: Plan
        """

        self.B = []
        """ Индексы базисных переменных """

        self.A = [[]]
        """ Матрица коэффициентов уравнения """

        self.alpha = []
        """ Оценка каждого столбца. комплесное число"""

        self.ai0 = []
        """ Свободные коэффициенты """

        self.sigma = []
        """ Оценки базисных переменных """

        self.task = None
        """ Исходная задача """

        self.z = None
        """ Значение целевой функции в текущем плане """

        self.last_error = ""
        """ Текст последней ошибки """

        if source is not None:
            if not(isinstance(source, Plan)):
                self.last_error = "Источник не типа Plan"
                return

            self.B = copy.copy(source.B)
            self.A = copy.deepcopy(source.A)
            self.alpha = copy.copy(source.alpha)
            self.alpha = copy.copy(source.alpha)
            self.ai0 = copy.copy(source.ai0)
            self.task = source.task

            for i in range(self.task.m, 0, -1):
                self.sigma.append(None)

    def set_task(self, source_task):
        """
        Установка задачи плана и инициализация

        :param source_task: Исходная задача для установки параметров
        :type source_task: Task
        """

        if not isinstance(source_task, Task):
            self.last_error = "Задача не типа Task"
            return False

        self.task = source_task

        self.A = copy.deepcopy(self.task.A)

        for i in range(self.task.m, 0, -1):
            k = self.task.n - i
            # Сохраняем в качестве исходных базисных переменных последние переменные в векторе X
            self.B.append(k)

            # Заполняем свободные коэффициенты плана
            self.ai0.append(self.task.X[k])

            self.sigma.append(None)

        for i in range(0, self.task.n):
            self.alpha.append(None)

        self.last_error = ""
        return True

    def calc_alpha_assessment(self):
        """ Пересчитать оценки переменных """
        for j in range(0, self.task.n):

            self.alpha[j] = 0
            for i in range(0, self.task.m):
                self.alpha[j] += self.task.C[self.B[i]] * self.A[i][j]

            self.alpha[j] -= self.task.C[j]

    def calc_sigma(self, col=0):
        """
        Посчитать оценки строк

        :param col: Столбец по которому оцениваем коэффициет
        :type col: Integer

        """
        for i in range(0, self.task.m):
            if self.A[i][col] > 0:
                self.sigma[i] = self.ai0[i] / self.A[i][col]
            else:
                self.sigma[i] = None

    def calc_z(self):
        """ Посчитать значение целевой функции в плане """
        self.z = 0

        for i in range(0, self.task.m):
            self.z += self.task.C[self.B[i]] * self.ai0[i]

        return self.z

    def is_optimal(self, L=None):
        """ Проверка плана на оптимальность """
        if L is None:
            for i in range(0, self.task.n):
                if round(self.alpha[i].imag, 10) != 0:
                    # если пристутствует параметр, то план не известо оптимален или нет
                    return False
                if round(self.alpha[i].real, 10) < 0:
                    return False

        else:
            for i in range(0, self.task.n):
                val = round(self.alpha[i].real + self.alpha[i].imag * L, 10)
                if val < 0:
                    return False

        return True

    def is_only_l(self):
        """ В оценках плана нет отрицательнцх целх значений, остались только значения L """
        for i in range(0, self.task.n):
            if round(self.alpha[i].real) < 0 and round(self.alpha[i].imag) == 0:
                return False

        for i in range(0, self.task.n):
            if round(self.alpha[i].imag) != 0:
                return True

        return False

    def is_solvable(self, L=None):
        """ Оценить разрешимость плана, в случае неоптимальности плана, проверка на возможность перехода """
        if L is None:
            for j in range(0, self.task.n):
                if self.alpha[j].real < 0:
                    # если оценка отрицательна, то проверяем столбцы
                    is_good = False # предполагаем худший вариант, что нет положительных элементов в столбце
                    for i in range(0, self.task.m):
                        if self.A[i][j] > 0:
                            is_good = True
                            break

                    if not is_good:
                        # нашёлся столбец без положительных коэффициентов
                        return False
        else:
            for j in range(0, self.task.n):
                if self.alpha[j].real + self.alpha[j].imag * L< 0:
                    # если оценка отрицательна, то проверяем столбцы
                    is_good = False # предполагаем худший вариант, что нет положительных элементов в столбце
                    for i in range(0, self.task.m):
                        if self.A[i][j] > 0:
                            is_good = True
                            break

                    if not is_good:
                        # нашёлся столбец без положительных коэффициентов
                        return False
        return True

    ############################
    #                          #
    # МЕТОДЫ ОФОРМЛЕНИЯ ВЫВОДА #
    #                          #
    ############################
    def sign_M(self, digit):
        if digit == 0:
            return "0"
        elif digit == 1:
            return "+L"
        elif digit == -1:
            return "-L"
        else:
            return '{:>+7.2f}L'.format(digit)

    def format_M(self, digit):
        out = ""
        if type(digit) is complex:
            if digit.real == 0:
                out = '{:^15s}'.format(self.sign_M(digit.imag))
            elif round(digit.imag, 5) == 0:
                out = '{:^15.2f}'.format(digit.real)
            else:
                out = '{:>4.2f}{:>4s}'.format(digit.real, self.sign_M(digit.imag))
        elif type(digit) is str:
            out = '{:^15s}'.format(digit)
        elif digit is None:
            out = '{:^15s}'.format('-')
        else:
            out = '{:^15.2f}'.format(digit)

        return out

    def format_variable_name(self, i):
        out = "x[" + str(i + 1) + "]"

        return out

    def print_hline(self, sym):
        print
        sys.stdout.write('+')
        for i in range(0, (self.task.n + 4)*16 - 1):
            sys.stdout.write(sym)
        sys.stdout.write('+')
        print

    def out_column_str(self, s):
        sys.stdout.write('{:^15s}|'.format(s))

    def print_plan(self):
        """ Вывод плана на экран """
        # вывод коэффициентов для симплексной таблицы
        # пропустим два стоблца
        sys.stdout.write('{:>33}'.format('|'))
        for i in range(0, self.task.n):
            self.out_column_str(self.format_M(self.task.C[i]))

        self.print_hline('-')

        # шапка таблицы
        sys.stdout.write('|')
        self.out_column_str('C[i]')
        self.out_column_str('B')

        for i in range(0, self.task.n):
            self.out_column_str(self.format_variable_name(i))

        self.out_column_str('ai[0]')
        self.out_column_str('sigma')
        self.print_hline('=')

        first = True
        for i in range(0, self.task.m):
            if first:
                first = False
            else:
                print
            sys.stdout.write('|')
            self.out_column_str(self.format_M(self.task.C[self.B[i]]))
            self.out_column_str(self.format_variable_name(self.B[i]))

            for j in range(0, self.task.n):
                self.out_column_str(self.format_M(self.A[i][j]))

            self.out_column_str(self.format_M(self.ai0[i]))
            self.out_column_str(self.format_M(self.sigma[i]))

        self.print_hline('-')
        sys.stdout.write('|')
        self.out_column_str("")
        self.out_column_str("alpha_j")
        for i in range(0, self.task.n):
            self.out_column_str(self.format_M(self.alpha[i]))

        self.out_column_str(self.format_M(self.z))
        self.out_column_str("Z")

        self.print_hline('=')
        print

