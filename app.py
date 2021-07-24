from pathlib import Path

from pydub import AudioSegment
from pydub.silence import split_on_silence
from scipy.io.wavfile import read
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st


@st.cache
def df_stats(audio):
    valores = [audio.duration_seconds, audio.dBFS,
               audio.max_dBFS, audio.frame_rate]
    unidades = ['Segundos', 'dBFS', 'dBFS', 'Hz']
    medidas = ['Duración', 'Volumen', 'Máxima amplitud', 'Frame Rate']

    stats = {"Valor": valores, "Unidad": unidades}

    df = pd.DataFrame(stats, index=medidas)
    df['Valor'] = df['Valor'].map('{:.2f}'.format)

    return df


def graph_amplitude(fp):
    wav_rate, wav_data = read(fp)
    seconds = len(wav_data) / wav_rate
    x_range = np.arange(0, seconds, 1/wav_rate)

    canal1 = wav_data[:, 0]

    fig, ax = plt.subplots()
    ax.plot(x_range, canal1, linewidth=0.01, alpha=0.7, color='#ff7f00')
    ax.set_xlabel('Segundos')
    ax.set_ylabel('Amplitud')

    return fig


st.title(":studio_microphone: Convertidor de Audio")

uploaded = st.file_uploader("Cargue archivo a convertir", type=["mp3"])

temp = Path("temp")
temp.mkdir(parents=True, exist_ok=True)

if uploaded is not None:

    st.markdown("---")
    st.subheader("Información del audio cargado")
    st.markdown("### Reproducción")

    st.audio(uploaded, format=uploaded.type)

    sound = AudioSegment.from_mp3(uploaded)

    stats = df_stats(sound)

    st.markdown("### Estadísticas")
    st.dataframe(stats)

    if st.checkbox("Ver gráfica de Amplitud"):
        fname = f"{Path(uploaded.name).stem}.wav"
        fp = temp.joinpath(fname)
        sound.export(fp, format='wav')

        fig = graph_amplitude(fp)

        st.pyplot(fig)

    st.markdown("---")

    st.markdown("## Modificación del audio")

    volume = sound.dBFS
    minimo = int(volume - abs(sound.max_dBFS - volume)/2)
    maximo = int(volume-1)

    with st.form(key='controles'):
        st.markdown("### Parámetros que puede modificar")

        th_label = "Seleccione el umbral de silencio"
        th_help = "Menor valor es menor volumen"
        threshold = st.slider(th_label, minimo, maximo,
                              value=maximo, step=1, help=th_help)

        si_label = "Seleccione mínima duración del silencio"
        si_help = "En milisegundos. Silencios de mayor duración a este valor se eliminan."
        silent = st.slider(si_label, 1000, 4000, value=1000,
                           step=1000, help=si_help)

        submit_btn = st.form_submit_button(label='Modificar')

    chunks = split_on_silence(
        sound, min_silence_len=silent, silence_thresh=threshold)

    modificado = chunks[0]
    for chunk in chunks[1:]:
        modificado = modificado.append(chunk)

    fp_new = temp.joinpath("modificado.mp3")
    modificado.export(fp_new)
    st.markdown(
        f"Con *Umbral de Silencio* {threshold} y *Duración Mínima de Silencio* {silent} el archivo cargado fue dividido en {len(chunks)} partes antes de unir.")

    st.markdown("---")
    st.markdown("## Reproducción & Descarga")
    st.audio(str(fp_new), format=uploaded.type)
    st.caption("Descargue el audio haciendo click derecho en el reproductor")
