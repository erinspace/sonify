import io
from time import sleep

import pygame
from midiutil.MidiFile import MIDIFile

NOTES = [
    ['C'], ['C#', 'Db'], ['D'], ['D#', 'Eb'], ['E'], ['F'], ['F#', 'Gb'],
    ['G'], ['G#', 'Ab'], ['A'], ['A#', 'Bb'], ['B']
]

KEYS = {
    'c_major': ['C', 'D', 'E', 'F', 'G', 'A', 'B'],
    'g_major': ['G', 'A', 'B', 'C', 'D', 'E', 'F#'],
    'eb_major': ['Eb', 'F', 'G', 'Ab', 'Bb', 'C', 'D']
}


def convert_to_key(data, key):
    x, y = zip(*data)

    # Finding the index of the note closest to all the notes in the options list
    notes_in_key = key_name_to_notes(key)

    scaled_y = scale_list_to_range(y, new_min=min(notes_in_key), new_max=max(notes_in_key))

    new_y = []
    for note in scaled_y:
        new_y.append(get_closest_midi_value(note, notes_in_key))

    return list(zip(x, new_y))


def key_name_to_notes(key, octave_start=2, octave_end=4):
    key = KEYS.get(key)

    if not key:
        raise ValueError('No key by that name found')

    notes = []
    for octave in range(octave_start, octave_end+1):
        for note in key:
            notes.append(note_to_midi(note, octave))

    return notes



def get_closest_midi_value(value, possible_values):
    return sorted(possible_values, key=lambda i: abs(i - value))[0]


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
    max: max data value, defaults to 127
    return: data, but y normalized to the range specified by min and max
    """
    if min < 0 or max > 120:
        raise ValueError('Midi notes must be in a range from 0 - 120')

    new_min = min or 0
    new_max = max or 127

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
    return ((old_value - old_min)/(old_max - old_min)) * (new_max - new_min) + new_min


def write_to_midifile(data, track_type='single'):
    """
    data: list of tuples of x, y coordinates for pitch and timing
    type: the type of data passed to create tracks. Either 'single' or 'multiple'
    """
    if track_type not in ['single', 'multiple']:
        raise ValueError('Track type must be single or multiple')
    
    if track_type == 'single':
        data = [data]

    memfile = io.BytesIO()
    midifile = MIDIFile(numTracks=len(data), adjust_origin=False)

    track = 0
    time = 0
    program = 0
    channel = 0
    duration = 1
    volume = 100

    for data_list in data:
        midifile.addTrackName(track, time, 'Track {}'.format(track))
        midifile.addTempo(track, time, 120)

        # Write the notes we want to appear in the file
        for point in data_list:
            time = point[0]
            pitch = int(point[1])
            midifile.addNote(track, channel, pitch, time, duration, volume)
            midifile.addProgramChange(track, channel, time, program)

        track += 1
        channel += 1
        program += 15

    midifile.writeFile(memfile)
    
    return memfile


def play_memfile_as_midi(memfile):
    # https://stackoverflow.com/questions/27279864/generate-midi-file-and-play-it-without-saving-it-to-disk
    pygame.init()
    pygame.mixer.init()
    memfile.seek(0)
    pygame.mixer.music.load(memfile)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        sleep(1)
    print('Done playing!')


def play_midi_from_data(input_data, key=None, track_type='single'):
    """
    data: a list of tuples, or a list of lists of tuples to add as seperate tracks
    eg: 
    data = [(1, 5), (5, 7)] OR
    data = [
        [(1, 5), (5, 7)],
        [(4, 7), (2, 10)]
    ]
    """
    if key:
        if track_type == 'multiple':
            data = []
            for data_list in input_data:
                data.append(convert_to_key(data_list, key))
        else:
            data = convert_to_key(input_data, key)
    else:
        data = input_data

    memFile = write_to_midifile(data, track_type)
    play_memfile_as_midi(memFile)
