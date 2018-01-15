# -*- coding: utf-8 -*-
from plan import Plan


class PlanFactory:
    """ Набор фабричных методов для генерации планов """

    @staticmethod
    def from_task(task):
        """ Инициализация плана из задачи """
        plan = Plan()
        plan.set_task(task)

        return plan

    @staticmethod
    def from_plan(plan):
        """ Инициализация плана из плана """
        plan = Plan(plan)

        return plan

