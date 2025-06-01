workspace {
    name "Coin Keeper"
    description "Coin Keeper - приложение для управления бюджетом"

    !identifiers hierarchical

    model {

        user = person "Пользователь" {
            description "Пользователь приложения"
        }

        budget_admin = person "Администратор" {
            description "Администратор приложения"
        }
        
        budget_system = softwareSystem "Coin Keeper" {
            group "Хранение данных" {
                db_budget = container "База данных доходов и расходов" {
                    description "Хранение данных о доходах и расходах" 
                    technology "PostgreSQL"
                    tags "database"
                }
                
                db_user = container "База данных пользователей" {
                    description "Хранение данных о пользователях" 
                    technology "PostgreSQL"
                    tags "database"
                }
            }
            
            user_service = container "Система управления пользователями" {
                description "Обработка запросов, связанных с пользователями" 
                technology "Python"
                -> db_user "Получает и сохраняет информацию о пользователях"
            }

            budget_service = container "Система управления бюджетом" {
                description "Обработка запросов, связанных с бюджетом" 
                technology "Python"
                -> db_budget "Получает и сохраняет информацию о доходах и расходах"
            }
                    
        }

        budget_admin -> budget_system.user_service "Использует для получения списка всех пользователей"
        
        user -> budget_system.user_service "Использует для получения информации о пользователе"
        user -> budget_system.budget_service "Использует для получения и изменения информации о доходах, расходах и бюджете"

        budget_system.user_service -> budget_system.db_user "Читает и записывает данные о пользователях"
        budget_system.budget_service -> budget_system.db_budget "Читает и записывает данные о доходах и расходах"
    }

    views {

        themes default
        styles {
            element "database" {
                shape cylinder
            }
        }
        
        systemContext budget_system "Context" {
            include *
            autoLayout lr
        }
        
        container budget_system "Container" {
            include *
            autoLayout lr
        }

        dynamic budget_system "uc01" "Создание нового пользователя" {
            autoLayout
            user -> budget_system.user_service "Создать нового пользователя (POST)"
            budget_system.user_service -> budget_system.db_user "Сохранить данные о пользователе"
        }
    
        dynamic budget_system "uc02" "Поиск пользователя по логину" {
            autoLayout
            budget_admin -> budget_system.user_service "Найти пользователя (GET)"
            budget_system.user_service -> budget_system.db_user "Найти данные о пользователе"
        }
    
        dynamic budget_system "uc03" "Поиск пользователя по имени и фамилии" {
            autoLayout
            budget_admin -> budget_system.user_service "Найти пользователя (GET)"
            budget_system.user_service -> budget_system.db_user "Найти данные о пользователе"
        }
    
        dynamic budget_system "uc04" "Создание дохода" {
            autoLayout
            user -> budget_system.budget_service "Создать новый доход (POST)"
            budget_system.budget_service -> budget_system.db_budget "Сохранить данные о доходе"
        }

        dynamic budget_system "uc05" "Создание расхода" {
            autoLayout
            user -> budget_system.budget_service "Создать новый доход (POST)"
            budget_system.budget_service -> budget_system.db_budget "Сохранить данные о расходе"
        }
    
        dynamic budget_system "uc06" "Поиск всех доходов" {
            autoLayout
            user -> budget_system.budget_service "Получить список доходов (GET)"
            budget_system.budget_service -> budget_system.db_budget "Собрать данные обо всех доходах"
        }

        dynamic budget_system "uc07" "Поиск всех расходов" {
            autoLayout
            user -> budget_system.budget_service "Получить список расходов (GET)"
            budget_system.budget_service -> budget_system.db_budget "Собрать данные обо всех расходах"
        }

        dynamic budget_system "uc08" "Получение распланированного бюджета" {
            autoLayout
            user -> budget_system.budget_service "Получить бюджет (GET)"
            budget_system.budget_service -> budget_system.db_budget "Получить распланированный бюджет"
        }

    }
    
}
