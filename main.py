# -*- coding: utf-8 -*-
import sys
from task import Task
from solver import Solver

print "Параметрическое программирование"
print "Студент группы ПО(м)-71"
print "Горбач Александр"

if len(sys.argv) < 2:
    print "Необходимо указать файл с входными данными в качестве первого аргумента программы"
    exit(1)

task = Task()
if not task.load(sys.argv[1]):
    print "Ошибка загрузки файла задания:"
    print task.last_error
    exit(2)

# plan = PlanFactory.from_task(task)

solver = Solver(task)
solver.solve()


