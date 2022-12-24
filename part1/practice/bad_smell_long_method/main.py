# В задании представлена одна большая функция...
# Делает она всего ничего:
# - читает из строки (файла)         `_read`
# - сортирует прочитанные значения   `_sort`
# - фильтрует итоговый результат     `_filter`

# Конечно, вы можете попробовать разобраться как она
# это делает, но мы бы советовали разнести функционал
# по более узким функциям и написать их с нуля


csv = """Вася;39\nПетя;26\nВасилий Петрович;9"""


def get_user_list() -> list:
    user_list = get_list(csv)
    users_w_filter = get_age_filter(user_list)
    sorted_users = sort_users(users_w_filter)
    return sorted_users


def get_list(string: str) -> list:
    user_list = [user.split(";") for user in string.split('\n')]
    return user_list


def get_age_filter(user_list: list) -> list:
    valid_users = [user for user in user_list if int(user[1]) > 10]
    return valid_users


def sort_users(user_list: list) -> list:
    return sorted(user_list, key=lambda user: int(user[1]))