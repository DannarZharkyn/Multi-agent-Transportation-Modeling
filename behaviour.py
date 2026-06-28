class CarBehavior:
    @staticmethod

    def aggressive_behavior(car, traffic_light):
        if not traffic_light:
            car.speed = 2.1
            car.min_distance = 20
            car._maintain_car_spacing()
            return

        if traffic_light.state == "yellow":
                car.speed = 2.5
        elif traffic_light.state == "red":
            if car._is_in_intersection():
                car.speed = 2.1
            elif car._is_at_intersection():
                car.speed = 0
            else:
                car.speed = 2.1
        else:
            car.speed = 2.1

        car.min_distance = 20
        car._maintain_car_spacing()

    @staticmethod
    def cautious_behavior(car, traffic_light):

        if not hasattr(car, 'light_change_timer'):
            car.light_change_timer = 0

        if traffic_light and traffic_light.state == "green":
            car.light_change_timer += 1

            if car.light_change_timer >= 30:
                car.speed = 1.9
            else:
                car.speed = 0
        else:
            car.light_change_timer = 0
            if car._is_at_intersection():
                car.speed = 0
            else:
                car.speed = 1.9

        car.min_distance = 40
        car._maintain_car_spacing()

    @staticmethod
    def standard_behavior(car, traffic_light):
        if traffic_light.state == "green":
            car.speed = 2
        else:
            if car._is_at_intersection():
                car.speed = 0
            else:
                car.speed = 2
        car.min_distance = 30
        car._maintain_car_spacing()
