db = db.getSiblingDB('budget_tracker');

db.incomes.createIndex({ "periodicity": 1 });
db.incomes.createIndex({ "assignee_id": 1 });

db.incomes.insertMany([
    {
        title: "Тестовый доход 1",
        description: "Описание тестового дохода 1",
        value: 10000,
        due_date: "2025-04-15",
        periodicity: "once",
        periodicity_value: 0,
        created_at: new Date(),
        updated_at: new Date(),
        assignee_id: 1
    },
    {
        title: "Тестовый доход 2",
        description: "Описание тестового дохода 2",
        value: 10000,
        due_date: "2025-04-15",
        periodicity: "once",
        periodicity_value: 0,        
        created_at: new Date(),
        updated_at: new Date(),
        assignee_id: 1
    }
]);



db.costs.createIndex({ "periodicity": 1 });
db.costs.createIndex({ "assignee_id": 1 });

db.costs.insertMany([
    {
        title: "Тестовый расход 1",
        description: "Описание тестового расхода 1",
        value: 10000,
        due_date: "2025-04-15",
        periodicity: "once",
        periodicity_value: 0,        
        created_at: new Date(),
        updated_at: new Date(),
        assignee_id: 1
    },
    {
        title: "Тестовый расход 2",
        description: "Описание тестового расхода 2",
        status: "enabled",
        value: 10000,
        due_date: "2025-04-15",
        periodicity: "once",
        periodicity_value: 0,        
        created_at: new Date(),
        updated_at: new Date(),
        assignee_id: 1
    }
]);
