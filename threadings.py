import multiprocessing
import threading
from queue import Queue
from random import randint
from time import sleep, time


log_lock = threading.Lock()


def log_to_file(message):
    with log_lock:
        print(message)
        with open('operations.log', 'a') as log_file:
            log_file.write(message + '\n')


class Truck(threading.Thread):
    def __init__(self, truck_id, max_load, delivery_time, warehouse_queue, region_name):
        super().__init__()
        self.truck_id = truck_id
        self.max_load = max_load
        self.delivery_time = delivery_time
        self.warehouse_queue = warehouse_queue
        self.region_name = region_name

    def run(self):
        load = randint(1, self.max_load)
        log_to_file(f'[{self.region_name}] [Грузовик {self.truck_id}]Везет {load} товаров')
        sleep(self.delivery_time)
        self.warehouse_queue.put(load)
        log_to_file(f'[{self.region_name}] [Грузовик {self.truck_id}] Доставил {load} товаров на склад ')


class Warehouse:
    def __init__(self, region_name):
        self.stock = 0
        self.lock = threading.Lock()
        self.region_name = region_name

    def receive_goods(self, amount):
        with self.lock:
            self.stock += amount
            log_to_file(f'[{self.region_name}] На склад поступило {amount} Текущий запас: {self.stock}')

    def process_warehouse_queue(self, queue):
        while not queue.empty():
            goods = queue.get()
            self.receive_goods(goods)
            sleep(1)


def city_region(region_name):
    log_to_file(f'[{region_name}] Запуск обработки регионов....')
    warehouse_queue = Queue()
    warehouse = Warehouse(region_name)

    trucks = [
        Truck(truck_id=1, max_load=50, delivery_time=3, warehouse_queue=warehouse_queue, region_name=region_name),
        Truck(truck_id=2, max_load=30, delivery_time=5, warehouse_queue=warehouse_queue, region_name=region_name),
        Truck(truck_id=3, max_load=60, delivery_time=2, warehouse_queue=warehouse_queue, region_name=region_name),
    ]

    for truck in trucks:
        truck.start()

    for truck in trucks:
        truck.join()

    threads = []
    for _ in range(3):
        thread = threading.Thread(target=warehouse.process_warehouse_queue, args=(warehouse_queue,))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()

    log_to_file(f'[{region_name}] Обработка завершена. Текущий запас на складе: {warehouse.stock}')

    return warehouse.stock


def manage_city():
    regions = ["Центр", "Юг", "Север"]
    with multiprocessing.Pool(processes=len(regions)) as pool:
        region_results = pool.map(city_region, regions)
    total_stock = sum(region_results)
    message = f"\n--- Итоговый отчёт по городу ---\nОбщий запас товаров во всех регионах: {total_stock}  \nВсе операции завершены."
    log_to_file(message)



if __name__ == "__main__":
    start_time = time()

    with open('operations.log', 'w') as log_file:
        log_file.write("=== Лог операций ===\n")

    print("Запуск городской инфраструктуры...\n")
    log_to_file("Запуск городской инфраструктуры...")

    manage_city()

    end_time = time()

    log_to_file(f"Программа завершена за {end_time - start_time:.2f} секунд.")
    print(f"\nПрограмма завершена за {end_time - start_time:.2f} секунд.")

