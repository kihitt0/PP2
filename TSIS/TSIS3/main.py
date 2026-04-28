"""Racer – TSIS 3 entry point."""

import sys
import pygame

import persistence as ps
import racer
import ui

W, H = racer.W, racer.H


def main():
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Racer – TSIS 3")
    clock = pygame.time.Clock()

    font_large  = pygame.font.SysFont("Consolas", 52, bold=True)
    font_medium = pygame.font.SysFont("Consolas", 28, bold=True)
    font_small  = pygame.font.SysFont("Consolas", 17, bold=True)
    ui_fonts    = (font_large, font_medium, font_small)

    # racer.run_game expects (font_small, font_medium, font_large)
    game_fonts  = (font_small, font_medium, font_large)

    settings = ps.load_settings()
    state    = "menu"
    last_score, last_dist, last_coins = 0, 0, 0
    player_name = "Player"

    while True:
        if state == "menu":
            action = ui.main_menu(screen, clock, ui_fonts)
            if action == "play":
                player_name = ui.name_entry_screen(screen, clock, ui_fonts)
                state = "game"
            elif action == "leaderboard":
                state = "leaderboard"
            elif action == "settings":
                state = "settings"
            else:
                pygame.quit()
                sys.exit()

        elif state == "game":
            last_score, last_dist, last_coins = racer.run_game(screen, clock, settings, game_fonts)
            ps.add_entry(player_name, last_score, last_dist)
            state = "gameover"

        elif state == "gameover":
            action = ui.game_over_screen(screen, clock, ui_fonts,
                                         last_score, last_dist, last_coins)
            if action == "retry":
                state = "game"
            else:
                player_name = "Player"
                state = "menu"

        elif state == "leaderboard":
            ui.leaderboard_screen(screen, clock, ui_fonts)
            state = "menu"

        elif state == "settings":
            settings = ui.settings_screen(screen, clock, ui_fonts, settings)
            state = "menu"


if __name__ == "__main__":
    main()
