workspace {
    name "Бюджетирование"

    !identifiers hierarchical

    model {
        properties { 
            structurizr.groupSeparator "/"
        }

        user = person "Пользователь" {
            description "Управляет своим бюджетом"
            tags "user"
        }

        budgeting_system = softwareSystem "Система Бюджетирования" {
            description "Позволяет считать динамику бюджета за период и управлять доходами и расходами"
            tags "system"

            user_service = container "User Service" {
                description "Управляет пользователями"
                technology "Python"
                tags "service"
            } 

            budget_service = container "Budget Service" {
                description "Позволяет считать динамику бюджета за период и управлять доходами и расходами"
                technology "Python"
                tags "service"
            } 

            database = container "Database" {
                description "Хранит данные пользователей, доходов и расходов"
                technology "PostgreSQL"
                tags "database"
            }

            mongo = container "Mongo" {
                description "Хранит данные доходов и расходов"
                technology "MongoDB"
                tags "database"
            }


            redis = container "Redis" {
                description "Хранит сессии пользователей"
                technology "Redis"
                tags "cache"
            }

            user -> user_service "Регистрация и вход"
            user_service -> database "Сохранение и получение данных"
            user_service -> redis "Сохранение сессии (JWT)"

            user -> budget_service "Добавить доход"
            user -> budget_service "Добавить расход"

            budget_service -> redis "Получение сессии"
            budget_service -> mongo "Сохранение и получение доходов и расходов"
            
            budget_service -> user "Получить все доходы"
            budget_service -> user "Получить все расходы"
            budget_service -> user "Посчитать динамику бюджета за период"
        }

        user -> budgeting_system "Использует систему для управления бюджетом"
    }

    views {
        themes default

        properties {
            structurizr.tooltips true
        }

        systemContext budgeting_system {
            autoLayout lr 1000 1000
            include *
        }

        container budgeting_system {
            autoLayout tb 500 250
            include *
        }

        dynamic budgeting_system "Case1" "Создание нового пользователя" {
            autoLayout
            user -> budgeting_system.user_service "Создание пользователя (POST /user)"
            budgeting_system.user_service -> budgeting_system.database "Сохранение данных о пользователе"
            budgeting_system.user_service -> user "Возвращает подтверждение регистрации"
        }

        dynamic budgeting_system "Case2" "Авторизация пользователя" {
            autoLayout
            user -> budgeting_system.user_service "Авторизация (POST /auth)"
            budgeting_system.user_service -> budgeting_system.database "Проверка учетных данных"
            budgeting_system.user_service -> budgeting_system.redis "Сохранение сессии"
            budgeting_system.user_service -> user "Возвращает токен авторизации"
        }

        dynamic budgeting_system "Case3" "Создание дохода" {
            autoLayout tb 1000 100
            user -> budgeting_system.user_service "Авторизация (POST /auth)"
            budgeting_system.user_service -> user "Возвращает токен авторизации"
            user -> budgeting_system.budget_service "Создание дохода (POST /income)"
            budgeting_system.budget_service -> budgeting_system.redis "Проверка наличия сессии"
            budgeting_system.budget_service -> budgeting_system.mongo "Сохранение дохода"
            budgeting_system.budget_service -> user "Возвращает подтверждение операции"
        }

        dynamic budgeting_system "Case4" "Создание расхода" {
            autoLayout tb 1000 100
            user -> budgeting_system.user_service "Авторизация (POST /auth)"
            budgeting_system.user_service -> user "Возвращает токен авторизации"
            user -> budgeting_system.budget_service "Создание расхода (POST /cost)"
            budgeting_system.budget_service -> budgeting_system.redis "Проверка наличия сессии"
            budgeting_system.budget_service -> budgeting_system.mongo "Сохранение расхода"
            budgeting_system.budget_service -> user "Возвращает подтверждение операции"
        }

        dynamic budgeting_system "Case5" "Получение перечня доходов" {
            autoLayout tb 1000 100
            user -> budgeting_system.user_service "Авторизация (POST /auth)"
            budgeting_system.user_service -> user "Возвращает токен авторизации"
            user -> budgeting_system.budget_service "Запрос списка доходов (GET /income)"
            budgeting_system.budget_service -> budgeting_system.redis "Проверка наличия сессии"
            budgeting_system.budget_service -> budgeting_system.mongo "Извлечение данных о доходах"
            budgeting_system.budget_service -> user "Передача списка доходов"
        }

        dynamic budgeting_system "Case6" "Получение перечня расходов" {
            autoLayout tb 1000 100
            user -> budgeting_system.user_service "Авторизация (POST /auth)"
            budgeting_system.user_service -> user "Возвращает токен авторизации"
            user -> budgeting_system.budget_service "Запрос списка расходов (GET /cost)"
            budgeting_system.budget_service -> budgeting_system.redis "Проверка наличия сессии"
            budgeting_system.budget_service -> budgeting_system.mongo "Извлечение данных о расходах"
            budgeting_system.budget_service -> user "Передача списка расходов"
        }

        dynamic budgeting_system "Case7" "Получение посчитанной динамики бюджета за период" {
            autoLayout tb 1000 100
            user -> budgeting_system.user_service "Авторизация (POST /auth)"
            budgeting_system.user_service -> user "Возвращает токен авторизации"
            user -> budgeting_system.budget_service "Запрос динамики бюджета за период (GET /budget)"
            budgeting_system.budget_service -> budgeting_system.redis "Проверка наличия сессии"
            budgeting_system.budget_service -> budgeting_system.mongo "Извлечение данных о доходах"
            budgeting_system.budget_service -> budgeting_system.mongo "Извлечение данных о расходах"
            budgeting_system.budget_service -> user "Передача динамики бюджета за период"
        }

        styles {
            element "database" {
                shape cylinder
                background #f4b183
                color #000000
            }
            
            element "service" {
                shape roundedBox
                background #8eaadb
                color #000000
            }
            
            element "system" {
                shape box
                background #d5a6bd
                color #000000
            }
            
            element "user" {
                shape person
                background #ffe599
                color #000000
            }
        }
    }
}
