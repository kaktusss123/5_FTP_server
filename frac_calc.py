def mult(a, b):
    """
    Функция умножения дробей
    Дроби a, b в виде кортежа
    Числитель на числитель, знаменатель на знаменатель
    """
    return tuple(a[i] * b[i] for i in range(2))


def summ(a, b):
    """
    Суммирование дробей.
    Дроби в виде кортежа
    """
    # Если разные знаменатели, то приводим к одному
    if a[1] != b[1]:
        a, b = tuple(a[i]*b[1] for i in range(2)), tuple(b[i]*a[1]
                                                         for i in range(2))
    ret_tuple = (a[0]+b[0], a[1])
    return ret_tuple


def minus(a, b):
    """
    Вычитание дробей.
    Дроби в виде кортежа
    """
    # Со знаменателем то же самое, что и в сложении
    if a[1] != b[1]:
        a, b = tuple(a[i]*b[1] for i in range(2)), tuple(b[i]*a[1]
                                                         for i in range(2))
    ret_tuple = (a[0]-b[0], a[1])
    return ret_tuple


def divide(a, b):
    """
    Деление дробей.
    Дроби в виде кортежа
    Умножаем первую на перевернутую вторую
    """
    ret_tuple = (a[0]*b[1], a[1]*b[0])
    return ret_tuple


def str_to_tuple(str_frac):
    """
    Функция, переводящая строковую дробь в кортеж
    """
    # Если дробь отрицательная, мы запомним знак, а пока будем считать, что она положительная
    if str_frac.startswith('-'):
        sign = -1
        str_frac = str_frac[1:]
    else:
        sign = 1
    try:
        # Если дробь смешанная, то
        cel = int(str_frac[:str_frac.index('(')])  # Целая часть
        ret_lst = [int(i) for i in str_frac[str_frac.index(
            '(') + 1: -1].split('/')]  # нецелые части
        ret_lst[0] = ret_lst[0] + cel*ret_lst[1]
        frac = [i for i in ret_lst]
        # Не забываем изменить знак числителя
        frac[0] *= sign
        return tuple(frac)
    except ValueError:
        # Если у нас вообще дробь, а не число
        if '/' in str_frac:
            frac = [int(i) for i in str_frac.split('/')]
            frac[0] *= sign
            return tuple(frac)
        # Если просто число, считаем его дробью со знаменателем 1
        else:
            return (int(str_frac), 1)


def gcd(a, b):
    """
    Рекурсивная функция нахождения наибольшего общего делителя
    Честно украденная из интернета
    """
    if b == 0:
        return abs(a)
    else:
        return gcd(b, a % b)


def tuple_to_str(a, b):
    """
    Функция, превращающая дробь в строку
    принимает 2 дроби в виде кортежей
    """
    # Опять же не забываем про знак
    if a < 0:
        sign = -1
        a = -a
    else:
        sign = 1
    gcd_num = gcd(a, b)  # Считаем НОД
    a, b = a // gcd_num, b // gcd_num
    if a % b == 0:
        return f'{a//b * sign}'
    elif a > b:
        return f'{a//b * sign}({a%b}/{b})'
    else:
        return f'{a * sign}/{b}'


def evaluate(string, saved):
    """
    Основная функция производящая счет дробей
    На вход поступает строка с выражением
    """
    string = string.split()
    # Восстановление сохраненного значения
    for i, el in enumerate(string):
        if e in saved:
            string[i] = saved[el]

    dict_funcs = {'+': summ,
                  '-': minus,
                  '/': divide,
                  '*': mult}
    # Проходим по всем знакам, поэтому с шагом 2
    for i in string[1::2]:
        # Если пользователь ввел например ^
        if i not in dict_funcs:
            return "Неверно введенное значение"
    # Проходим по всем элементам
    for i in range(len(string)):
        # Если на начетной позиции, то переводим в кортежную дробь, иначе оставляем знак
        string[i] = str_to_tuple(string[i]) if i % 2 == 0 else string[i]
    # Помещаем в lst сначала номера умножения и деления
    lst = [i for i, e in enumerate(string[1: -1], 1) if e in ('*', '/')]
    # Какая-то темная магия здесь творится
    lst = [e if i == 0 else e - 2 * i for i, e in enumerate(lst)]
    # Производим умножения и деления
    for i in lst:
        string[i - 1: i + 2] = [dict_funcs[string[i]]
                                (string[i - 1], string[i + 1])]
    # Делаем то же самое со сложением
    lst = [i for i, e in enumerate(string[1: -1: 2], 1)]
    lst = [e if i == 0 else e - 2 * i for i, e in enumerate(lst)]
    for i in lst:
        string[i - 1: i + 2] = [dict_funcs[string[i]]
                                (string[i - 1], string[i + 1])]
    # В итоге результат складывается в 1 элемент string
    # Возвращаем его строковое представление
    return tuple_to_str(*string[0])


if __name__ == "__main__":
    saved = {}  # Тут будем хранить сохраненные значения
    last_output = None
    while True:
        comm = input('Input: ')  # Читаем команду
        if comm.startswith('save'):  # save - сохраняем
            saved[comm.split()[-1]] = last_output
            print('save success')
        elif comm.startswith('del'):  # del - удаляем
            name = comm.split()[-1]
            if name in saved:
                del saved[name]
                print('del success')
            else:
                print('No such save')
        elif comm.startswith('restore'):  # restore - вывести сохраненное значение
            restored = saved.get(comm.split()[-1])
            if restored is None:
                print('No such save')
            else:
                last_output = restored
                print(last_output)
        elif comm == 'to double':  # to double - последний output переводим в double
            if last_output is None:
                print('No fraction')
            else:
                frac = str_to_tuple(last_output)
                print(frac[0] / frac[1])
        elif comm == 'exit':  # exit - выходим
            break
        else:
            last_output = evaluate(comm, saved)
            print(last_output)

# Не работают операции в скобках

# Input: 3/15 - 7/15 * 15/4
# -1(11/20)
# Input: save m1
# save success
# Input: 2/3 + 2 * 4
# 8(2/3)
# Input: save m2
# save success
# Input: to double
# 8.666666666666666
# Input: restore m3
# No such save
# Input: restore m1
# -1(11/20)
# Input: to double
# -1.55
# Input: del m2
# del success
# Input: restore m2
# No such save
# Input: exit
# -1(11/20)