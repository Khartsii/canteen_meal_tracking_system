users_name = ['Alice', 'Bob', 'Charlie', 'David', 'Eve']
users_orders = {'Alice': ['Pizza, cost $10.99']}  # список заказов пользователей (например, словарь с именами пользователей и их заказами)
state_orders = ...  # состояние заказа (принятый, в процессе, выполнен)
dish_name = ...
dish_price = ...
dish_access = ...

# добавление нового пользователя в список
def add_user(users_name):
    name = str(input("Enter the name of the user to add: "))
    if name not in users_name:
        users_name.append(name)
        return(f"{name} has been added to the user list.")
    else:
        return(f"{name} is already in the user list.")


# информация и доступность блюда
def dish_info(dish_name, dish_price, dish_access):
    if dish_access:
        return(f"The dish '{dish_name}' is available for order, cost: ${dish_price}.")
    else:
        return(f"The dish '{dish_name}' is not available for order.")


# информация о пользователе и его заказах
def info_user(name, users_name, users_orders, user_count):
    if name in users_name and users_orders is not None:
        return(f"User '{name}' has order {users_orders}.")
    else:
        return(f"User '{name}' has no orders or does not exist in the user list.")


print(add_user(users_name))
print(dish_info('Pizza', 10.99, True))
print(info_user('Alice', users_name, users_orders, 1))