# traffic_model.py - Updated version
import random
from car_agent import CarAgent
from traffic_light import TrafficLight

class TrafficModel:
    def __init__(self, running_simulation, CENTER_X, CENTER_Y, HEIGHT, MIN_CAR_DISTANCE, INTERSECTION_SIZE, LANE_WIDTH, SIM_WIDTH, SIM_HEIGHT):
        self.cars = []
        self.running_simulation = running_simulation
        self.CENTER_X = CENTER_X
        self.CENTER_Y = CENTER_Y
        self.HEIGHT = HEIGHT
        self.MIN_CAR_DISTANCE = MIN_CAR_DISTANCE
        self.INTERSECTION_SIZE = INTERSECTION_SIZE
        self.LANE_WIDTH = LANE_WIDTH
        self.SIM_WIDTH = SIM_WIDTH
        self.SIM_HEIGHT = SIM_HEIGHT
        self.turn_counter_2_2 = 0
        self.turn_counter_3_1 = 0
        self.turn_counter_5_1 = 0
        self.turn_counter_8_2 = 0
        self.SPAWN_OFFSET = 200
        self.SPAWN_SPACING = 40
        self.initial_car_counts = {}
        self.car_counts = {}
        self.road_car_counts = {"2": 0, "3": 0, "5": 0, "8": 0}
        self.calculated_timings = False
        self.cycle_counter = 0
        self.using_initial_counts = True
        self.first_cycle_complete = False

        # Бағдаршамдарды анықтау (әр бағыт үшін біреу)
        self.traffic_lights = {
            "2.1_2.2": TrafficLight("2.1_2.2", CENTER_X, CENTER_Y),
            "3.1_3.2": TrafficLight("3.1_3.2", CENTER_X, CENTER_Y),
            "5.1_5.2": TrafficLight("5.1_5.2", CENTER_X, CENTER_Y),
            "8.1_8.2": TrafficLight("8.1_8.2", CENTER_X, CENTER_Y)
        }
        # Бастапқы белсенді бағдаршамды орнату
        self.active_traffic_light_id = "2.1_2.2"
        self.traffic_lights[self.active_traffic_light_id].state = "green"
        self.traffic_lights[self.active_traffic_light_id].timer = 0
        # Бағдаршамдардың ауысу ретін тізім түрінде сақтау
        self.traffic_light_cycle = list(self.traffic_lights.keys())
        self.cycle_index = 0 #Ағымдағы цикл индексі
        # Әр жолақта (бағытта) бастапқы көлік саны
        self.initial_car_counts = {
            "2.1": 0, "2.2": 0,
            "3.1": 0, "3.2": 0,
            "5.1": 0, "5.2": 0,
            "8.1": 0, "8.2": 0
        }
# Көліктерді көрініс аймағы бойынша санау функциясы
    def count_visible_cars_per_road(self):
        counts = {
            "2.1": 0, "2.2": 0,
            "3.1": 0, "3.2": 0,
            "5.1": 0, "5.2": 0,
            "8.1": 0, "8.2": 0
        }
        for car in self.cars:
            if self.is_visible(car): # Егер көлік көрінетін аймақта болса
                lane = car.lane  # Көліктің бағытын алу
                counts[lane] += 1 # Сол бағыт бойынша санын арттыру
        return counts
