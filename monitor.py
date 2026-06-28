import pygame
from pygame import gfxdraw
import math
import os

class TrafficMonitor:
    def __init__(self, x, y, width, height, model):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.model = model
        self.font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 30)
        self.chart_padding = 20
        self.chart_height = 150
        self.history_length = 50
        self.moving_history = []
        self.waiting_history = []
        self.time_counter = 0
        try:
            font_path = None
            possible_fonts = [
                'arial.ttf',
                'DejaVuSans.ttf',
                'Arial Unicode.ttf',
                '/System/Library/Fonts/Supplemental/Arial.ttf'
            ]

            for font in possible_fonts:
                if os.path.exists(font):
                    font_path = font
                    break

            if font_path:
                self.font = pygame.font.Font(font_path, 20)
                self.title_font = pygame.font.Font(font_path, 26)
            else:
                self.font = pygame.font.Font(None, 20)
                self.title_font = pygame.font.Font(None, 26)
        except:
            self.font = pygame.font.Font(None, 20)
            self.title_font = pygame.font.Font(None, 26)

    def draw(self, surface):
        pygame.draw.rect(surface, (240, 240, 240), (self.x, self.y, self.width, self.height))
        pygame.draw.rect(surface, (200, 200, 200), (self.x, self.y, self.width, self.height), 2)

        title = self.title_font.render("Көлік жүйесі", True, (0, 0, 0))
        surface.blit(title, (self.x + (self.width - title.get_width()) // 2, self.y + 10))

        moving, waiting = self.model.count_cars()
        self._update_history(moving, waiting)
        self._draw_chart(surface)

        stats_y = self.y + self.chart_height + self.chart_padding + 40

        minutes = int(self.time_counter) // 60
        seconds = int(self.time_counter) % 60
        time_text = self.font.render(f"Уақыт: {minutes}м {seconds}с", True, (0, 0, 0))
        total_seconds = int(self.time_counter)
        minutes = total_seconds // 60
        seconds = total_seconds % 60


        time_text = self.font.render(
            f"Уақыт: {minutes}м {seconds}с",
            True,
            (0, 0, 0)
        )
        surface.blit(time_text, (self.x + 20, stats_y))

        if self.model.running_simulation:
            self.time_counter += 1/30

        total = moving + waiting

        total_text = self.font.render(f"Барлық көлік саны: {total}", True, (0, 0, 0))
        moving_text = self.font.render(f"Қозғалу: {moving}", True, (0, 128, 0))
        waiting_text = self.font.render(f"Тоқтау: {waiting}", True, (200, 0, 0))

        surface.blit(total_text, (self.x + 20, stats_y + 30))
        surface.blit(moving_text, (self.x + 20, stats_y + 60))
        surface.blit(waiting_text, (self.x + 20, stats_y + 90))

        legend_y = stats_y + 130
        pygame.draw.rect(surface, (0, 200, 0), (self.x + 20, legend_y, 15, 15))
        surface.blit(self.font.render("Қозғалу", True, (0, 0, 0)), (self.x + 40, legend_y))

        pygame.draw.rect(surface, (200, 0, 0), (self.x + 120, legend_y, 15, 15))
        surface.blit(self.font.render("Тоқтау", True, (0, 0, 0)), (self.x + 140, legend_y))

        density = self.model.current_density()
        density_text = self.font.render(f"Жол жүктемесі: {density:.1f}%", True, (0, 0, 0))
        surface.blit(density_text, (self.x + 20, legend_y + 30))

        timing_y = legend_y + 70
        title = self.font.render("Бағдаршам жарығы:", True, (0, 0, 0))
        surface.blit(title, (self.x + 20, timing_y))

        road_info = [
            ("Жол 2.2 + 3.1", self.model.get_road_car_counts_for_display().get("2", 0)),
            ("Жол 3.2 + 2.1", self.model.get_road_car_counts_for_display().get("3", 0)),
            ("Жол 5.1 + 8.1", self.model.get_road_car_counts_for_display().get("5", 0)),
            ("Жол 5.2 + 8.2", self.model.get_road_car_counts_for_display().get("8", 0))
        ]

        y_offset = timing_y + 30
        for road, count in road_info:
            green_time = 15
            for light in self.model.traffic_lights.values():
                if road.split()[1] in light.id:
                    green_time = light.current_green_time
                    break

            text = f"{road}: {count} көлік | {green_time}c жасыл"
            text_surface = self.font.render(text, True, (0, 0, 0))
            surface.blit(text_surface, (self.x + 20, y_offset))
            y_offset += 25


    def _update_history(self, moving, waiting):
        self.moving_history.append(moving)
        self.waiting_history.append(waiting)

        if len(self.moving_history) > self.history_length:
            self.moving_history.pop(0)
            self.waiting_history.pop(0)

    def reset(self):
        self.moving_history = []
        self.waiting_history = []
        self.time_counter = 0

    def update_model(self, new_model):
        self.model = new_model
        self.reset()

    def _draw_chart(self, surface):
        # Графиктің сол жақ жоғарғы бұрыш координаталарын анықтау
        chart_x = self.x + self.chart_padding + 40
        chart_y = self.y + 50
        chart_width = self.width - 2 * self.chart_padding - 40
        chart_area_height = self.chart_height
        # График салынатын ақ түсті тікбұрышты аймақты салу
        pygame.draw.rect(surface, (255, 255, 255), (chart_x, chart_y, chart_width, chart_area_height))
        pygame.draw.rect(surface, (200, 200, 200), (chart_x, chart_y, chart_width, chart_area_height), 1)
        # Ең үлкен мәнді табу (график шкаласы үшін), нөлден жоғары болуын қамтамасыз ету
        max_value = max(max(self.moving_history + [1]), max(self.waiting_history + [1]))
        max_value = ((max_value // 10) + 1) * 10
        # Горизонталды сызықтарды және оларға сәйкес мәндерді салу (5 бөлікке бөлу)

        for i in range(0, 6):
            value = i * (max_value // 5)
            y_pos = chart_y + chart_area_height - (i * chart_area_height // 5)


            pygame.draw.line(surface, (220, 220, 220),
                        (chart_x, y_pos), (chart_x + chart_width, y_pos), 1)


            value_text = self.font.render(str(value), True, (0, 0, 0))
            surface.blit(value_text, (self.x + self.chart_padding, y_pos - 10))


        if len(self.moving_history) > 1:
            points = []
            for i, value in enumerate(self.moving_history):
                x = chart_x + (i * chart_width) // (self.history_length - 1)
                y = chart_y + chart_area_height - (value * chart_area_height) // max_value
                points.append((x, y))
            # Егер екі немесе одан көп нүкте болса, жасыл сызықпен қосу
            if len(points) > 1:
                pygame.draw.lines(surface, (0, 200, 0), False, points, 2)

        if len(self.waiting_history) > 1:
            points = []
            for i, value in enumerate(self.waiting_history):
                x = chart_x + (i * chart_width) // (self.history_length - 1)
                y = chart_y + chart_area_height - (value * chart_area_height) // max_value
                points.append((x, y))
            # Қызыл түспен күту мәндерін қосу
            if len(points) > 1:
                pygame.draw.lines(surface, (200, 0, 0), False, points, 2)

        # Соңғы қозғалыстағы және күту мәндерін көрсету (оң жақ жоғарғы бұрышта)
        if self.moving_history:
            current_moving = self.moving_history[-1]
            current_waiting = self.waiting_history[-1]

            moving_text = self.font.render(str(current_moving), True, (0, 200, 0))
            waiting_text = self.font.render(str(current_waiting), True, (200, 0, 0))

            surface.blit(moving_text, (chart_x + chart_width - 50, chart_y + 5))
            surface.blit(waiting_text, (chart_x + chart_width - 50, chart_y + 25))
