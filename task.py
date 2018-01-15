# -*- coding: utf-8 -*-
import json


class Task:
    """ Класс-контейнер для задачи, так же содержит ссылку на решение
        В дополнение умеет считывать файл с заданием
    """

    def __init__(self):
        self.n = 0
        """ Число переменных """
        self.m = 0
        """ Число ограничений """

        self.A = [[]]
        """ Матрица коэффициентов в системе уравнений, двумерный массив """
        self.X = []
        """ Вектор свободных членов """
        self.C = []
        """ Коэффициенты целевой функции """
        self.target = "max"
        """ Цель задачи, решаем на миниум или на максимум. Возможные значение min и max"""

        self.last_error = ""
        """ Текст последней ошибки """

    def load(self, file_name):
        """ Загрузка класса задачи из файла задания """
        with open(file_name, 'r') as f:
            data = json.load(f)
            return self.initialize(data['n'], data['m'], data['A'], data['X'], data['C'], data['target'])

    def initialize(self, n, m, A, X, C, target):
        """ Инициализирует класс начальными значениями """
        if len(C) != n:
            self.last_error = "Длина C не соответствует количеству переменных"
            return False

        if len(X) != n:
            self.last_error = "Длина X не соответствует количеству переменных"
            return False

        if len(A) != m:
            self.last_error = "Длина A не соответствует заявленному количеству ограничений"
            return False

        i = 0
        for row in A:
            if len(row) != n:
                self.last_error = "Длина A[" + str(i) + "] не соотвествует количесту переменных"
                return False
            i += 1

        for i in range(0, n):
            C[i] = complex(C[i])

        self.n = n
        self.m = m
        self.X = X
        self.C = C
        self.A = A
        self.target = target

        self.last_error = ""
        return True

