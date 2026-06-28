import pygame

WHITE = (255, 255, 255)
ROAD = (50, 50, 50)
SOLID_DIVIDER = (255, 255, 255)
LANE_MARKINGS = (255, 255, 255)
SIM_BORDER = (0, 0, 0)
STOP_LINE_COLOR = (255, 0, 0)


ROAD_WIDTH = 150
LANE_WIDTH = ROAD_WIDTH // 2
INTERSECTION_SIZE = 100
DASH_LENGTH = 20
DASH_GAP = 20


pygame.font.init()
font = pygame.font.Font(None, 36)


def draw_dashed_line(surface, color, start_pos, end_pos, width=2):
    x1, y1 = start_pos
    x2, y2 = end_pos
    dx = x2 - x1
    dy = y2 - y1
    distance = (dx ** 2 + dy ** 2) ** 0.5
    num_dashes = distance // (DASH_LENGTH + DASH_GAP)

    for i in range(int(num_dashes)):
        start_dash = (x1 + (dx * i * (DASH_LENGTH + DASH_GAP) / distance),
                      y1 + (dy * i * (DASH_LENGTH + DASH_GAP) / distance))
        end_dash = (x1 + (dx * (i * (DASH_LENGTH + DASH_GAP) + DASH_LENGTH) / distance),
                    y1 + (dy * (i * (DASH_LENGTH + DASH_GAP) + DASH_LENGTH) / distance))
        pygame.draw.line(surface, color, start_dash, end_dash, width)


def draw_text(surface, text, x, y):
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect(center=(x, y))
    surface.blit(text_surface, text_rect)


