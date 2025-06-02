import unittest
import requests
from datetime import datetime, timedelta
import logging
import random
import time

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Конфигурация
AUTH_URL = "http://localhost:8000/"
BUDGET_URL = "http://localhost:8001/"
MASTER_CREDENTIALS = {
    "username": "admin",
    "password": "secret"
}

YOUR_NUMBER_COUNTER = random.randrange(1000, 10000, 1)



class TestBudgetAPI(unittest.TestCase):

    def setUp(self):
        """Подготовка перед каждым тестом: получение токена"""
        global YOUR_NUMBER_COUNTER
        self.headers = {}
        response = requests.post(
            f"{AUTH_URL}/token",
            data=MASTER_CREDENTIALS
        )
        self.assertEqual(response.status_code, 200, "Не удалось получить токен")
        
        token_data = response.json()
        self.token = token_data["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

        logger.info("Токен успешно получен")



    def test_create_user(self, user_data=None):
        """Проверка создания пользователя"""
        global YOUR_NUMBER_COUNTER
        if not user_data:
            user_data = {
                "username": "username_"+str(YOUR_NUMBER_COUNTER),
                "first_name": "first_name_"+str(YOUR_NUMBER_COUNTER),
                "last_name": "last_name_"+str(YOUR_NUMBER_COUNTER),
                "email": "email_"+str(YOUR_NUMBER_COUNTER),
                "password": "password_"+str(YOUR_NUMBER_COUNTER)
            }
            YOUR_NUMBER_COUNTER += 1

        response = requests.post(
            f"{AUTH_URL}/users",
            json=user_data,
            headers=self.headers
        )
        self.assertEqual(response.status_code, 200, "Ошибка при создании пользователя")
        user_data = response.json()
        #self.assertEqual(user_data["username"], "admin", "Неверный username")
        #self.assertEqual(user_data["role"], "admin", "Неверная роль пользователя")
        
        logger.info("Тест создания пользователя прошел успешно")
        return user_data


    def test_get_users(self):
        """Проверка получения списка пользователей"""
        global YOUR_NUMBER_COUNTER
        # Сначала создадим пользователя
        id = self.test_create_user()['id']
        response = requests.get(
            f"{AUTH_URL}/users",
            headers=self.headers
        )
        self.assertEqual(response.status_code, 200, "Ошибка при получении списка пользователей")
        users = response.json()
        self.assertTrue(len(users) > 0, "Список пользователей пуст")
        
        # Проверяем, что созданный пользователь присутствует в списке
        created_user = next(user for user in users if user["id"] == id)
        self.assertEqual(created_user["id"], id, "Созданный пользователь не найден в списке")
        
        logger.info(f"Тест получения списка пользователей прошел успешно: найдено {len(users)} пользователей: {users}")

    def test_get_users_by_names(self):
        """Проверка получения списка пользователей по имени и фамилии"""
        global YOUR_NUMBER_COUNTER
        # Сначала создадим пользователя

        user_data = self.test_create_user()
        first_name = user_data['first_name']
        last_name = user_data['last_name']
        id = user_data['id']

        response = requests.get(
            f"{AUTH_URL}/users_by_names",
            json=user_data,
            headers=self.headers
        )
        self.assertEqual(response.status_code, 200, "Ошибка при получении списка пользователей по имени и фамилии")
        users = response.json()
        self.assertTrue(len(users) > 0, "Список пользователей пуст")
        
        # Проверяем, что созданный пользователь присутствует в списке
        created_user = next(user for user in users if user["id"] == id)

        self.assertEqual(created_user["first_name"], first_name, "Созданный пользователь не найден в списке")
        self.assertEqual(created_user["last_name"], last_name, "Созданный пользователь не найден в списке")

        logger.info(f"Тест получения списка пользователей имени и фамилии прошел успешно: найдено {len(users)} пользователей: {users}")



    def test_get_user_by_username(self):
        """Проверка получения списка пользователей по логину"""
        global YOUR_NUMBER_COUNTER
        # Сначала создадим пользователя

        user_data = self.test_create_user()
        username = user_data['username']
        id = user_data['id']

        response = requests.get(
            f"{AUTH_URL}/user_by_username",
            json=user_data,
            headers=self.headers
        )
        self.assertEqual(response.status_code, 200, "Ошибка при получении списка пользователей по логину")
        created_user = response.json()
        
        # Проверяем, что созданный пользователь присутствует в списке
        self.assertEqual(created_user["id"], id, "Созданный пользователь не найден в списке")
        self.assertEqual(created_user["username"], username, "Созданный пользователь не найден в списке")

        logger.info(f"Тест получения списка пользователей по логину прошел успешно: {created_user}")




    def test_create_income(self, income_data=None):
        """Проверка создания дохода"""
        global YOUR_NUMBER_COUNTER
        if not income_data:
            income_data = {
                "title": f"Тестовый доход {datetime.now().strftime('%Y%m%d_%H%M%S')}"+str(YOUR_NUMBER_COUNTER),
                "value": 1000+YOUR_NUMBER_COUNTER,
                "due_date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
                "periodicity": "once",
                "periodicity_value": 0,
            }
            YOUR_NUMBER_COUNTER += 1

        response = requests.post(
            f"{BUDGET_URL}/incomes",
            json=income_data,
            headers=self.headers
        )
        self.assertEqual(response.status_code, 200, "Ошибка при создании дохода")
        income_data = response.json()
        #self.assertEqual(income_data["username"], "admin", "Неверный username")
        #self.assertEqual(income_data["role"], "admin", "Неверная роль дохода")
        
        logger.info("Тест создания дохода прошел успешно")
        return income_data


    def test_get_incomes(self):
        """Проверка получения списка доходов"""
        global YOUR_NUMBER_COUNTER
        # Сначала создадим пользователя
        income_id = self.test_create_income()['income_id']
        response = requests.get(
            f"{BUDGET_URL}/incomes",
            headers=self.headers
        )
        self.assertEqual(response.status_code, 200, "Ошибка при получении списка доходов")
        incomes = response.json()
        self.assertTrue(len(incomes) > 0, "Список доходов пуст")
        
        # Проверяем, что созданный пользователь присутствует в списке
        created_income = next(income for income in incomes if income["income_id"] == income_id)
        self.assertEqual(created_income["income_id"], income_id, "Созданный доход не найден в списке")
        
        logger.info(f"Тест получения списка доходов прошел успешно: найдено {len(incomes)} доходов: {incomes}")








    def test_create_cost(self, cost_data=None):
        """Проверка создания расхода"""
        global YOUR_NUMBER_COUNTER
        if not cost_data:
            cost_data = {
                "title": f"Тестовый доход {datetime.now().strftime('%Y%m%d_%H%M%S')}"+str(YOUR_NUMBER_COUNTER),
                "value": 1000+YOUR_NUMBER_COUNTER,
                "due_date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
                "periodicity": "once",
                "periodicity_value": 0,
            }
            YOUR_NUMBER_COUNTER += 1

        response = requests.post(
            f"{BUDGET_URL}/costs",
            json=cost_data,
            headers=self.headers
        )
        self.assertEqual(response.status_code, 200, "Ошибка при создании расхода")
        cost_data = response.json()
        #self.assertEqual(cost_data["username"], "admin", "Неверный username")
        #self.assertEqual(cost_data["role"], "admin", "Неверная роль расхода")
        
        logger.info("Тест создания расхода прошел успешно")
        return cost_data


    def test_get_costs(self):
        """Проверка получения списка расходов"""
        global YOUR_NUMBER_COUNTER
        # Сначала создадим пользователя
        cost_id = self.test_create_cost()['cost_id']
        response = requests.get(
            f"{BUDGET_URL}/costs",
            headers=self.headers
        )
        self.assertEqual(response.status_code, 200, "Ошибка при получении списка расходов")
        costs = response.json()
        self.assertTrue(len(costs) > 0, "Список расходов пуст")
        
        # Проверяем, что созданный пользователь присутствует в списке
        created_cost = next(cost for cost in costs if cost["cost_id"] == cost_id)
        self.assertEqual(created_cost["cost_id"], cost_id, "Созданный расход не найден в списке")
        
        logger.info(f"Тест получения списка расходов прошел успешно: найдено {len(costs)} расходов: {costs}")




    def test_get_budget(self):
        """Проверка получения списка расходов"""
        global YOUR_NUMBER_COUNTER
        # Сначала создадим пользователя

        budget_data = {
                "value": 1000+YOUR_NUMBER_COUNTER,
                "due_date": (datetime.now() + timedelta(days=15)).strftime("%Y-%m-%d"),
            }
        YOUR_NUMBER_COUNTER += 1

        response = requests.get(
            f"{BUDGET_URL}/budget",
            json=budget_data,
            headers=self.headers
        )
        self.assertEqual(response.status_code, 200, "Ошибка при получении списка расходов")
        budget = response.json()
        
        logger.info(f"Тест получения списка расходов прошел успешно: {budget}")
























if __name__ == "__main__":
    unittest.main()