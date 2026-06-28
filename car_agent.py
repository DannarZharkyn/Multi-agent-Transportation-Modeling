import math
from behaviour import CarBehavior

class CarAgent:
    def __init__(self, unique_id, model, start_x, start_y, direction, lane, car_type):
        self.unique_id = unique_id
        self.model = model
        self.x = start_x
        self.y = start_y
        self.direction = direction
        self.lane = lane
        self.car_type = car_type.lower()
        self.speed = 2
        self.min_distance = 40
        self.turning = False
        self.has_crossed = False
        self.target_x = None
        self.target_y = None
        self.special_turn_progress = 0
        self.turn_start_x = 0
        self.turn_start_y = 0
        self.impatient_timer = 0

    def step(self):
        if not self.model.running_simulation:
            return

        if self.turning:
            self._handle_turning_movement()
            return

        direction_handlers = {
            "down": self.handle_down_movement,
            "up": self.handle_up_movement,
            "left": self.handle_left_movement,
            "right": self.handle_right_movement,
        }

        handler = direction_handlers.get(self.direction)
        if handler:
            handler()

    def _handle_turning_movement(self):
        if self.direction == "special_turn_to_4_1":
            self._handle_special_turn()
            return
        elif self.direction == "special_turn_to_4_2":
            self._handle_special_turn_to_4_2()
            return
        elif self.direction == "special_turn_to_1_2":
            self._handle_special_turn_to_1_2()
            return
        elif self.direction == "smooth_left_turn":
            self._handle_smooth_left_turn()
            return
        elif self.direction == "smooth_right_turn":
            self._handle_smooth_right_turn()
            return
        elif self.direction == "smooth_down_turn":
            self._handle_smooth_down_turn()
            return
        elif self.direction == "smooth_up_turn":
            self._handle_smooth_up_turn()
            return

        # Нысана координатасына дейінгі айырмашылықтарды есептеу
        dx = self.target_x - self.x
        dy = self.target_y - self.y

        # Егер көлік арнайы жолақтарда болса, тура бағытпен қозғалады
        if self.lane in ["2.2", "3.1", "5.1", "8.2"]:
            distance = math.sqrt(dx**2 + dy**2)
            if distance > 0:
                self.x += (dx / distance) * self.speed
                self.y += (dy / distance) * self.speed
            # Мақсатқа жеткенде бұрылысты аяқтау
            if distance < self.speed:
                self.x = self.target_x
                self.y = self.target_y
                self.turning = False
            return


        if not hasattr(self, 'turn_phase'):
            if self.direction in ['left', 'right']:
                self.turn_phase = 'align_horizontal'
            else:
                self.turn_phase = 'align_vertical'

        if self.turn_phase == 'align_horizontal':

            target_y = self.model.CENTER_Y
            dy_align = target_y - self.y
            if abs(dy_align) > 1:
                self.y += (dy_align / abs(dy_align)) * self.speed
            else:
                self.y = target_y
                self.turn_phase = 'turn_vertical'

        elif self.turn_phase == 'align_vertical':

            target_x = self.model.CENTER_X
            dx_align = target_x - self.x
            if abs(dx_align) > 1:
                self.x += (dx_align / abs(dx_align)) * self.speed
            else:
                self.x = target_x
                self.turn_phase = 'turn_horizontal'

        elif self.turn_phase == 'turn_vertical':

            step_y = self.speed if dy > 0 else -self.speed
            self.y += step_y
            if abs(dy) <= self.speed:
                self.y = self.target_y
                self.turn_phase = 'final_approach'

        elif self.turn_phase == 'turn_horizontal':

            step_x = self.speed if dx > 0 else -self.speed
            self.x += step_x
            if abs(dx) <= self.speed:
                self.x = self.target_x
                self.turn_phase = 'final_approach'

        else:
            distance = math.sqrt(dx**2 + dy**2)

            if distance > 0:
                self.x += (dx / distance) * self.speed
                self.y += (dy / distance) * self.speed


        if (abs(self.x - self.target_x) < self.speed and
            abs(self.y - self.target_y) < self.speed):
            self.x = self.target_x
            self.y = self.target_y
            self.turning = False
            if hasattr(self, 'turn_phase'):
                del self.turn_phase


    def _is_at_intersection(self):
        return (self.model.CENTER_X - 80 <= self.x <= self.model.CENTER_X + 80 and
                self.model.CENTER_Y - 80 <= self.y <= self.model.CENTER_Y + 80)

    def _is_in_intersection(self):

        return (self.model.CENTER_X - self.model.INTERSECTION_SIZE//2 <= self.x <= self.model.CENTER_X + self.model.INTERSECTION_SIZE//2 and
                self.model.CENTER_Y - self.model.INTERSECTION_SIZE//2 <= self.y <= self.model.CENTER_Y + self.model.INTERSECTION_SIZE//2)

    def _distance_to_stop_line(self):
        # Тоқтау сызығына дейінгі қашықтықты есептейді
        if self.direction == "down":
            return (self.model.CENTER_Y - self.model.INTERSECTION_SIZE//2 - 40) - self.y
        elif self.direction == "up":
            return self.y - (self.model.CENTER_Y + self.model.INTERSECTION_SIZE//2 + 40)
        elif self.direction == "right":
            return (self.model.CENTER_X + self.model.INTERSECTION_SIZE//2 + 40) - self.x
        elif self.direction == "left":
            return self.x - (self.model.CENTER_X - self.model.INTERSECTION_SIZE//2 - 40)
        return float('inf')

    def _at_stop_line(self):

        return abs(self._distance_to_stop_line()) <= 5


    def _maintain_car_spacing(self): # Көліктер арасындағы қашықтықты сақтайды (алдыңғы көлікпен арақашықтықты тексереді)

        car_ahead = self._get_car_ahead() # Алдыңғы көлікті анықтайды
        if car_ahead: # Егер бағыт төмен болса және алдыңғы көлік тым жақын болса — тоқтау
            if self.direction == "down" and (car_ahead.y - self.y) < self.min_distance:
                self.speed = 0
            elif self.direction == "up" and (self.y - car_ahead.y) < self.min_distance:
                self.speed = 0
            elif self.direction == "right" and (car_ahead.x - self.x) < self.min_distance:
                self.speed = 0
            elif self.direction == "left" and (self.x - car_ahead.x) < self.min_distance:
                self.speed = 0
# Алдыңғы көлікті табу функциясы
    def _get_car_ahead(self):
        closest_car = None
        min_distance = float('inf')

        for car in self.model.cars:
            if (car != self and
                car.lane == self.lane and
                car.direction == self.direction and
                not car.turning):

                if self.direction == "down" and car.y > self.y:
                    distance = car.y - self.y
                elif self.direction == "up" and car.y < self.y:
                    distance = self.y - car.y
                elif self.direction == "right" and car.x > self.x:
                    distance = car.x - self.x
                elif self.direction == "left" and car.x < self.x:
                    distance = self.x - car.x
                else:
                    continue

                if 0 < distance < min_distance:
                    min_distance = distance
                    closest_car = car

        return closest_car
    # Жолаққа сәйкес бағдаршамды қайтарады
    def _get_traffic_light(self):
        lane_group = self.lane.split('.')[0]
        lane_num = self.lane.split('.')[1]

        # Бағдаршамды жолақ тобына және нөміріне қарай таңдайды
        if (lane_group == "2" and lane_num == "2") or (lane_group == "3" and lane_num == "1"):
            return self.model.traffic_lights.get("2.1_2.2")
        elif (lane_group == "2" and lane_num == "1") or (lane_group == "3" and lane_num == "2"):
            return self.model.traffic_lights.get("3.1_3.2")

        elif (lane_group == "5" and lane_num == "1") or (lane_group == "8" and lane_num == "1"):
            return self.model.traffic_lights.get("5.1_5.2")
        elif (lane_group == "5" and lane_num == "2") or (lane_group == "8" and lane_num == "2"):
            return self.model.traffic_lights.get("8.1_8.2")
        return None

    def handle_down_movement(self):
        traffic_light = self._get_traffic_light()

        if self.y > self.model.CENTER_Y + self.model.INTERSECTION_SIZE // 2:
            self.has_crossed = True

        if self.has_crossed:
            CarBehavior.standard_behavior(self, traffic_light)
        else:
            if self.car_type == "red":
                CarBehavior.aggressive_behavior(self, traffic_light)
            elif self.car_type == "blue":
                CarBehavior.cautious_behavior(self, traffic_light)
            else:
                CarBehavior.standard_behavior(self, traffic_light)

        if self.speed > 0 and self.y < self.model.CENTER_Y + self.model.SIM_HEIGHT // 2:
            self.y += self.speed

        if not self.turning and self.model.CENTER_Y - 70 <= self.y <= self.model.CENTER_Y + 70:
            if self.lane == "2.1":
                self._start_turn_into_6_1()
            elif self.lane == "2.2":
                self._start_turn_into_7_1_or_4_2()

    def handle_up_movement(self):
        traffic_light = self._get_traffic_light()

        if self.y < self.model.CENTER_Y - self.model.INTERSECTION_SIZE // 2:
            self.has_crossed = True

        if self.has_crossed:
            CarBehavior.standard_behavior(self, traffic_light)
        else:
            if self.car_type == "red":
                CarBehavior.aggressive_behavior(self, traffic_light)
            elif self.car_type == "blue":
                CarBehavior.cautious_behavior(self, traffic_light)
            else:
                CarBehavior.standard_behavior(self, traffic_light)

        if self.speed > 0 and self.y > self.model.CENTER_Y - self.model.SIM_HEIGHT // 2:
            self.y -= self.speed

        if not self.turning and self.model.CENTER_Y - 70 <= self.y <= self.model.CENTER_Y + 70:
            if self.lane == "3.1":
                self._start_turn_into_6_2_or_1_1()
            elif self.lane == "3.2":
                self._start_turn_into_7_2()

    def handle_right_movement(self):
        traffic_light = self._get_traffic_light()

        if self.x > self.model.CENTER_X + self.model.INTERSECTION_SIZE // 2:
            self.has_crossed = True

        if self.has_crossed:
            CarBehavior.standard_behavior(self, traffic_light)
        else:
            if self.car_type == "red":
                CarBehavior.aggressive_behavior(self, traffic_light)
            elif self.car_type == "blue":
                CarBehavior.cautious_behavior(self, traffic_light)
            else:
                CarBehavior.standard_behavior(self, traffic_light)

        if self.speed > 0 and self.x < self.model.CENTER_X + self.model.SIM_WIDTH // 2:
            self.x += self.speed

        if not self.turning and self.model.CENTER_X - 70 <= self.x <= self.model.CENTER_X + 70:
            if self.lane == "5.1":
                self._start_turn_into_1_1_or_7_1()
            elif self.lane == "5.2":
                self._start_turn_into_4_1()

    def handle_left_movement(self):
        traffic_light = self._get_traffic_light()

        if self.x < self.model.CENTER_X - self.model.INTERSECTION_SIZE // 2:
            self.has_crossed = True

        if self.has_crossed:
            CarBehavior.standard_behavior(self, traffic_light)
        else:
            if self.car_type == "red":
                CarBehavior.aggressive_behavior(self, traffic_light)
            elif self.car_type == "blue":
                CarBehavior.cautious_behavior(self, traffic_light)
            else:
                CarBehavior.standard_behavior(self, traffic_light)

        if self.speed > 0 and self.x > self.model.CENTER_X - self.model.SIM_WIDTH // 2:
            self.x -= self.speed

        if not self.turning and self.model.CENTER_X - 70 <= self.x <= self.model.CENTER_X + 70:
            if self.lane == "8.2":
                self._start_turn_into_1_2()
            elif self.lane == "8.1":
                self._start_turn_into_4_2_or_6_2()


    def _start_turn_into_6_1(self):

        self.turning = True
        self.direction = "smooth_left_turn"
        self.turn_start_x = self.x
        self.turn_start_y = self.y

        self.target_x = self.model.CENTER_X - self.model.SIM_WIDTH // 2
        self.target_y = self.model.CENTER_Y + self.model.LANE_WIDTH // 2 - self.model.LANE_WIDTH // 4

        self.turn_progress = 0
        self.speed = 2

    def _handle_smooth_left_turn(self):
        # Бұрылысты бастайтын бастапқы нүкте

        p0 = (self.turn_start_x, self.turn_start_y)
        # Бақылау нүктелері - бұрылыстың тегістігін қамтамасыз етеді
        p1 = (self.model.CENTER_X - 20, self.model.CENTER_Y + 20)
        p2 = (self.model.CENTER_X - 40, self.model.CENTER_Y)
        # Бұрылыстың аяқталатын нүктесі (тағайындалған координата)
        p3 = (self.target_x, self.target_y)

       # Бұрылыс бойындағы прогресс (0.0 - 1.0 аралығында)
        t = self.turn_progress

        # Бэзье қисығы бойынша ағымдағы x және y координаталарын есептеу
        x = (1 - t)**3 * p0[0] + 3 * (1 - t)**2 * t * p1[0] + 3 * (1 - t) * t**2 * p2[0] + t**3 * p3[0]
        y = (1 - t)**3 * p0[1] + 3 * (1 - t)**2 * t * p1[1] + 3 * (1 - t) * t**2 * p2[1] + t**3 * p3[1]

        # Қисық бойындағы бағытты есептеу (туындысы арқылы)
        dx = -3*(1 - t)**2 * p0[0] + 3*(1 - t)**2 * p1[0] - 6*(1 - t)*t * p1[0] + 6*(1 - t)*t * p2[0] - 3*t**2 * p2[0] + 3*t**2 * p3[0]
        dy = -3*(1 - t)**2 * p0[1] + 3*(1 - t)**2 * p1[1] - 6*(1 - t)*t * p1[1] + 6*(1 - t)*t * p2[1] - 3*t**2 * p2[1] + 3*t**2 * p3[1]
    # Жылдамдықты қисық бойында сақтау үшін қисық ұзындығын есептеу
        length = (dx**2 + dy**2) ** 0.5
        if length == 0:
            length = 1
            # Бұрылыс прогресін жаңарту (жылдамдықты қисыққа бейімдеу)
        dt = self.speed / length


        self.turn_progress += dt
        self.turn_progress = min(self.turn_progress, 1.0)

        # Көліктің координаталарын жаңарту
        self.x = x
        self.y = y


        if self.turn_progress >= 1.0:
            self.turning = False
            self.direction = "left"
            self.turn_progress = 0


    def _start_turn_into_7_1_or_4_2(self):
        if self.model.turn_counter_2_2 % 2 == 0:
            self.target_x = self.model.CENTER_X + self.model.SIM_WIDTH // 2
            self.target_y = self.model.CENTER_Y - self.model.LANE_WIDTH // 2 - self.model.LANE_WIDTH // 4
            self.direction = "right"
        else:
            self.target_x = self.model.CENTER_X + self.model.LANE_WIDTH // 2 + self.model.LANE_WIDTH // 4
            self.target_y = self.model.CENTER_Y + self.model.SIM_HEIGHT // 2
            self.direction = "down"
        self.turning = True
        self.speed = 2
        self.model.turn_counter_2_2 += 1


    def _start_turn_into_6_2_or_1_1(self):
        if self.model.turn_counter_3_1 % 2 == 0:
            self.target_x = self.model.CENTER_X - self.model.SIM_WIDTH // 2
            self.target_y = self.model.CENTER_Y + self.model.LANE_WIDTH // 2 + self.model.LANE_WIDTH // 4
            self.direction = "left"
        else:
            self.target_x = self.model.CENTER_X - self.model.LANE_WIDTH // 2 - self.model.LANE_WIDTH // 4
            self.target_y = self.model.CENTER_Y - self.model.SIM_HEIGHT // 2
            self.direction = "up"
        self.turning = True
        self.speed = 2
        self.model.turn_counter_3_1 += 1

    def _handle_smooth_right_turn(self):

        p0 = (self.turn_start_x, self.turn_start_y)
        p1 = (self.model.CENTER_X + 20, self.model.CENTER_Y - 20)
        p2 = (self.model.CENTER_X + 40, self.model.CENTER_Y)
        p3 = (self.target_x, self.target_y)


        t = self.turn_progress


        x = (1 - t)**3 * p0[0] + 3 * (1 - t)**2 * t * p1[0] + 3 * (1 - t) * t**2 * p2[0] + t**3 * p3[0]
        y = (1 - t)**3 * p0[1] + 3 * (1 - t)**2 * t * p1[1] + 3 * (1 - t) * t**2 * p2[1] + t**3 * p3[1]


        dx = -3*(1 - t)**2 * p0[0] + 3*(1 - t)**2 * p1[0] - 6*(1 - t)*t * p1[0] + 6*(1 - t)*t * p2[0] - 3*t**2 * p2[0] + 3*t**2 * p3[0]
        dy = -3*(1 - t)**2 * p0[1] + 3*(1 - t)**2 * p1[1] - 6*(1 - t)*t * p1[1] + 6*(1 - t)*t * p2[1] - 3*t**2 * p2[1] + 3*t**2 * p3[1]


        length = (dx**2 + dy**2) ** 0.5
        if length == 0:
            length = 1
        dt = self.speed / length


        self.turn_progress += dt
        self.turn_progress = min(self.turn_progress, 1.0)


        self.x = x
        self.y = y


        if self.turn_progress >= 1.0:
            self.turning = False
            self.direction = "right"
            self.turn_progress = 0

    def _start_turn_into_7_2(self):

        self.turning = True
        self.direction = "smooth_right_turn"
        self.turn_start_x = self.x
        self.turn_start_y = self.y

        self.target_x = self.model.CENTER_X + self.model.SIM_WIDTH // 2
        self.target_y = self.model.CENTER_Y - self.model.LANE_WIDTH // 2 + self.model.LANE_WIDTH // 4

        self.turn_progress = 0
        self.speed = 2
    def _handle_smooth_down_turn(self):

        p0 = (self.turn_start_x, self.turn_start_y)
        p1 = (self.model.CENTER_X + 20, self.model.CENTER_Y + 20)
        p2 = (self.model.CENTER_X, self.model.CENTER_Y + 40)
        p3 = (self.target_x, self.target_y)


        t = self.turn_progress


        x = (1 - t)**3 * p0[0] + 3 * (1 - t)**2 * t * p1[0] + 3 * (1 - t) * t**2 * p2[0] + t**3 * p3[0]
        y = (1 - t)**3 * p0[1] + 3 * (1 - t)**2 * t * p1[1] + 3 * (1 - t) * t**2 * p2[1] + t**3 * p3[1]


        dx = -3*(1 - t)**2 * p0[0] + 3*(1 - t)**2 * p1[0] - 6*(1 - t)*t * p1[0] + 6*(1 - t)*t * p2[0] - 3*t**2 * p2[0] + 3*t**2 * p3[0]
        dy = -3*(1 - t)**2 * p0[1] + 3*(1 - t)**2 * p1[1] - 6*(1 - t)*t * p1[1] + 6*(1 - t)*t * p2[1] - 3*t**2 * p2[1] + 3*t**2 * p3[1]


        length = (dx**2 + dy**2) ** 0.5
        if length == 0:
            length = 1
        dt = self.speed / length


        self.turn_progress += dt
        self.turn_progress = min(self.turn_progress, 1.0)


        self.x = x
        self.y = y


        if self.turn_progress >= 1.0:
            self.turning = False
            self.direction = "down"
            self.turn_progress = 0

    def _handle_smooth_up_turn(self):

        p0 = (self.turn_start_x, self.turn_start_y)
        p1 = (self.model.CENTER_X - 20, self.model.CENTER_Y - 20)
        p2 = (self.model.CENTER_X, self.model.CENTER_Y - 40)
        p3 = (self.target_x, self.target_y)


        t = self.turn_progress


        x = (1 - t)**3 * p0[0] + 3 * (1 - t)**2 * t * p1[0] + 3 * (1 - t) * t**2 * p2[0] + t**3 * p3[0]
        y = (1 - t)**3 * p0[1] + 3 * (1 - t)**2 * t * p1[1] + 3 * (1 - t) * t**2 * p2[1] + t**3 * p3[1]


        dx = -3*(1 - t)**2 * p0[0] + 3*(1 - t)**2 * p1[0] - 6*(1 - t)*t * p1[0] + 6*(1 - t)*t * p2[0] - 3*t**2 * p2[0] + 3*t**2 * p3[0]
        dy = -3*(1 - t)**2 * p0[1] + 3*(1 - t)**2 * p1[1] - 6*(1 - t)*t * p1[1] + 6*(1 - t)*t * p2[1] - 3*t**2 * p2[1] + 3*t**2 * p3[1]


        length = (dx**2 + dy**2) ** 0.5
        if length == 0:
            length = 1
        dt = self.speed / length


        self.turn_progress += dt
        self.turn_progress = min(self.turn_progress, 1.0)


        self.x = x
        self.y = y

        if self.turn_progress >= 1.0:
            self.turning = False
            self.direction = "up"
            self.turn_progress = 0

    def _start_turn_into_1_1_or_7_1(self):
        if self.model.turn_counter_5_1 % 2 == 0:
            self.target_x = self.model.CENTER_X - self.model.LANE_WIDTH // 2 - self.model.LANE_WIDTH // 4
            self.target_y = self.model.CENTER_Y - self.model.SIM_HEIGHT // 2
            self.direction = "up"
        else:
            self.target_x = self.model.CENTER_X + self.model.SIM_WIDTH // 2
            self.target_y = self.model.CENTER_Y - self.model.LANE_WIDTH // 2 - self.model.LANE_WIDTH // 4
            self.direction = "right"
        self.turning = True
        self.speed = 2
        self.model.turn_counter_5_1 += 1

    def _start_turn_into_4_1(self):
        self.turning = True
        self.direction = "smooth_down_turn"
        self.turn_start_x = self.x
        self.turn_start_y = self.y
        self.target_x = self.model.CENTER_X + self.model.LANE_WIDTH//2 - self.model.LANE_WIDTH//4
        self.target_y = self.model.CENTER_Y + self.model.SIM_HEIGHT//2
        self.turn_progress = 0
        self.speed = 2

    def _start_turn_into_1_2(self):
        self.turning = True
        self.direction = "smooth_up_turn"
        self.turn_start_x = self.x
        self.turn_start_y = self.y
        self.target_x = self.model.CENTER_X - self.model.LANE_WIDTH//2 + self.model.LANE_WIDTH//4
        self.target_y = self.model.CENTER_Y - self.model.SIM_HEIGHT//2
        self.turn_progress = 0
        self.speed = 2

    def _handle_special_turn_to_1_2(self):
        if abs(self.x - self.target_x) > 1:

            self.x -= self.speed
        else:
            self.x = self.target_x
            if self.y > self.target_y:
                self.y -= self.speed
            else:
                self.y = self.target_y
                self.turning = False
                self.direction = "up"


    def _handle_special_turn_to_4_2(self):
        if abs(self.x - self.target_x) > 1:
            step = min(self.speed, abs(self.target_x - self.x))
            self.x += step * (1 if self.target_x > self.x else -1)
        else:
            self.x = self.target_x

            if abs(self.y - self.target_y) > 1:
                step = min(self.speed, abs(self.target_y - self.y))
                self.y += step
            else:
                self.y = self.target_y
                self.turning = False
                self.direction = "down"

    def _start_turn_into_4_2_or_6_2(self):
        self.turning = True
        self.speed = 2

        if self.model.turn_counter_8_2 % 2 == 0:

            self.direction = "special_turn_to_4_2"
            self.turn_start_x = self.x
            self.turn_start_y = self.y
            self.target_x = self.model.CENTER_X + self.model.LANE_WIDTH // 2 + self.model.LANE_WIDTH // 4
            self.target_y = self.model.CENTER_Y + self.model.SIM_HEIGHT // 2
            self.special_turn_progress = 0
        else:

            self.direction = "left"
            self.turn_phase = "final_approach"
            self.target_x = self.model.CENTER_X - self.model.SIM_WIDTH // 2
            self.target_y = self.model.CENTER_Y + self.model.LANE_WIDTH // 2 + self.model.LANE_WIDTH // 4

        self.model.turn_counter_8_2 += 1

    def _handle_special_turn(self):
        distance_x = abs(self.target_x - self.turn_start_x)
        distance_y = abs(self.target_y - self.turn_start_y)
        total_distance = distance_x + distance_y

        self.special_turn_progress = min(
            self.special_turn_progress + (self.speed / total_distance),
            1.0
        )

        if self.special_turn_progress < (distance_x / total_distance):

            progress = self.special_turn_progress / (distance_x / total_distance)
            self.x = self.turn_start_x + (self.target_x - self.turn_start_x) * progress
            self.y = self.turn_start_y
        else:
            self.x = self.target_x
            progress = (self.special_turn_progress - (distance_x / total_distance)) / (distance_y / total_distance)
            self.y = self.turn_start_y + (self.target_y - self.turn_start_y) * progress

        if self.special_turn_progress >= 1.0:
            self.direction = "down"
            self.turning = False
            self.special_turn_progress = 0