def draw_intersection(surface, center_x, center_y, height, sim_x_offset, sim_width):
    pygame.draw.rect(surface, ROAD, (center_x - INTERSECTION_SIZE // 2, center_y - INTERSECTION_SIZE // 2, INTERSECTION_SIZE, INTERSECTION_SIZE))

    # Vertical roads
    pygame.draw.rect(surface, ROAD, (center_x - ROAD_WIDTH // 2, center_y - sim_width // 2, LANE_WIDTH, sim_width))
    pygame.draw.rect(surface, ROAD, (center_x, center_y - sim_width // 2, LANE_WIDTH, sim_width))

    # Horizontal roads
    pygame.draw.rect(surface, ROAD, (sim_x_offset, center_y - ROAD_WIDTH // 2, center_x - INTERSECTION_SIZE // 2 - sim_x_offset, LANE_WIDTH))
    pygame.draw.rect(surface, ROAD, (sim_x_offset, center_y, center_x - INTERSECTION_SIZE // 2 - sim_x_offset, LANE_WIDTH))
    pygame.draw.rect(surface, ROAD, (center_x + INTERSECTION_SIZE // 2, center_y - ROAD_WIDTH // 2, sim_x_offset + sim_width - (center_x + INTERSECTION_SIZE // 2), LANE_WIDTH))
    pygame.draw.rect(surface, ROAD, (center_x + INTERSECTION_SIZE // 2, center_y, sim_x_offset + sim_width - (center_x + INTERSECTION_SIZE // 2), LANE_WIDTH))

    # Solid dividers
    pygame.draw.line(surface, SOLID_DIVIDER, (center_x, center_y - sim_width // 2), (center_x, center_y -20 - INTERSECTION_SIZE // 2), 3)
    pygame.draw.line(surface, SOLID_DIVIDER, (center_x, center_y + 20 + INTERSECTION_SIZE // 2), (center_x, center_y + sim_width // 2), 3)
    pygame.draw.line(surface, SOLID_DIVIDER, (sim_x_offset, center_y), (center_x -20- INTERSECTION_SIZE // 2, center_y), 3)
    pygame.draw.line(surface, SOLID_DIVIDER, (center_x+20+ INTERSECTION_SIZE // 2, center_y), (sim_x_offset + sim_width, center_y), 3)

    # dashed white lines
    draw_dashed_line(surface, LANE_MARKINGS, (center_x - LANE_WIDTH // 2, center_y - sim_width // 2), (center_x - LANE_WIDTH // 2, center_y - INTERSECTION_SIZE // 2))
    draw_dashed_line(surface, LANE_MARKINGS, (center_x - LANE_WIDTH // 2, center_y +30+ INTERSECTION_SIZE // 2), (center_x - LANE_WIDTH // 2, center_y + sim_width // 2))

    draw_dashed_line(surface, LANE_MARKINGS, (center_x + LANE_WIDTH // 2, center_y - sim_width // 2), (center_x + LANE_WIDTH // 2, center_y - INTERSECTION_SIZE // 2))
    draw_dashed_line(surface, LANE_MARKINGS, (center_x + LANE_WIDTH // 2, center_y +30 + INTERSECTION_SIZE // 2), (center_x + LANE_WIDTH // 2, center_y + sim_width // 2))

    draw_dashed_line(surface, LANE_MARKINGS, (sim_x_offset, center_y - LANE_WIDTH // 2), (center_x - INTERSECTION_SIZE // 2, center_y - LANE_WIDTH // 2))
    draw_dashed_line(surface, LANE_MARKINGS, (center_x + 30+ INTERSECTION_SIZE // 2, center_y - LANE_WIDTH // 2), (sim_x_offset + sim_width, center_y - LANE_WIDTH // 2))

    draw_dashed_line(surface, LANE_MARKINGS, (sim_x_offset, center_y + LANE_WIDTH // 2), (center_x - INTERSECTION_SIZE // 2, center_y + LANE_WIDTH // 2))
    draw_dashed_line(surface, LANE_MARKINGS, (center_x + 30 + INTERSECTION_SIZE // 2, center_y + LANE_WIDTH // 2), (sim_x_offset + sim_width, center_y + LANE_WIDTH // 2))

    stop_line_width = 5
    stop_line_length = LANE_WIDTH
    STOP_LINE_OFFSET = 20

    # Vertical stop lines
    pygame.draw.line(surface, STOP_LINE_COLOR,
                    (center_x - ROAD_WIDTH // 2, center_y - INTERSECTION_SIZE // 2 - STOP_LINE_OFFSET),
                    (center_x - ROAD_WIDTH // 2 + stop_line_length, center_y - INTERSECTION_SIZE // 2 - STOP_LINE_OFFSET),
                    stop_line_width)
    pygame.draw.line(surface, STOP_LINE_COLOR,
                    (center_x, center_y - INTERSECTION_SIZE // 2 - STOP_LINE_OFFSET),
                    (center_x + stop_line_length, center_y - INTERSECTION_SIZE // 2 - STOP_LINE_OFFSET),
                    stop_line_width)
    pygame.draw.line(surface, STOP_LINE_COLOR,
                    (center_x - ROAD_WIDTH // 2, center_y + INTERSECTION_SIZE // 2 + STOP_LINE_OFFSET),
                    (center_x - ROAD_WIDTH // 2 + stop_line_length, center_y + INTERSECTION_SIZE // 2 + STOP_LINE_OFFSET),
                    stop_line_width)
    pygame.draw.line(surface, STOP_LINE_COLOR,
                    (center_x, center_y + INTERSECTION_SIZE // 2 + STOP_LINE_OFFSET),
                    (center_x + stop_line_length, center_y + INTERSECTION_SIZE // 2 + STOP_LINE_OFFSET),
                    stop_line_width)

    # Horizontal stop lines
    pygame.draw.line(surface, STOP_LINE_COLOR,
                    (center_x - INTERSECTION_SIZE // 2 - STOP_LINE_OFFSET, center_y - ROAD_WIDTH // 2),
                    (center_x - INTERSECTION_SIZE // 2 - STOP_LINE_OFFSET, center_y - ROAD_WIDTH // 2 + stop_line_length),
                    stop_line_width)
    pygame.draw.line(surface, STOP_LINE_COLOR,
                    (center_x - INTERSECTION_SIZE // 2 - STOP_LINE_OFFSET, center_y),
                    (center_x - INTERSECTION_SIZE // 2 - STOP_LINE_OFFSET, center_y + stop_line_length),
                    stop_line_width)
    pygame.draw.line(surface, STOP_LINE_COLOR,
                    (center_x + INTERSECTION_SIZE // 2 + STOP_LINE_OFFSET, center_y - ROAD_WIDTH // 2),
                    (center_x + INTERSECTION_SIZE // 2 + STOP_LINE_OFFSET, center_y - ROAD_WIDTH // 2 + stop_line_length),
                    stop_line_width)
    pygame.draw.line(surface, STOP_LINE_COLOR,
                    (center_x + INTERSECTION_SIZE // 2 + STOP_LINE_OFFSET, center_y),
                    (center_x + INTERSECTION_SIZE // 2 + STOP_LINE_OFFSET, center_y + stop_line_length),
                    stop_line_width)

    draw_text(surface, "1.1", center_x - LANE_WIDTH // 2 - LANE_WIDTH // 4, center_y - INTERSECTION_SIZE)
    draw_text(surface, "1.2", center_x - LANE_WIDTH // 2 + LANE_WIDTH // 4, center_y - INTERSECTION_SIZE)
    draw_text(surface, "2.1", center_x + LANE_WIDTH // 2 - LANE_WIDTH // 4, center_y - INTERSECTION_SIZE)
    draw_text(surface, "2.2", center_x + LANE_WIDTH // 2 + LANE_WIDTH // 4, center_y - INTERSECTION_SIZE)
    draw_text(surface, "3.1", center_x - LANE_WIDTH // 2 - LANE_WIDTH // 4, center_y + INTERSECTION_SIZE)
    draw_text(surface, "3.2", center_x - LANE_WIDTH // 2 + LANE_WIDTH // 4, center_y + INTERSECTION_SIZE)
    draw_text(surface, "4.1", center_x + LANE_WIDTH // 2 - LANE_WIDTH // 4, center_y + INTERSECTION_SIZE)
    draw_text(surface, "4.2", center_x + LANE_WIDTH // 2 + LANE_WIDTH // 4, center_y + INTERSECTION_SIZE)
    draw_text(surface, "5.1", center_x - INTERSECTION_SIZE, center_y - LANE_WIDTH // 2 - LANE_WIDTH // 4)
    draw_text(surface, "5.2", center_x - INTERSECTION_SIZE, center_y - LANE_WIDTH // 2 + LANE_WIDTH // 4)
    draw_text(surface, "6.1", center_x - INTERSECTION_SIZE, center_y + LANE_WIDTH // 2 - LANE_WIDTH // 4)
    draw_text(surface, "6.2", center_x - INTERSECTION_SIZE, center_y + LANE_WIDTH // 2 + LANE_WIDTH // 4)
    draw_text(surface, "7.1", center_x + INTERSECTION_SIZE, center_y - LANE_WIDTH // 2 - LANE_WIDTH // 4)
    draw_text(surface, "7.2", center_x + INTERSECTION_SIZE, center_y - LANE_WIDTH // 2 + LANE_WIDTH // 4)
    draw_text(surface, "8.2", center_x + INTERSECTION_SIZE, center_y + LANE_WIDTH // 2 - LANE_WIDTH // 4)
    draw_text(surface, "8.1", center_x + INTERSECTION_SIZE, center_y + LANE_WIDTH // 2 + LANE_WIDTH // 4)
