import pygame
pygame.font.init()
font = pygame.font.Font(None, 30)
label_font = pygame.font.Font(None, 24)

class UI:
    def __init__(self):
        BUTTON_WIDTH = 150
        BUTTON_HEIGHT = 40
        BUTTON_SPACING = 10
        BUTTON_Y = 20
        BUTTON_X_START = 20

        self.button_colors = {
            "Start/Continue": {
                "normal": (76, 175, 80),
                "hover": (56, 142, 60),
                "text": (255, 255, 255)
            },
            "Pause": {
                "normal": (244, 67, 54),
                "hover": (211, 47, 47),
                "text": (255, 255, 255)
            },
            "Reset": {
                "normal": (33, 150, 243),
                "hover": (25, 118, 210),
                "text": (255, 255, 255)
            }
        }
        self.buttons = {
            "Start/Continue": pygame.Rect(BUTTON_X_START, BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT),
            "Pause": pygame.Rect(BUTTON_X_START + BUTTON_WIDTH + BUTTON_SPACING, BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT),
            "Reset": pygame.Rect(BUTTON_X_START + 2*(BUTTON_WIDTH + BUTTON_SPACING), BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT)
        }
        self.driver_type_labels = {
            "red": "А",
            "green": "Қ",
            "blue": "С"
        }
        self.driver_label_y = 80

        INPUT_BOX_WIDTH = 40
        INPUT_BOX_HEIGHT = 30
        ROAD_SPACING = 50
        START_Y = 110

        self.roads = [
            {"label": "Жол 2.1", "inputs": {
                "red": {"color": (255, 200, 200)},
                "green": {"color": (200, 255, 200)},
                "blue": {"color": (200, 200, 255)}
            }},
            {"label": "Жол 2.2", "inputs": {
                "red": {"color": (255, 200, 200)},
                "green": {"color": (200, 255, 200)},
                "blue": {"color": (200, 200, 255)}
            }},
            {"label": "Жол 3.1", "inputs": {
                "red": {"color": (255, 200, 200)},
                "green": {"color": (200, 255, 200)},
                "blue": {"color": (200, 200, 255)}
            }},
            {"label": "Жол 3.2", "inputs": {
                "red": {"color": (255, 200, 200)},
                "green": {"color": (200, 255, 200)},
                "blue": {"color": (200, 200, 255)}
            }},
            {"label": "Жол 5.1", "inputs": {
                "red": {"color": (255, 200, 200)},
                "green": {"color": (200, 255, 200)},
                "blue": {"color": (200, 200, 255)}
            }},
            {"label": "Жол 5.2", "inputs": {
                "red": {"color": (255, 200, 200)},
                "green": {"color": (200, 255, 200)},
                "blue": {"color": (200, 200, 255)}
            }},
            {"label": "Жол 8.1", "inputs": {
                "red": {"color": (255, 200, 200)},
                "green": {"color": (200, 255, 200)},
                "blue": {"color": (200, 200, 255)}
            }},
            {"label": "Жол 8.2", "inputs": {
                "red": {"color": (255, 200, 200)},
                "green": {"color": (200, 255, 200)},
                "blue": {"color": (200, 200, 255)}
            }}
        ]

        for i, road in enumerate(self.roads):
            y_pos = START_Y + i * ROAD_SPACING
            road["label_rect"] = pygame.Rect(20, y_pos, 80, 30)
            road["inputs"]["red"]["rect"] = pygame.Rect(110, y_pos, INPUT_BOX_WIDTH, INPUT_BOX_HEIGHT)
            road["inputs"]["red"]["text"] = ""
            road["inputs"]["green"]["rect"] = pygame.Rect(180, y_pos, INPUT_BOX_WIDTH, INPUT_BOX_HEIGHT)
            road["inputs"]["green"]["text"] = ""
            road["inputs"]["blue"]["rect"] = pygame.Rect(250, y_pos, INPUT_BOX_WIDTH, INPUT_BOX_HEIGHT)
            road["inputs"]["blue"]["text"] = ""

        self.active_road_input = None

    def draw_button(self, screen, button_name, mouse_pos):
        button_rect = self.buttons[button_name]
        colors = self.button_colors[button_name]

        hover = button_rect.collidepoint(mouse_pos)
        color = colors["hover"] if hover else colors["normal"]

        pygame.draw.rect(screen, color, button_rect, border_radius=5)
        pygame.draw.rect(screen, (200, 200, 200), button_rect, 2, border_radius=5)

        text_surface = font.render(button_name, True, colors["text"])
        text_rect = text_surface.get_rect(center=button_rect.center)
        screen.blit(text_surface, text_rect)

        return button_rect

    def draw_input_box(self, screen):
        for i, (car_type, label) in enumerate(self.driver_type_labels.items()):
            label_surface = label_font.render(label, True, (0, 0, 0))
            screen.blit(label_surface, (110 + i * 70, self.driver_label_y))

        for road in self.roads:
            label_surface = font.render(road["label"], True, (0, 0, 0))
            screen.blit(label_surface, (road["label_rect"].x, road["label_rect"].y + 5))

            for car_type, input_data in road["inputs"].items():
                is_active = self.active_road_input == (road["label"].split()[-1], car_type)
                bg_color = (255, 255, 255) if is_active else input_data["color"]
                pygame.draw.rect(screen, bg_color, input_data["rect"], border_radius=3)
                pygame.draw.rect(screen, (200, 200, 200), input_data["rect"], 2, border_radius=3)
                text_surface = font.render(input_data["text"], True, (0, 0, 0))
                screen.blit(text_surface, (input_data["rect"].x + 5, input_data["rect"].y + 5))