# Жолдар бойынша көлік сандарын визуалды көрсету үшін дайындау
    def get_road_car_counts_for_display(self):
        lane_counts = self.count_visible_cars_per_road()
        return {
            "2": lane_counts["2.2"] + lane_counts["3.1"],  # Light 1
            "3": lane_counts["3.2"] + lane_counts["2.1"],  # Light 2
            "5": lane_counts["8.1"] + lane_counts["5.1"],  # Light 3
            "8": lane_counts["5.2"] + lane_counts["8.2"]   # Light 4
        }

    def calculate_dynamic_timings(self, car_counts):
        #уақытты есептеу формула
        BASE_TIME = 15  # T in the formula
        MIN_GREEN = 5    # g_min
        MAX_GREEN = 30   # g_max


        light_lane_mapping = {
            "2.1_2.2": ["2.2", "3.1"],
            "3.1_3.2": ["3.2", "2.1"],
            "5.1_5.2": ["8.1", "5.1"],
            "8.1_8.2": ["5.2", "8.2"]
        }

        print("\nБағдаршам уақытын есептеу:")

        for light_id, lanes in light_lane_mapping.items():

            #формула бір, кезектегі көлік санын есептеу

            n_i = sum(car_counts[lane] for lane in lanes)

            N = sum(car_counts.values())

            if N > 0:
                #  G = max(g_min, min(n_i/N * 2T, g_min))
                raw_time = (n_i / N) * (2 * BASE_TIME)
                green_time = max(MIN_GREEN, min(raw_time, MAX_GREEN))
                green_time = round(green_time)
            else:
                green_time = MIN_GREEN


            light = self.traffic_lights[light_id]
            light.dynamic_timings = {
                "red": 0,
                "yellow": 150,
                "green": green_time * 30
            }
            light.current_green_time = green_time
            light.car_count = n_i

            print(f"{light_id}: {n_i} көлік -> {green_time}с жасыл")

    def calculate_initial_timings(self):

        light_lane_mapping = {
            "2.1_2.2": ["2.2", "3.1"],
            "3.1_3.2": ["3.2", "2.1"],
            "5.1_5.2": ["8.1", "5.1"],
            "8.1_8.2": ["5.2", "8.2"]
        }

        BASE_TIME = 15
        MIN_GREEN = 5
        MAX_GREEN = 30

        print("\nБастапқы көлік саны бойынша уақытты есептеу:")
        print("Бастапқы көлік саны:", self.initial_car_counts)

        for light_id, lanes in light_lane_mapping.items():
            total_cars = sum(self.initial_car_counts[lane] for lane in lanes)
            # Егер көлік саны аз болса, минималды жасыл уақыт беріледі
            if total_cars <= 3:
                green_time = MIN_GREEN
            else:
                all_cars = sum(self.initial_car_counts.values())
                if all_cars > 0:
                    proportion = total_cars / all_cars
                    green_time = int(proportion * BASE_TIME * 2)
                else:
                    green_time = MIN_GREEN

                green_time = max(MIN_GREEN, min(green_time, MAX_GREEN))

            light = self.traffic_lights[light_id]
            light.dynamic_timings = {
                "red": 0,
                "yellow": 150,
                "green": green_time * 30
            }
            light.current_green_time = green_time
            light.car_count = total_cars

            print(f"{light_id}: {total_cars} көлік ({' + '.join(lanes)}) -> {green_time}с жасыл")

    def start_simulation(self):
        print("\nМодельдеуді бастау")
        self.calculate_initial_timings()
        self.running_simulation = True
        self.first_cycle_complete = False

    def step(self):
        # Mesa was only used as a randomized scheduler. Keeping this tiny
        # scheduler local makes the simulation portable to browsers.
        cars_to_step = self.cars.copy()
        random.shuffle(cars_to_step)
        for car in cars_to_step:
            car.step()
         # Белсенді бағдаршамды жаңарту

        active_traffic_light = self.traffic_lights[self.active_traffic_light_id]
        active_traffic_light.update(self.active_traffic_light_id)
    # Егер ағымдағы жарық қызыл және уақыты аяқталса, келесі циклге көшу
        if active_traffic_light.state == "red" and active_traffic_light.timer == 0:
            self.cycle_index = (self.cycle_index + 1) % len(self.traffic_light_cycle)

            if self.cycle_index == 0:
                self.cycle_counter += 1
                if not self.first_cycle_complete:
                    self.first_cycle_complete = True

               # Бір цикл аяқталғаннан кейін көлік санын қайта есептеу
                if self.cycle_counter >= 1:
                    current_counts = self.count_visible_cars_per_road()
                    self.calculate_dynamic_timings(current_counts)
                # Келесі бағдаршамды іске қосу
            self.active_traffic_light_id = self.traffic_light_cycle[self.cycle_index]
            self.traffic_lights[self.active_traffic_light_id].state = "green"
            self.traffic_lights[self.active_traffic_light_id].timer = 0
    # Көрінетін аумақтан шыққан көліктерді жою
        self.cars = [
            car for car in self.cars
            if car.turning or (
                (car.direction == "down" and car.y < self.CENTER_Y + self.SIM_HEIGHT//2) or
                (car.direction == "up" and car.y > self.CENTER_Y - self.SIM_HEIGHT//2) or
                (car.direction == "right" and car.x < self.CENTER_X + self.SIM_WIDTH//2) or
                (car.direction == "left" and car.x > self.CENTER_X - self.SIM_WIDTH//2)
            )
        ]

    def add_car(self, x, y, direction, lane, car_type):
        # Көлікті карта шетінде жарамды позицияға орналастыру
        if direction == "down":
            y = self.CENTER_Y - self.SIM_HEIGHT // 2 - self.SPAWN_OFFSET
        elif direction == "up":
            y = self.CENTER_Y + self.SIM_HEIGHT // 2 + self.SPAWN_OFFSET
        elif direction == "right":
            x = self.CENTER_X - self.SIM_WIDTH // 2 - self.SPAWN_OFFSET
        elif direction == "left":
            x = self.CENTER_X + self.SIM_WIDTH // 2 + self.SPAWN_OFFSET

       # Бір жолақта бар көліктерді анықтау
        same_lane_cars = [c for c in self.cars if c.lane == lane and c.direction == direction]

       # Жолақ бойынша ретке келтіру үшін ығысу есептеу
        queue_position = len(same_lane_cars)
        offset = queue_position * self.SPAWN_SPACING

       # Ығыстыру арқылы нақты орынды анықтау
        if direction == "down":
            y -= offset
        elif direction == "up":
            y += offset
        elif direction == "right":
            x -= offset
        elif direction == "left":
            x += offset
# Жаңа көлікті қосу

        car = CarAgent(len(self.cars), self, x, y, direction, lane, car_type)
        self.cars.append(car)
# Бастапқы көлік санын жаңарту

        road = lane.split('.')[0] + '.' + lane.split('.')[1]
        self.initial_car_counts[road] = self.initial_car_counts.get(road, 0) + 1
        self.calculated_timings = False

    def is_visible(self, car):
        # Көлік көрінетін аймақта ма, соны тексеру
        return (self.CENTER_X - self.SIM_WIDTH//2 <= car.x <= self.CENTER_X + self.SIM_WIDTH//2 and
                self.CENTER_Y - self.SIM_HEIGHT//2 <= car.y <= self.CENTER_Y + self.SIM_HEIGHT//2)

    def count_cars(self):
        # Көрінетін көліктерді санау
        try:
            visible_cars = [car for car in self.cars if self.is_visible(car)]
            moving = 0
            waiting = 0

            for car in visible_cars:
                traffic_light = car._get_traffic_light()
                is_at_intersection = car._is_at_intersection()
                car_ahead = car._get_car_ahead()

                is_blocked = False
                # Егер алдындағы көлік тым жақын болса, тоқтау
                if car_ahead:
                    if car.direction == "down" and (car_ahead.y - car.y < car.min_distance):
                        is_blocked = True
                    elif car.direction == "up" and (car.y - car_ahead.y < car.min_distance):
                        is_blocked = True
                    elif car.direction == "right" and (car_ahead.x - car.x < car.min_distance):
                        is_blocked = True
                    elif car.direction == "left" and (car.x - car_ahead.x < car.min_distance):
                        is_blocked = True


                at_red_light = (is_at_intersection and
                            traffic_light and
                            traffic_light.state in ["red", "yellow"] and
                            not (car.car_type == "red"))

                is_moving = (car.speed > 0 and not is_blocked and not at_red_light)

                if is_moving:
                    moving += 1
                else:
                    waiting += 1

            return moving, waiting
        except Exception as e:
            print(f"Қателік орын алды: {e}")
        return 0, 0

    def max_possible_cars(self):
        # Жолдың ұзындығына байланысты максималды көлік саны
        lane_length = self.SIM_WIDTH
        min_car_length = self.MIN_CAR_DISTANCE
        lanes = 4
        return int((lane_length / min_car_length) * lanes)

    def current_density(self):
        visible_cars = [car for car in self.cars if self.is_visible(car)]
        max_cars = self.max_possible_cars()
        effective_max = max_cars * 1.2
        raw_density = (len(visible_cars) / effective_max * 100)
        return min(raw_density, 100)
