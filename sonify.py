import io
from time import sleep

import pygame
from midiutil.MidiFile import MIDIFile

NOTES = [
    ['C'], ['C#', 'Db'], ['D'], ['D#', 'Eb'], ['E'], ['F'], ['F#', 'Gb'],
    ['G'], ['G#', 'Ab'], ['A'], ['A#', 'Bb'], ['B']
]

C_MAJOR = ['C', 'D', 'E', 'F', 'G', 'A', 'B']


def note_to_midi(note_name, octave=3):
    midi_base = 0
    for note_list in NOTES:
        if note_name.upper() in note_list:
            break
        midi_base += 1

    return midi_base + octave*12

def scale_y_to_midi_range(data, new_min=None, new_max=None):
    """
    midi notes have a range of 0 - 120. Make sure the data is in that range
    data: list of tuples of x, y coordinates for pitch and timing
    min: min data value, defaults to 0
    max: max data value, defaults to 120
    return: data, but y normalized to the range specified by min and max
    """
    if min < 0 or max > 120:
        raise ValueError('Midi notes must be in a range from 0 - 120')

    new_min = min or 0
    new_max = max or 120

    x, y = zip(*data)

    old_min = min(y)
    old_max = max(y)

    new_y = scale_list_to_range(y, new_min, new_max)

    return list(zip(x, new_y))

def scale_list_to_range(list_to_scale, new_min=None, new_max=None):
    old_min = min(list_to_scale)
    old_max = max(list_to_scale)
    return [get_scaled_value(value, old_min, old_max, new_min, new_max) for value in list_to_scale]


def get_scaled_value(old_value, old_min, old_max, new_min, new_max):
    return ((old_value - old_min)/(old_max - old_min)) * ((new_max - new_min) + new_min)


def write_to_midifile(data, key=None):
    """
    data: list of tuples of x, y coordinates for pitch and timing
    key: type of scale to make sure the notes adhere to (coming soon!)
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
        midifile.addNote(track, channel, pitch, time, duration, volume)
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


def play_midi_from_data(input_data, key=None):        
    memFile = write_to_midifile(input_data, key)
    play_memfile_as_midi(memFile)
