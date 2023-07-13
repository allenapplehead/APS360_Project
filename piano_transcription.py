from piano_transcription_inference import PianoTranscription, sample_rate, load_audio

# Load audio
(audio, _) = load_audio("test_data/target_0001-0.mp3", sr=sample_rate, mono=True)

# Transcriptor
transcriptor = PianoTranscription(device='cpu', checkpoint_path=None)  # device: 'cuda' | 'cpu'

# Transcribe and write out to MIDI file
transcribed_dict = transcriptor.transcribe(audio, 'cut_liszt.mid')