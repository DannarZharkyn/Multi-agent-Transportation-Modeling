import pygame

TRAFFIC_LIGHT_STATES = ["red", "yellow", "green"]
TRAFFIC_LIGHT_COLORS = {"red": (255, 0, 0), "yellow": (255, 255, 0), "green": (0, 255, 0)}

class TrafficLight:
    def __init__(self, id, center_x, center_y):
        self.id = id
        self.state = "red"
        self.timer = 0
        self.center_x = center_x
        self.center_y = center_y
        self.base_timings = {"red": 0, "yellow": 150, "green": 450}
        self.dynamic_timings = None
        self.car_count = 0
        self.current_green_time = 15


        if "2.1_2.2" in id:  # Light
            self.size = 9
            self.x = center_x - 10
            self.y = center_y - 10
        elif "3.1_3.2" in id:  # Light 2
            self.size = 7
            self.x = center_x + 10
            self.y = center_y  - 10
        elif "5.1_5.2" in id:  #  Light 3
            self.size = 9
            self.x = center_x
            self.y = center_y + 10
        elif "8.1_8.2" in id:  # Light 4
            self.size = 7
            self.x = center_x
            self.y = center_y + 25
        # Қазіргі уақыттағы бағдаршамның жұмыс уақытын алу (динамикалық болса, соны, болмаса негізгі уақытты қайтарады)
    def get_current_timings(self):
        return self.dynamic_timings if self.dynamic_timings else self.base_timings
        # Бағдаршамның күйін жаңарту (қолданыстағы бағдаршам болса, таймерді арттырады және күйді ауыстырады)
    def update(self, active_traffic_light_id):
        timings = self.get_current_timings()
        # Егер бұл бағдаршам қазіргі белсенді бағдаршам болса
        if self.id == active_traffic_light_id:
            self.timer += 1 # Таймерді 1-ге арттырамыз
             # Егер бағдаршам жасыл күйде болса және уақыты аяқталса
            if self.state == "green" and self.timer >= timings["green"]:
                self.state = "yellow"
                self.timer = 0
            elif self.state == "yellow" and self.timer >= timings["yellow"]:
                self.state = "red"
                self.timer = 0
        else:
            self.state = "red"
            self.timer = 0

    def draw(self, surface):
        pygame.draw.circle(surface, TRAFFIC_LIGHT_COLORS[self.state], (self.x, self.y), self.size)
        font = pygame.font.Font(None, 14)
        label = ""
        if "2.1_2.2" in self.id:
            label = "1"
        elif "3.1_3.2" in self.id:
            label = "2"
        elif "5.1_5.2" in self.id:
            label = "3"
        elif "8.1_8.2" in self.id:
            label = "4"

        text = font.render(label, True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.x, self.y))
        surface.blit(text, text_rect)
