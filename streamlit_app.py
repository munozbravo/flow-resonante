from pydub import AudioSegment
from pydub.silence import split_on_silence
import pandas as pd
import streamlit as st


@st.cache
def df_stats(audio):
    valores = [audio.duration_seconds, audio.dBFS, audio.max_dBFS, audio.frame_rate]
    unidades = ["Segundos", "dBFS", "dBFS", "Hz"]
    medidas = ["Duración", "Volumen", "Máxima amplitud", "Frame Rate"]

    stats = {"Valor": valores, "Unidad": unidades}

    df = pd.DataFrame(stats, index=medidas)
    df["Valor"] = df["Valor"].map("{:.2f}".format)

    return df


st.title(":studio_microphone: Convertidor de Audio")

uploaded = st.file_uploader("Cargue archivo a convertir", type=["mp3"])

if uploaded is not None:

    st.markdown("---")
    st.markdown("## Información del audio cargado")
    st.markdown("### Reproducción & Estadísticas")

    st.audio(uploaded, format=uploaded.type)

    audio = AudioSegment.from_mp3(uploaded)

    if st.checkbox("Ver estadísticas del audio"):
        stats = df_stats(audio)

        st.markdown("### Estadísticas")
        st.dataframe(stats)

    st.markdown("---")
    st.markdown("## Modificación del audio")

    with st.form(key="controles"):
        st.markdown("### Parámetros que puede modificar")

        th_label = "Umbral de silencio (dBFS)"
        th_help = "Menor valor es menor volumen de umbral."
        si_label = "Mínima duración de silencio (segundos)"
        si_help = "Silencios de mayor duración a este valor se eliminan."

        volume = int(audio.dBFS)
        minimo = int(volume - abs(audio.max_dBFS - volume) / 2)

        left, mid, right = st.beta_columns([3, 1, 3])

        with left:
            threshold = st.slider(
                th_label, minimo, volume, value=volume, step=1, help=th_help
            )

        with right:
            silent = st.slider(
                si_label, 1000, 4000, value=1000, step=1000, help=si_help
            )

        submit_btn = st.form_submit_button(label="Modificar audio")

    if submit_btn:
        st.markdown("---")
        st.markdown("## Reproducción & Descarga")

        chunks = split_on_silence(
            audio, min_silence_len=silent, silence_thresh=threshold
        )

        modificado = chunks[0]
        for chunk in chunks[1:]:
            modificado = modificado.append(chunk)

        st.markdown(
            f"Con *Umbral de Silencio* {threshold} y *Duración Mínima de Silencio* {silent} el archivo cargado fue dividido en {len(chunks)} partes antes de unir."
        )

        temp_audio = modificado.export(format="mp3")
        st.audio(temp_audio.read(), format=uploaded.type)
        st.caption(
            "Descargue el audio haciendo click derecho en el extremo derecho del reproductor"
        )
