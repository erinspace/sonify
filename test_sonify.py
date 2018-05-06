from . import sonify


def test_key_name_to_notes():
    key_name = 'c_major'
    desired_return_value = [36, 38, 40, 41, 43, 45, 47]
    output = sonify.key_name_to_notes(key_name, octave_start=1, number_of_octaves=1)
    assert set(desired_return_value) == set(output)

    key_name = 'g_major'
    desired_return_value = [43, 45, 47, 48, 50, 52, 54]
    output = sonify.key_name_to_notes(key_name, octave_start=1, number_of_octaves=1)
    assert set(desired_return_value) == set(output)


def test_convert_notes_to_a_key():
    x = [1, 2]
    y = [1, 2]

    data = list(zip(x, y))

    converted_c_data = sonify.convert_to_key(data, 'c_major')
    x, y_in_c = zip(*converted_c_data)
    assert y_in_c[0] == 36
    assert y_in_c[1] == 59

    converted_g_data = sonify.convert_to_key(data, 'g_major')
    x, y_in_g = zip(*converted_g_data)
    assert y_in_g[0] == 43
    assert y_in_g[1] == 66
