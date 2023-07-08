import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import ConnectionPatch
import librosa

def display_spectrograms(source, target, sr):
    source_spect = librosa.feature.melspectrogram(y=source, sr=sr)
    target_spect = librosa.feature.melspectrogram(y=target, sr=sr)

    fig, ax = plt.subplots(nrows=2, sharex=True, sharey=True)

    source_spect_dB = librosa.power_to_db(source_spect, ref=np.max)
    source_img = librosa.display.specshow(source_spect_dB, x_axis='time',
                            y_axis='mel', sr=sr,
                            fmax=8000, ax=ax[0])
    fig.colorbar(source_img, ax=ax[0], format='%+2.0f dB')
    ax[0].set(title='source')

    target_spect_dB = librosa.power_to_db(target_spect, ref=np.max)
    target_img = librosa.display.specshow(target_spect_dB, x_axis='time',
                            y_axis='mel', sr=sr,
                            fmax=8000, ax=ax[1])
    fig.colorbar(target_img, ax=ax[1], format='%+2.0f dB')
    ax[1].set(title='target')

    plt.show()


def display_waveforms(source, target, sr):
    fig, ax = plt.subplots(nrows=2, sharex=True, sharey=True)
    librosa.display.waveshow(source, sr=sr, ax=ax[0])
    ax[0].set(title='Source')
    ax[0].label_outer()

    librosa.display.waveshow(target, sr=sr, ax=ax[1])
    ax[1].set(title='Target')

    plt.show()


def align_dtw(source, target, sr):
    hop_length = 1024

    source_chroma = librosa.feature.chroma_cqt(y=source, sr=sr, hop_length=hop_length)
    target_chroma = librosa.feature.chroma_cqt(y=target, sr=sr, hop_length=hop_length)

    D, wp = librosa.sequence.dtw(X=source_chroma, Y=target_chroma, metric='cosine')
    wp_s = librosa.frames_to_time(wp, sr=sr, hop_length=hop_length)

    fig, (ax1, ax2) = plt.subplots(nrows=2, sharex=True, sharey=True, figsize=(8,4))

    # Plot x_2
    librosa.display.waveshow(target, sr=sr, ax=ax2)
    ax2.set(title='Target')

    # Plot x_1
    librosa.display.waveshow(source, sr=sr, ax=ax1)
    ax1.set(title='Sample')
    ax1.label_outer()


    n_arrows = 20
    for tp1, tp2 in wp_s[::len(wp_s)//n_arrows]:
        # Create a connection patch between the aligned time points
        # in each subplot
        con = ConnectionPatch(xyA=(tp1, 0), xyB=(tp2, 0),
                            axesA=ax1, axesB=ax2,
                            coordsA='data', coordsB='data',
                            color='r', linestyle='--',
                            alpha=0.5)
        con.set_in_layout(False)  # This is needed to preserve layout
        ax2.add_artist(con)
    
    plt.show()


source, sr = librosa.load("test_data/source_0001.mp3")
target, sr = librosa.load("test_data/target_0001-0.mp3")

#display_spectrograms(source, target, sr)
#display_waveforms(source, target, sr)
align_dtw(source, target, sr)

