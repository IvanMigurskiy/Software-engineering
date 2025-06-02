#!/bin/bash

echo "Результаты бенчмарков (без авторизации)" > bench.txt
echo "===================" >> bench.txt

echo "Тестирование с кэшем" >> bench.txt
echo "===================" >> bench.txt

echo "Тестирование с кэшем (1 поток)" | tee -a bench.txt
wrk -t1 -c10 -d15s http://localhost:8000/users/1 >> bench.txt 2>&1
echo "-------------------" >> bench.txt

echo "Тестирование с кэшем (5 потоков)" | tee -a bench.txt
wrk -t5 -c10 -d15s http://localhost:8000/users/1 >> bench.txt 2>&1
echo "-------------------" >> bench.txt

echo "Тестирование с кэшем (10 потоков)" | tee -a bench.txt
wrk -t10 -c10 -d15s http://localhost:8000/users/1 >> bench.txt 2>&1
echo "===================" >> bench.txt

