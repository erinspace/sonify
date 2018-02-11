import io
import random
from time import sleep

import pygame
from midiutil.MidiFile import MIDIFile


def write_to_midifile(data, key=None):
    """
    data: list of tuples of x, y coordinates for pitch and timing
    style: type of scale to make sure the notes adhere to (coming soon!)
    """
    memfile = io.BytesIO()
    midifile = MIDIFile(1, adjust_origin=False)  
    
    track = 0
    time = 0
    channel = 0
    base_pitch = 60
    duration = 1
    volume = 100
    
    # A bit more setup
    midifile.addTrackName(track, time, "Awesome Data Track")
    midifile.addTempo(track, time, 120)

    # Write the notes we want to appear in the file
    for point in data:
        time = point[0]
        pitch = base_pitch + int(point[1])
        midifile.addNote(track,channel,pitch,time,duration,volume)
    midifile.writeFile(memfile)
    
    return memfile


def play_memfile_as_midi(memfile):
    pygame.init()
    pygame.mixer.init()
    memfile.seek(0)  # "rewind" the memFile to play from the beginning
    pygame.mixer.music.load(memfile)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        sleep(1)
    print("Finished!")


def play_midi_from_data(input_data, style=None):        
    memFile = write_to_midifile(input_data, style)
    play_memfile_as_midi(memFile)
