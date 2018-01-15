# -*- coding: utf-8 -*-
from __future__ import division
from plan_factory import PlanFactory
from solution import Solution
import copy
import sys


class Solver:
    """ Управляет ходом решения симплексным методом """

    def __init__(self, task):
        """
        Конструктор класса решателя

        :param task: задача для решения
        :type task: Task
        """

        self.task = task

    def calc_A(self, new_plan, plan, row, col):
        """ Пересчёт коэффициентов относительно разрешающего элемента"""
        # вычисляем элементы разрешающей строки
        for i in range(0, self.task.n):
            new_plan.A[row][i] /= plan.A[row][col]

        # обнуляем элементы разрешающего столбца
        rows = list(range(self.task.m))
        del rows[row]
        for i in rows:
            new_plan.A[i][col] = 0

        # вычисляем оставшиеся элементы
        cols = list(range(self.task.n))
        del cols[col]
        for i in rows:
            for j in cols:
                new_plan.A[i][j] = (plan.A[i][j] * plan.A[row][col] - plan.A[i][col] * plan.A[row][j]) / plan.A[row][col]

        # вычисляем ai0
        new_plan.ai0[row] /= plan.A[row][col]
        for i in rows:
            new_plan.ai0[i] = (plan.ai0[i] * plan.A[row][col] - plan.A[i][col] * plan.ai0[row]) / plan.A[row][col]

        # обновляем базисные переменные
        new_plan.B[row] = col

        return new_plan

    def get_solve_col(self, alpha, L=None):
        """ Выбор разрешающего столбца """
        solve_col = None

        if L is None:
            # проверяем, есть ли реальные отрицательные столбцы
            solve_val = alpha[0].real
            for i in range(self.task.n):
                if alpha[i].imag == 0 and alpha[i].real < 0:
                    if alpha[i].real <= solve_val:
                        solve_col = i
                        solve_val = alpha[i].real

            if solve_col is None:
                # остались только столбцы с L
                for i in range(self.task.n):
                    # возвращаем первое значение
                    if alpha[i].imag != 0:
                        solve_col = i
                        break
        else:
            # подставляем значение L и вычисляем на равне со всеми
            solve_val = alpha[0].real + alpha[0].imag * L
            for i in range(self.task.n):
                tmp_val = alpha[0].real + alpha[0].imag * L
                if tmp_val < 0:
                    if tmp_val < solve_val:
                        solve_col = i
                        solve_val = tmp_val

        return solve_col

    def get_solve_col_lambda(self, alpha, initial_col=0):
        """ Выбор разрешающего столбца только с L"""
        solve_col = None
        for i in range(initial_col, self.task.n):
            if alpha[i].imag != 0:
                return i

        return solve_col

    def get_solve_row(self, plan, solve_col):
        """ Выбор разрешающего столбца """
        row_chosen = False
        sigma_col = solve_col
        plan.calc_sigma(sigma_col)

        solve_row = 0
        solve_val = plan.sigma[0]
        # print "simga"
        # print plan.sigma
        while not row_chosen:
            for i in range(0, self.task.m):
                if plan.sigma[i] is not None:
                    solve_row = i
                    solve_val = plan.sigma[i]
                    break

            possible_cycle = False

            for i in range(solve_row + 1, self.task.m):
                if (plan.sigma[i] is not None) and (plan.sigma[i] <= solve_val):
                    if plan.sigma[i] == solve_val:
                        possible_cycle = True
                    else:
                        possible_cycle = False

                    solve_row = i
                    solve_val = plan.sigma[i]

            if possible_cycle:
                if sigma_col == solve_col:
                    if solve_col == 0:
                        sigma_col = 1
                    else:
                        sigma_col = 0
                else:
                    sigma_col += 1
                    if sigma_col == solve_col:
                        # мы уже проверяли рарешающий столбец
                        sigma_col += 1

                    if sigma_col > self.task.n:
                        # все стоблцы проверили и всё равно возможно зацикливание
                        # разрешающией строкой отсавляем последнюю найденную
                        row_chosen = True
                        continue

                # пересчитываем оценку сигма
                plan.calc_sigma(sigma_col)
            else:
                # если возмоного зацикливания нет
                row_chosen = True

        return solve_row

    def transition(self, plan):
        """ Переход к более оптимальному плану"""
        new_plan = PlanFactory.from_plan(plan)
        plan.calc_alpha_assessment()
        # выбираем разрешающий столбец
        solve_col = self.get_solve_col(plan.alpha)
        return self.transition_by_col(plan, new_plan, solve_col)

    def transition_by_col(self, plan, new_plan, solve_col):
        # выбираем разрешающую строку
        solve_row = self.get_solve_row(plan, solve_col)

        # print solve_row
        # print solve_col
        return self.calc_A(new_plan, plan, solve_row, solve_col)

    def analyse_interval(self, left_point, right_point, parent, plan):
        current_solution = Solution(left_point, right_point, [], [], None, None, parent)
        s = 0
        first_pass = True
        while not plan.is_optimal() and (not plan.is_only_l() or first_pass):
            s += 1
            first_pass = False
            if s > 100:
                current_solution.insolvable_reason = "Возможно зацикливание!"
                print current_solution.insolvable_reason
                return current_solution

            print "План не оптимален"

            if not plan.is_solvable():
                current_solution.insolvable_reason = "Задача не разрешима из-за неогрниченности целевой функции в области допустимых решений"
                print current_solution.insolvable_reason
                return current_solution

            # задача разрешима, переходим к новому плану

            plan = self.transition(plan)
            plan.calc_alpha_assessment()
            plan.calc_z()
            solve_col = self.get_solve_col(plan.alpha)
            plan.calc_sigma(solve_col)

            print "Текущий план: "
            plan.print_plan()

        current_solution.X_opt = []
        for i in range(0, self.task.n):
            if i in plan.B:
                current_solution.X_opt.append(plan.ai0[plan.B.index(i)])
            else:
                current_solution.X_opt.append(0)

        current_solution.Z_max = plan.z

        print "Разбиваем интервал ({0}, {1})".format(left_point, right_point)

        solve_col = self.get_solve_col_lambda(plan.alpha)

        while solve_col is not None:
            split_point = -plan.alpha[solve_col].real / plan.alpha[solve_col].imag


            # проверяем вхождение точки в заданный интервал
            if not (split_point > left_point and split_point < right_point):
                # есть ли ещё решение с параметром, попробуем разбить и этот интервал
                solve_col = self.get_solve_col_lambda(plan.alpha, solve_col + 1)
                continue
            print "Точка разделения: {0:^8.2f}".format(split_point)
            # если слева или с права от текущей токи занчение отрицательно, то, соотвественно запускаем процесс расчёта
            # для подинтервала

            current_solution.left_child = copy.deepcopy(current_solution)
            current_solution.right_child = copy.deepcopy(current_solution)
            current_solution.left_child.right_point = split_point
            current_solution.right_child.left_point = split_point

            # левая точка
            lp = split_point - 0.000001
            if plan.alpha[solve_col].real + plan.alpha[solve_col].imag * lp < 0:
                current_solution.left_child = self.analyse_interval(left_point, split_point, current_solution, plan)

            # правая точка
            rp = split_point + 0.000001
            if plan.alpha[solve_col].real + plan.alpha[solve_col].imag * rp < 0:
                current_solution.right_child = self.analyse_interval(split_point, right_point, current_solution, plan)
            else:
                current_solution.right_child = None
            break

        current_solution.insolvable = False

        return current_solution

    def print_leafs(self, node):
        if node.left_child is None and node.right_child is None:
            print "Интервал ({0:^8.2f}, {1:^8.2f})".format(node.left_point, node.right_point)
            print "X"
            for i in range(0, self.task.n):
                sys.stdout.write("%8.3f" % node.X_opt[i])

            if self.task.target == 'min':
                node.Z_max = node.Z_max * -1

            print "\nZ = {0}".format(node.Z_max)
            print "------------------------------"
            print

        if node.left_child is not None:
            self.print_leafs(node.left_child)

        if node.right_child is not None:
            self.print_leafs(node.right_child)



    def solve(self):
        """ Выполнить решение симплесным методом """

        # если решаем задачу на минимум, то умножаем все коэффициенты в Z на -1
        # а затем результат на -1
        if self.task.target == 'min':
            self.task.C[:] = [x * -1 for x in self.task.C]

        # инициализируем базисный план
        plan = PlanFactory.from_task(self.task)

        plan.calc_alpha_assessment()
        plan.calc_z()

        solve_col = self.get_solve_col(plan.alpha)
        plan.calc_sigma(solve_col)

        print "Исходный опроный план: "
        plan.print_plan()

        current_left = -float("inf")
        current_right = float("inf")

        solution_root = self.analyse_interval(current_left, current_right, None, plan)

        # Обходим дерево решений и листья будут нашими ответами

        print "========================="
        print "Найденое решение"
        print "========================="

        self.print_leafs(solution_root)

        print "========================="

        return True


