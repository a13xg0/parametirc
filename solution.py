# -*- coding: utf-8 -*-
from __future__ import division
import sys
import copy


class Solution:
    """ Класс-контейнер для одного из решений плана. Спомощью указателей формирует дерево решений """

    def __init__(self, left_point=None, right_point=None, X_opt=None, Z_max=None, left_child=None, right_child=None, parent=None):
        """
        Конструктор
        """

        self.left_point = left_point
        """ Левая точка интервала """

        self.right_point = right_point
        """ Правая точка интервала """

        self.X_opt = X_opt
        """ Значенеи коэффициентов для решения """

        self.Z_max = Z_max
        """ Значение функции в точке """

        self.left_child = left_child
        """ Левый дочерний подитнетрвал"""

        self.right_child = right_child
        """ Правый дочерний подинтервал """

        self.parent = parent
        """ Родительский подинтервал """

        self.insolvable = True
        self.insolvable_reason = "default"
