workspace {
    model {
        user = person "User"
        
        auth = softwareSystem "Authentication Service" "auth" {
            AuthApi = container "Auth API" "authApi" {
                description "Handles authentication"
                technology "FastAPI"
            }
            AuthDb = container "Auth Database" "authDb" {
                description "Stores user data"
                technology "PostgreSQL"
            }
            AuthApi -> AuthDb "Reads/writes"
        }
        
        budget = softwareSystem "Budget Service" "budget" {
            IncomeApi = container "Income API" "incomeApi" {
                description "Manages incomes"
                technology "FastAPI"
            }
            IncomeDb = container "Income Database" "incomeDb" {
                description "Stores incomes"
                technology "PostgreSQL"
            }
            IncomeApi -> IncomeDb "Reads/writes"

            CostApi = container "Cost API" "costApi" {
                description "Manages costs"
                technology "FastAPI"
            }
            CostDb = container "Cost Database" "costDb" {
                description "Stores costs"
                technology "PostgreSQL"
            }
            CostApi -> CostDb "Reads/writes"

            
            BudgetApi = container "Budget API" "budgetApi" {
                description "Manages budget"
                technology "FastAPI"
            }
        }
        
        // Relationships
        user -> auth "Logs in"
        auth -> user "Returns JWT"
        
        user -> budget "Creates income"
        user -> budget "Creates cost"

        budget -> auth "Validates token"
        
        budget -> user "Returns incomes"
        budget -> user "Returns costs"
        budget -> user "Returns budget"

    }
}