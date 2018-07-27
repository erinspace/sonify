import io
from time import sleep

import pygame
from pretty_midi import note_name_to_number
from midiutil.MidiFile import MIDIFile

from .constants import KEYS, INSTRUMENTS, PERCUSSION


def make_first_number_match_key(y_values, notes_in_key):
    first_note_in_key = notes_in_key[0]
    transpose_value = first_note_in_key - y_values[0]
    new_y = []
    for y in y_values:
        new_y.append(y + transpose_value)

    return new_y


def convert_to_key(data, key, number_of_octaves=4):
    instrument, instrument_type = None, None
    if type(data[0]) != tuple:
        instrument = data.pop(0)
        _, instrument_type = get_instrument(instrument)

    x, y = zip(*data)

    if instrument_type == 'percussion':
        new_y = y
    else:
        # Finding the index of the note closest to all the notes in the options list
        notes_in_key = key_name_to_notes(key, number_of_octaves=number_of_octaves)

        transposed_y = make_first_number_match_key(y, notes_in_key)
        scaled_y = scale_list_to_range(transposed_y, new_min=min(notes_in_key), new_max=max(notes_in_key))

        new_y = []
        for note in scaled_y:
            new_y.append(get_closest_midi_value(note, notes_in_key))

    processed_data = list(zip(x, new_y))

    if instrument:
        processed_data = [instrument] + processed_data

    return processed_data


def key_name_to_notes(key, octave_start=1, number_of_octaves=4):
    """ Convert a key name to notes, using C3=60

    :param key: String matching one of the values in pre-defined KEY dict
    :param octave_start: octave for the first note, as defined by C3=60
    :param number_of_octaves: The number of octaves to include in the list
    :return:
    """
    key = KEYS.get(key)
    if not key:
        raise ValueError('No key by that name found')

    notes = []
    octave = octave_start + 1
    while len(notes) < number_of_octaves * 7:
        for note in key:
            note_with_octave = note + str(octave)
            note_number = note_name_to_number(note_with_octave)
            if note_number % 12 == 0 and len(notes) != 0:
                octave += 1
                note_with_octave = note + str(octave)
                note_number = note_name_to_number(note_with_octave)
            notes.append(note_number)

    return notes


def get_closest_midi_value(value, possible_values):
    return sorted(possible_values, key=lambda i: abs(i - value))[0]


def scale_y_to_midi_range(data, new_min=0, new_max=127):
    """
    midi notes have a range of 0 - 127. Make sure the data is in that range
    data: list of tuples of x, y coordinates for pitch and timing
    min: min data value, defaults to 0
    max: max data value, defaults to 127
    return: data, but y normalized to the range specified by min and max
    """
    if new_min < 0 or new_max > 127:
        raise ValueError('Midi notes must be in a range from 0 - 127')

    x, y = zip(*data)
    new_y = scale_list_to_range(y, new_min, new_max)

    return list(zip(x, new_y))


def scale_list_to_range(list_to_scale, new_min, new_max):
    old_min = min(list_to_scale)
    old_max = max(list_to_scale)
    return [get_scaled_value(value, old_min, old_max, new_min, new_max) for value in list_to_scale]


def get_scaled_value(old_value, old_min, old_max, new_min, new_max):
    return ((old_value - old_min)/(old_max - old_min)) * (new_max - new_min) + new_min


def quantize_x_value(list_to_quantize, steps=0.5):
    # Restrict the x range to something that's a  multiple of the number of steps given!
    quantized_x = []
    for x in list_to_quantize:
        quantized_x.append(round(steps * round(float(x) / steps), 2))
    return quantized_x


def get_instrument(instrument_name):
    instrument_type = 'melodic'
    program_number = INSTRUMENTS.get(instrument_name.lower())
    if not program_number:
        program_number = PERCUSSION.get(instrument_name.lower())
        instrument_type = 'percussion'
        if not program_number:
            raise AttributeError('No instrument or percussion could be found by that name')
    return program_number - 1, instrument_type


def write_to_midifile(data, track_type='single'):
    """
    data: list of tuples of x, y coordinates for pitch and timing
          Optional: add a string to the start of the data list to specify instrument!
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
    volume = 90

    for data_list in data:
        midifile.addTrackName(track, time, 'Track {}'.format(track))
        midifile.addTempo(track, time, 120)

        instrument_type = 'melodic'
        if type(data_list[0]) != tuple:
            program, instrument_type = get_instrument(data_list.pop(0))

        if instrument_type == 'percussion':
            volume = 100
            channel = 9

        # Write the notes we want to appear in the file
        for point in data_list:
            time = point[0]
            pitch = int(point[1]) if instrument_type == 'melodic' else program
            midifile.addNote(track, channel, pitch, time, duration, volume)
            midifile.addProgramChange(track, channel, time, program)

        track += 1
        channel = 0

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


def play_midi_from_data(input_data, key=None, number_of_octaves=4, track_type='single'):
    """
    input_data: a list of tuples, or a list of lists of tuples to add as separate tracks
    eg:
    input_data = [(1, 5), (5, 7)] OR
    input_data = [
        [(1, 5), (5, 7)],
        [(4, 7), (2, 10)]
    ]
    key: key to play back the graph -- see constants.py for current choices
    number_of_octaves: number of octaves used to restrict the music playback
     when converting to a key

    optional -- append an instrument name to the start of each data list
                to play back using that program number!
    """
    if key:
        if track_type == 'multiple':
            data = []
            for data_list in input_data:
                data.append(convert_to_key(data_list, key, number_of_octaves))
        else:
            data = convert_to_key(input_data, key, number_of_octaves)
    else:
        data = input_data

    memfile = write_to_midifile(data, track_type)
    play_memfile_as_midi(memfile)
