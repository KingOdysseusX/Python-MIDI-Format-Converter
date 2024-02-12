# main.py

import mido

"""
The issue with using MuseScore 4 midi files in FL Studio 21 is they are
not compatible with FL Studio 21 because FL Studio 21 does not use the first track
for storing or reading note data; whereas, MuseScore 4 does. This converter
will convert the MuseScore 4 midi file into a format that is compatible with FL Studio 21.
To do this, the converter will take the first track of the MuseScore 4 midi file
and move all the notes held within it to the second track of the MuseScore 4 midi file
so that the first track only contains the necessary data matching how FL Studio 21
expects the data to be.
"""

class MuseScore4ToFLStudioConverter:
    def __init__(self, muse_file):
        """
        Initializes the converter.

        args:
            muse_file: Path to the MuseScore4 MIDI file.
        """
        try:
            self.muse_mid = mido.MidiFile(muse_file)
        except IOError:
            print(f"Error: The file {muse_file} does not exist.")
            return

        self.muse_track_names = [track.name for track in self.muse_mid.tracks]

    def _calculate_absolute_times(self, track):
        absolute_times = []
        current_time = 0
        for msg in track:
            current_time += msg.time
            absolute_times.append((current_time, msg))
        return absolute_times

    def _merge_tracks_preserving_timing(self, track1, track2):
        abs_times_track1 = self._calculate_absolute_times(track1)
        abs_times_track2 = self._calculate_absolute_times(track2)

        merged = sorted(abs_times_track1 + abs_times_track2, key=lambda x: x[0])

        new_track = mido.MidiTrack()
        last_time = 0
        for abs_time, msg in merged:
            delta_time = abs_time - last_time
            new_msg = msg.copy(time=delta_time)
            new_track.append(new_msg)
            last_time = abs_time

        return new_track

    def convert_midi_file(self):
        if len(self.muse_mid.tracks) < 2:
            print("The MIDI file must have at least two tracks.")
            return

        # Filter and store meta messages before clearing the first track
        meta_messages = [msg for msg in self.muse_mid.tracks[0] if isinstance(msg, mido.MetaMessage)]

        # Merge the first two tracks preserving their timing
        merged_track = self._merge_tracks_preserving_timing(self.muse_mid.tracks[0], self.muse_mid.tracks[1])

        # Clear the first track and add back the meta messages
        self.muse_mid.tracks[0].clear()
        for msg in meta_messages:
            self.muse_mid.tracks[0].append(msg)

        # Replace the second track with the merged track
        self.muse_mid.tracks[1] = merged_track

    def save_converted_file(self, output_file):
        try:
            self.muse_mid.save(output_file)
        except Exception as e:
            print(f"Failed to save the converted file: {e}")


if __name__ == "__main__":
    muse_file = "Path/To/MuseScore4/File.mid"
    flstudio_file = "Path/To/Desired/FLStudio/File.mid"
    converter = MuseScore4ToFLStudioConverter(muse_file)
    converter.convert_midi_file()
    converter.save_converted_file(flstudio_file)
