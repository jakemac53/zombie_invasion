import pygame, glob, random, os, sys
from pygame import mixer

class Music(object):
    """
    This class is an abstraction of pygame.mixer and pygame.mixer.music.
    It dynamically loads all MIDI files in the music folder and queues
    them for playback. It provides a number of simple methods to control
    simple attributes of the music.
    """
    freq = 44100
    bitsize = -16
    channels = 2
    buffer = 1024
    titles = []
    volume = 0.8
    is_theme = False
    MIN_VOLUME = 0.0
    MAX_VOLUME = 1.0
#    music_path = 'test_music'
    music_path = 'music'
    theme_path = os.path.join(music_path, 'theme.mid')
    current_title = 0

    def __init__(self, theme=False):
        """ Initializes the music object. """
        mixer.init(self.freq, self.bitsize, self.channels, self.buffer)
        mixer.music.set_volume(self.volume)

        # Build a list of all midis in the folder
        self.titles = glob.glob(os.path.join(self.music_path, '*.mid'))
        random.shuffle(self.titles)

        try:
            self.titles.remove(self.theme_path)
            self.titles.insert(0, self.theme_path)
        except ValueError:
            pass

        try:
            mixer.music.load(self.titles[0])
            self.current_title = 0
        except pygame.error:
            pass

    def update(self):
        """
        This method gets called once per tick to check if
        the song is over and needs to be changed to the
        next track.
        """
        if not mixer.music.get_busy():
            self.current_title += 1
            if self.current_title >= len(self.titles):
                self.current_title = 0
            mixer.music.load(self.titles[self.current_title])
            self.play()

    def next(self):
        """ Skip to the next track. """
        self.current_title += 1
        if self.current_title >= len(self.titles):
            self.current_title = 0
        mixer.music.load(self.titles[self.current_title])
        self.play()

    def prev(self):
        """ Skip to the previous track. """
        self.current_title -= 1
        if self.current_title < 0:
            self.current_title = len(self.titles) - 1
        mixer.music.load(self.titles[self.current_title])
        self.play()

    def play(self):
        """ Plays the current loaded song. """
        mixer.music.play()

    def pause(self):
        """ Pause the music. """
        mixer.music.pause()

    def unpause(self):
        """ Unpause the music. """
        mixer.music.unpause()

    def stop(self):
        """ Stop the music. """
        mixer.music.stop()

    def mute(self):
        """ Mute the music. """
        mixer.music.set_volume(self.MIN_VOLUME)

    def unmute(self):
        """ Unmute the music. """
        mixer.music.set_volume(self.volume)

    def increase_volume(self, step=0.1):
        """
        Increase the volume. An optional step can be passed which
        determines the interval that the volume increases between
        MIN_VOLUME and MAX_VOLUME.
        """
        if self.volume + step > self.MAX_VOLUME:
            self.volume = self.MAX_VOLUME
        else:
            self.volume += step

    def decrease_volume(self, step=0.1):
        """
        Decrease the volume. An optional step can be passed which
        determines the interval that the volume decreases between
        MIN_VOLUME and MAX_VOLUME.
        """
        if self.volume - step < self.MIN_VOLUME:
            self.volume = self.MIN_VOLUME
        else:
            self.volume -= step