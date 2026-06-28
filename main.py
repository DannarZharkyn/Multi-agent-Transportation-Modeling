import pygame
import asyncio
import random
from traffic_model import TrafficModel
from traffic_light import TrafficLight
from ui import UI
from intersection import draw_intersection
from monitor import TrafficMonitor

# The simulation has no audio. Initializing only the modules we use avoids
# browser autoplay/media permission gates in the WebAssembly build.
pygame.display.init()
pygame.font.init()

WIDTH, HEIGHT = 1300, 800
SIM_X_OFFSET = 300
SIM_WIDTH = 600
SIM_HEIGHT = 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Мультиагенттік жүйе негізінде көлік қозғалысын симуляциялау")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
CAR_COLORS = {
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255)
}


ROAD_WIDTH = 150
LANE_WIDTH = ROAD_WIDTH // 2
CAR_SIZE = 15
MIN_CAR_DISTANCE = 30
INTERSECTION_SIZE = 100


CENTER_X, CENTER_Y = WIDTH // 2, HEIGHT // 2


ROAD2_LANE1_X = CENTER_X + LANE_WIDTH // 2 - LANE_WIDTH // 4
ROAD2_LANE2_X = CENTER_X + LANE_WIDTH // 2 + LANE_WIDTH // 4


ROAD3_LANE1_X = CENTER_X - LANE_WIDTH // 2 - LANE_WIDTH // 4
ROAD3_LANE2_X = CENTER_X - LANE_WIDTH // 2 + LANE_WIDTH // 4
ROAD5_LANE1_Y = CENTER_Y - LANE_WIDTH // 2 - LANE_WIDTH // 4
ROAD5_LANE2_Y = CENTER_Y - LANE_WIDTH // 2 + LANE_WIDTH // 4


model = TrafficModel(False, CENTER_X, CENTER_Y, HEIGHT, MIN_CAR_DISTANCE, INTERSECTION_SIZE, LANE_WIDTH, SIM_WIDTH, SIM_HEIGHT)
ui = UI()

monitor_width = 350
monitor = TrafficMonitor(
    x=CENTER_X + SIM_WIDTH//2 + 10,
    y=CENTER_Y - SIM_HEIGHT//2,
    width=monitor_width,
    height=SIM_HEIGHT,
    model=model
)

def get_road_inputs(road_num):
    for road in ui.roads:
        if road["label"].split()[-1] == road_num:
            return road["inputs"]
    return None


