workspace {

    model {
        user = person "Пользователь"
        

        frontend = softwareSystem "Frontend" {
            
        }

        backend = softwareSystem "Backend" {
            income = container "Планируемый доход"
            cost = container "Планируемый расход"

            user_in_app = container "Пользоваетель приложения"

        }

        user -> frontend "Создание нового пользователя"
        user -> frontend "Поиск пользователя по логину"
        user -> frontend "Поиск пользователя по маске имя и фамилии"
        user -> frontend "Создать планируемый доход"
        user -> frontend "Получить перечень планируемых доходов"
        user -> frontend "Создать планируемый расход"
        user -> frontend "Получить перечень планируемых расходов"
        user -> frontend "Посчитать динамику бюджета за период"

        frontend -> backend "Создание нового пользователя"
        frontend -> backend "Поиск пользователя по логину"
        frontend -> backend "Поиск пользователя по маске имя и фамилии"
        frontend -> backend "Создать планируемый доход"
        frontend -> backend "Получить перечень планируемых доходов"
        frontend -> backend "Создать планируемый расход"
        frontend -> backend "Получить перечень планируемых расходов"
        frontend -> backend "Посчитать динамику бюджета за период"
    }

    views {
        systemContext frontend "Diagram1" {
            include *
            autoLayout
        }

        systemContext backend "Diagram2" {
            include *
            autoLayout
        }


        theme default
    }

}

