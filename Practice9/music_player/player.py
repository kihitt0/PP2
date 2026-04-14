"""
player.py - Music Player Logic
Manages the playlist, track state, and pygame.mixer interactions.
"""

import os
import pygame


class MusicPlayer:
    """
    Encapsulates all music playback logic.
    Handles loading tracks, play/stop/next/prev, and status reporting.
    """

    SUPPORTED_EXTS = (".mp3", ".wav", ".ogg", ".flac")

    def __init__(self, music_dir: str):
        """
        Initialise the player and load all supported tracks from music_dir.

        Args:
            music_dir (str): Path to the folder containing audio files.
        """
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

        self.music_dir    = music_dir
        self.playlist     = []          # List of full file paths
        self.current_idx  = 0           # Index of the current track
        self.is_playing   = False       # Playback state flag
        self.volume       = 0.7         # Default volume (0.0 – 1.0)

        self._load_playlist()
        pygame.mixer.music.set_volume(self.volume)

    # ── Private helpers ───────────────────────────────────────────────────────

    def _load_playlist(self):
        """Scan music_dir and populate self.playlist with valid audio files."""
        if not os.path.isdir(self.music_dir):
            print(f"[Player] Music directory not found: {self.music_dir}")
            return

        for fname in sorted(os.listdir(self.music_dir)):
            if fname.lower().endswith(self.SUPPORTED_EXTS):
                self.playlist.append(os.path.join(self.music_dir, fname))

        if self.playlist:
            print(f"[Player] Loaded {len(self.playlist)} track(s).")
        else:
            print("[Player] No audio files found. Add .mp3/.wav/.ogg files to the music/ folder.")

    def _load_current_track(self):
        """Load the track at current_idx into pygame.mixer."""
        if not self.playlist:
            return False
        path = self.playlist[self.current_idx]
        try:
            pygame.mixer.music.load(path)
            return True
        except pygame.error as e:
            print(f"[Player] Could not load '{path}': {e}")
            return False

    # ── Public controls ───────────────────────────────────────────────────────

    def play(self):
        """Play (or resume) the current track."""
        if not self.playlist:
            print("[Player] No tracks in playlist.")
            return

        if self.is_playing:
            # Already playing — restart from beginning
            pygame.mixer.music.stop()

        if self._load_current_track():
            pygame.mixer.music.play()
            self.is_playing = True
            print(f"[Player] Playing: {self.get_track_name()}")

    def stop(self):
        """Stop playback."""
        pygame.mixer.music.stop()
        self.is_playing = False
        print("[Player] Stopped.")

    def next_track(self):
        """Advance to the next track and play it."""
        if not self.playlist:
            return
        self.current_idx = (self.current_idx + 1) % len(self.playlist)
        self.play()

    def prev_track(self):
        """Go back to the previous track and play it."""
        if not self.playlist:
            return
        self.current_idx = (self.current_idx - 1) % len(self.playlist)
        self.play()

    def volume_up(self):
        """Increase volume by 10%, capped at 1.0."""
        self.volume = min(1.0, self.volume + 0.1)
        pygame.mixer.music.set_volume(self.volume)

    def volume_down(self):
        """Decrease volume by 10%, floored at 0.0."""
        self.volume = max(0.0, self.volume - 0.1)
        pygame.mixer.music.set_volume(self.volume)

    def update(self):
        """
        Called every frame. Auto-advance to next track when current one ends.
        """
        if self.is_playing and not pygame.mixer.music.get_busy():
            # Track finished naturally — go to next
            self.next_track()

    # ── Status queries ────────────────────────────────────────────────────────

    def get_track_name(self) -> str:
        """Return the filename (without extension) of the current track."""
        if not self.playlist:
            return "No tracks loaded"
        basename = os.path.basename(self.playlist[self.current_idx])
        name, _ = os.path.splitext(basename)
        return name

    def get_position_ms(self) -> int:
        """Return current playback position in milliseconds."""
        if self.is_playing:
            return pygame.mixer.music.get_pos()
        return 0

    def get_status(self) -> str:
        """Return a human-readable status string."""
        return "▶ Playing" if self.is_playing else "■ Stopped"

    def get_playlist_info(self) -> str:
        """Return 'Track X / Y' string."""
        if not self.playlist:
            return "No tracks"
        return f"Track {self.current_idx + 1} / {len(self.playlist)}"

    def get_volume_bar(self, width=20) -> str:
        """Return a simple ASCII volume bar."""
        filled = int(self.volume * width)
        return "[" + "█" * filled + "░" * (width - filled) + "]"