async def main():
    global model
    running = True
    clock = pygame.time.Clock()
    simulation_started = False

    while running:
        screen.fill(WHITE)


        frame_thickness = 5
        pygame.draw.rect(screen, BLACK, (CENTER_X - SIM_WIDTH // 2 - frame_thickness,
                                       CENTER_Y - SIM_WIDTH // 2 - frame_thickness,
                                       SIM_WIDTH + 2 * frame_thickness,
                                       SIM_WIDTH + 2 * frame_thickness), frame_thickness)


        draw_intersection(screen, CENTER_X, CENTER_Y, HEIGHT, CENTER_X - SIM_WIDTH // 2, SIM_WIDTH)


        for traffic_light in model.traffic_lights.values():
            traffic_light.draw(screen)


        mouse_pos = pygame.mouse.get_pos()


        button_rects = {}
        for button_name in ui.buttons:
            rect = ui.draw_button(screen, button_name, mouse_pos)
            button_rects[button_name] = rect


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:

                ui.active_road_input = None
                for road in ui.roads:
                    road_num = road["label"].split()[-1]
                    for car_type, input_data in road["inputs"].items():
                        if input_data["rect"].collidepoint(event.pos):
                            ui.active_road_input = (road_num, car_type)
                            break
                    if ui.active_road_input:
                        break


                for button_name, rect in button_rects.items():
                    if rect.collidepoint(event.pos):
                        if button_name == "Start/Continue":
                            if not simulation_started:

                                max_density = 60
                                current_density = model.current_density()

                                if current_density >= max_density:
                                    print(f"Density limit reached ({max_density}%) - no new cars spawned")
                                    continue

                                cars_to_spawn = []
                                for road in ui.roads:
                                    road_num = road["label"].split()[-1]
                                    inputs = road["inputs"]

                                    for car_type, input_data in inputs.items():
                                        try:
                                            num_cars = int(input_data["text"])
                                            if num_cars <= 0:
                                                continue

                                            if road_num in ["2.1", "2.2"]:
                                                lane_x = ROAD2_LANE1_X if road_num == "2.1" else ROAD2_LANE2_X
                                                for i in range(num_cars):
                                                    cars_to_spawn.append((road_num, lane_x, 50 + i * MIN_CAR_DISTANCE, "down", car_type))

                                            elif road_num in ["3.1", "3.2"]:
                                                lane_x = ROAD3_LANE1_X if road_num == "3.1" else ROAD3_LANE2_X
                                                for i in range(num_cars):
                                                    start_y = CENTER_Y + (SIM_HEIGHT // 2) - (i * MIN_CAR_DISTANCE)
                                                    cars_to_spawn.append((road_num, lane_x, start_y, "up", car_type))

                                            elif road_num in ["5.1", "5.2"]:
                                                lane_y = ROAD5_LANE1_Y if road_num == "5.1" else ROAD5_LANE2_Y
                                                for i in range(num_cars):
                                                    start_x = CENTER_X - SIM_WIDTH//2 + i * (MIN_CAR_DISTANCE + CAR_SIZE)
                                                    cars_to_spawn.append((road_num, start_x, lane_y, "right", car_type))

                                            elif road_num in ["8.1", "8.2"]:
                                                lane_offset = LANE_WIDTH//4 if road_num == "8.1" else -LANE_WIDTH//4
                                                for i in range(num_cars):
                                                    start_x = CENTER_X + SIM_WIDTH//2 - i * (MIN_CAR_DISTANCE + CAR_SIZE)
                                                    cars_to_spawn.append((road_num, start_x, CENTER_Y + LANE_WIDTH//2 + lane_offset, "left", car_type))
                                        except ValueError:
                                            pass

                                random.shuffle(cars_to_spawn)

                                for car_info in cars_to_spawn:
                                    lane, x, y, direction, car_type = car_info
                                    model.add_car(x, y, direction, lane, car_type)
                                model.start_simulation()
                                simulation_started = True
                            else:

                                model.running_simulation = True

                        elif button_name == "Pause":
                            model.running_simulation = False

                        elif button_name == "Reset":
                            model.running_simulation = False
                            new_model = TrafficModel(False, CENTER_X, CENTER_Y, HEIGHT, MIN_CAR_DISTANCE,
                                                INTERSECTION_SIZE, LANE_WIDTH, SIM_WIDTH, SIM_HEIGHT)
                            monitor.update_model(new_model)
                            monitor.reset()
                            model = new_model
                            simulation_started = False


                            for road in ui.roads:
                                for input_data in road["inputs"].values():
                                    input_data["text"] = ""

            elif event.type == pygame.KEYDOWN:
                if ui.active_road_input is not None:
                    road_num, car_type = ui.active_road_input
                    for road in ui.roads:
                        if road["label"].split()[-1] == road_num:
                            inputs = road["inputs"]
                            if event.key == pygame.K_BACKSPACE:
                                inputs[car_type]["text"] = inputs[car_type]["text"][:-1]
                            elif event.unicode.isdigit():
                                inputs[car_type]["text"] += event.unicode
                            break

        if model.running_simulation:
            model.step()

        ui.draw_input_box(screen)

        # Draw cars
        for car in model.cars:
            if model.is_visible(car):
                car_color = CAR_COLORS.get(car.car_type, (0, 255, 0))
                pygame.draw.rect(screen, car_color,
                               (car.x - CAR_SIZE//2,
                                car.y - CAR_SIZE//2,
                                CAR_SIZE, CAR_SIZE))

        monitor.draw(screen)

        pygame.display.update()
        clock.tick(30)
        await asyncio.sleep(0)

    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
