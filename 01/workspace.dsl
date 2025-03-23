workspace {
    name "Artemizer's coinKeeper"
    !identifiers hierarchical

    model {
        client = Person "User"

        coinKeeper = softwareSystem "Coin Keeper" {

            service = container "Client Service"{
                technology "Python + Fast API"
            }

            server = container "Request Manager Server"{
                technology "Python"
            }

            db = container "Database"{
                technology "PostgreSQL"

                users = component "Users"
                cost = component "Cost"

                income = component "Income"
            }

        }

        
        client -> coinKeeper.service "Autorization" "Browser"
        client -> coinKeeper.service "Create planned income" "Browser"
        client -> coinKeeper.service "Look all planned income" "Browsert"
        client -> coinKeeper.service "Create planned cost" "Browser"
        client -> coinKeeper.service "Look all planned cost" "Browser"
        client -> coinKeeper.service "Calculate dynamic budget in period" "Browser"

        coinKeeper.service -> coinKeeper.server "Resend request to server" "Fast API"

        coinKeeper.server -> coinKeeper.db.users "Check existence of user's login" "SQL request"
        coinKeeper.server -> coinKeeper.db.users "Check existence of user' {name, surname}" "SQL request"
        coinKeeper.server -> coinKeeper.db.users "Add new user" "SQL request"
        coinKeeper.server -> coinKeeper.db.income "Add new income" "SQL request"
        coinKeeper.server -> coinKeeper.db.income "Get list of income" "SQL request"
        coinKeeper.server -> coinKeeper.db.income "Calculate dynamic of income in period" "SQL request"
        coinKeeper.server -> coinKeeper.db.cost "Add new cost" "SQL request"
        coinKeeper.server -> coinKeeper.db.cost "Get  list of cost" "SQL request"
        coinKeeper.server -> coinKeeper.db.cost "Calculate dynamic of cost in period" "SQL request"
        

    }

    views {
        themes default

        systemContext coinKeeper "context" {
            include *
            autoLayout lr
        }

        container coinKeeper "c2" {
            include *
            autoLayout lr
        }

        component coinKeeper.db "c3" {
            include *
            autoLayout
        }

        dynamic coinKeeper "SampleOfWorking" "Add income"{
           autoLayout lr
           client -> coinKeeper.service "Create income"
           coinKeeper.service -> coinKeeper.server "Send request on server"
           coinKeeper.server -> coinKeeper.db "Add id of income and id of income in database table income"
        }
    }
}
