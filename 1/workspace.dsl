workspace {
    name "Бюджетирование"
    description "Система управления бюджетом, доходами и расходами для их планирования"

    !identifiers hierarchical

    model {
        admin = person "Администратор" {
            description "Управление пользователями, доходами и расходами."
            tags "Person"
        }

        user = person "Пользователь" {
            description "Регистрация и управление профилем, создание планируемых доходов и расходов, отслеживание бюджета."
            tags "Person"
        }

        budgetSystem = softwareSystem "Бюджетирование" {
            description "Система управления бюджетом, доходами и расходами для их планирования"

            apiGateway = container "API Gateway" {
                technology "Go, Gin"
                description "API-шлюз для маршрутизации запросов"
                tags "Backend"
            }

            webApp = container "Web Application" {
                technology "React, HTML, CSS, JavaScript"
                description "Веб-приложение для взаимодействия пользователей с системой"
                -> apiGateway "Передача запросов" "HTTPS/JSON"
                tags "Frontend"
            }

            userDb = container "User Database" {
                technology "PostgreSQL"
                description "База данных для хранения информации о пользователях"
                tags "Database"
            }

            incomeDb = container "Income Database" {
                technology "PostgreSQL"
                description "База данных для хранения информации о доходах"
                tags "Database"
            }

            costDb = container "Cost Database" {
                technology "PostgreSQL"
                description "База данных для хранения информации о расходах"
                tags "Database"
            }

            budgetDb = container "Budget Database" {
                technology "PostgreSQL"
                description "База данных для хранения информации о бюджете"
                tags "Database"
            }

            messageBroker = container "Message Broker" {
                technology "RabbitMQ"
                description "Брокер сообщений для асинхронного взаимодействия между сервисами"
                tags "Messaging"
            }

            userService = container "User Service" {
                technology "Go, gRPC"
                description "Сервис управления пользователями (регистрация, поиск)"
                -> apiGateway "Запросы на управление пользователями" "HTTPS/JSON"
                -> userDb "Хранение информации о пользователях" "SQL"
                -> messageBroker "Публикация событий о пользователях" "AMQP"
                tags "Backend"
            }

            incomeService = container "Income Service" {
                technology "Go, gRPC"
                description "Сервис управления доходами (создание, получение списка)"
                -> apiGateway "Запросы на управление доходами" "HTTPS/JSON"
                -> incomeDb "Хранение информации о доходах" "SQL"
                -> messageBroker "Публикация событий о доходах" "AMQP"
                tags "Backend"
            }

            costService = container "Cost Service" {
                technology "Go, gRPC"
                description "Сервис управления расходами (создание, получение списка)"
                -> apiGateway "Запросы на управление расходами" "HTTPS/JSON"
                -> costDb "Хранение информации о расходах" "SQL"
                -> messageBroker "Публикация событий о расходах" "AMQP"
                tags "Backend"
            }

            budgetService = container "Budget Service" {
                technology "Go, gRPC"
                description "Сервис получения информации о бюджете"
                -> apiGateway "Запросы на получение информации о бюджете" "HTTPS/JSON"
                -> costDb "Хранение информации о бюджете" "SQL"
                -> messageBroker "Публикация событий о бюджете" "AMQP"
                tags "Backend"
            }
        }

        authSystem = softwareSystem "Система аутентификации и авторизации" {
            description "Управление пользователями и их ролями. Обеспечение безопасности API."
            tags "ExternalSystem"
        }

        admin -> budgetSystem.webApp "Управление пользователями, доходами и расходами"
        user -> budgetSystem.webApp "Регистрация, создание доходов и расходов, отслеживание бюджета"

        budgetSystem.userService -> authSystem "Аутентификация и авторизация" "HTTPS/JSON"
    }

    views {
        systemContext budgetSystem "SystemContext" {
            include *
            autolayout lr
        }

        container budgetSystem "Container" {
            include *
            autolayout lr
        }

        dynamic budgetSystem "createUser" "Создание нового пользователя" {
            admin -> budgetSystem.webApp "Создание нового пользователя"
            budgetSystem.webApp -> budgetSystem.apiGateway "POST /user"
            budgetSystem.apiGateway -> budgetSystem.userService "Создает запись в базе данных"
            budgetSystem.userService -> budgetSystem.userDb "INSERT INTO users"
            budgetSystem.userService -> budgetSystem.messageBroker "Публикует событие 'UserCreated'"
            autolayout lr
        }

        dynamic budgetSystem "searchUserByLogin" "Поиск пользователя по логину" {
            admin -> budgetSystem.webApp "Поиск пользователя по логину"
            budgetSystem.webApp -> budgetSystem.apiGateway "GET /user?login={login}"
            budgetSystem.apiGateway -> budgetSystem.userService "Ищет пользователя в базе данных"
            budgetSystem.userService -> budgetSystem.userDb "SELECT * FROM users WHERE login={login}"
            autolayout lr
        }

        dynamic budgetSystem "createIncome" "Создание нового дохода" {
            user -> budgetSystem.webApp "Создание нового дохода"
            budgetSystem.webApp -> budgetSystem.apiGateway "POST /income"
            budgetSystem.apiGateway -> budgetSystem.incomeService "Создает запись о доходе"
            budgetSystem.incomeService -> budgetSystem.incomeDb "INSERT INTO incomes"
            budgetSystem.incomeService -> budgetSystem.messageBroker "Публикует событие 'IncomeCreated'"
            autolayout lr
        }

        dynamic budgetSystem "createCost" "Создание нового расхода" {
            user -> budgetSystem.webApp "Создание нового расхода"
            budgetSystem.webApp -> budgetSystem.apiGateway "POST /cost"
            budgetSystem.apiGateway -> budgetSystem.costService "Создает запись о расходе"
            budgetSystem.costService -> budgetSystem.costDb "INSERT INTO costs"
            budgetSystem.costService -> budgetSystem.messageBroker "Публикует событие 'CostCreated'"
            autolayout lr
        }

        styles {
            element "Person" {
                shape Person
                background #08427b
                color #ffffff
            }
            element "Backend" {
                shape RoundedBox
                background #1168bd
                color #ffffff
            }
            element "Frontend" {
                shape WebBrowser
                background #438dd5
                color #ffffff
            }
            element "Database" {
                shape Cylinder
                background #85bbf0
                color #000000
            }
            element "Messaging" {
                shape Pipe
                background #ff8c00
                color #ffffff
            }
            element "ExternalSystem" {
                shape Box
                background #999999
                color #ffffff
            }
        }

        theme default
    }
}