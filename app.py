import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import numpy as np

# set page layout to wide
st. set_page_config(layout="wide")

# upload css file
with open("style.css") as source_des:
    st.markdown(f"<style>{source_des.read()}</style>", unsafe_allow_html=True)
    
# draw_signal 
# arguments: data: dataframe 
def draw_signal(data, freq=0, sampling_freq=0):
    # data = pd.read_csv(file)
    fig = plt.figure(figsize=(1, 6))
    plt.subplot(2, 1, 1)
    time = data.iloc[:, 0]
    amplitude = data.iloc[:, 1]
    plt.plot(time, amplitude, '-', label="original")
    plt.title('Signal')
    plt.grid(True)
    ##########################################################################
    # sampling
    try:
        max_time = data.iloc[:, 0].max()
        freq_sampling = sampling_freq
        no_points = data.shape[0]
        no_sample_points = sampling_freq*max_time
        step = no_points/no_sample_points
        sampling_time = []
        sampling_amplitude = []
        if (freq_sampling == 1):
            for i in range(int(step/3), int(no_points), int(step)):
                sampling_time.append(data.iloc[i, 0])
                sampling_amplitude.append(data.iloc[i, 1])
        elif (freq_sampling == 2):
            for i in range(int(step/2), int(no_points), int(step)):
                sampling_time.append(data.iloc[i, 0])
                sampling_amplitude.append(data.iloc[i, 1])
        else:
            for i in range(0, int(no_points), int(step)):
                sampling_time.append(data.iloc[i, 0])
                sampling_amplitude.append(data.iloc[i, 1])
        sampling_points = pd.DataFrame(
            {"time": sampling_time, "amplitude": sampling_amplitude})
        plt.plot(
            sampling_points.iloc[:, 0], sampling_points.iloc[:, 1], "o", color="black", label="sampling points")
        plt.xlabel("time(s)")
        plt.ylabel("amplitude(mv)")
        plt.subplot(2, 1, 2)
        plt.title("reconstructed signal")
        ynew = reconstruction(data, sampling_points)
        plt.plot(time, ynew, "r", label="reconstructed")
        plt.grid(True)
    except:
        sampling_points = pd.DataFrame(
            {"time": [0, 0], "amplitude": [0, 0]})
    plt.xlabel("time(s)")
    plt.ylabel("amplitude(mv)")
    plt.subplots_adjust(hspace=0.4)
    st.plotly_chart(fig, use_container_width=True)
    return sampling_points


def reconstruction(signal, sample):
    time = signal.iloc[:, 0]
    sampled_amplitude = sample.iloc[:, 1]
    sampled_time = sample.iloc[:, 0]
    T = (sampled_time[1] - sampled_time[0])
    sincM = np.tile(time, (len(sampled_time), 1)) - \
        np.tile(sampled_time[:, np.newaxis], (1, len(time)))
    yNew = np.dot(sampled_amplitude, np.sinc(sincM/T))
    return yNew


def save_file(name):
    if "signal_file" in st.session_state:
        time = st.session_state.signal_file.iloc[:, 0]
        amplitude_file = st.session_state.signal_file.iloc[:, 1]
    else:
        time = np.linspace(0, 10, 10000)
        amplitude_file = np.zeros(len(time))
    mixed_signal = 0
    for sig in st.session_state.signals:
        if sig[3] == "sin":
            mixed_signal += sig[1] * np.sin(2*np.pi*sig[2]*time)
        else:
            mixed_signal += sig[1] * np.cos(2*np.pi*sig[2]*time)
    mixed_signal = mixed_signal + amplitude_file
    final_signal = pd.DataFrame({"time": time, "amplitude": mixed_signal})
    final_signal.to_csv("%s.csv" % name, index=False)


def max_sampling(freq):
    if freq != 0:
        return 5*freq
    else:
        return 1


def noise(data, snr_db):
    signal = data.iloc[:, 1]
    power = (signal)**2
    signal_power_db = 10 * np.log10(power)
    signal_avg_power = np.mean(power)
    signal_avg_power_db = 10 * np.log10(signal_avg_power)
    noise_db = signal_avg_power_db - snr_db
    noise_watts = 10**(noise_db/10)
    signal_noise = np.random.normal(0, np.sqrt(noise_watts), len(signal))
    noised_signal = signal + signal_noise
    noised = pd.DataFrame(
        {"time": data.iloc[:, 0], "amplitude": noised_signal})
    return noised


def convert_to_dataframe():
    if "signal_file" in st.session_state:
        time = st.session_state.signal_file.iloc[:, 0]
        amplitude_file = st.session_state.signal_file.iloc[:, 1]
    else:
        time = np.linspace(0, 10, 10000)
        amplitude_file = np.zeros(len(time))
    mixed_signal = 0
    for sig in st.session_state.signals:
        if sig[3] == "sin":
            mixed_signal += sig[1] * np.sin(2*np.pi*sig[2]*time)
        else:
            mixed_signal += sig[1] * np.cos(2*np.pi*sig[2]*time)
    mixed_signal_with_file = mixed_signal + amplitude_file
    data_frame = pd.DataFrame(
        {"time": time, "amplitude": mixed_signal_with_file})
    return data_frame


def head():
    st.markdown("""
        <h1 style='text-align: center; margin-bottom: -35px; margin-top:-114px'>
        Sampling Studio
        </h1>
    """, unsafe_allow_html=True
                )

    st.caption("""
        <p style='text-align: center; margin-top:20px ; position: relative; margin-top:-58px;'>
        by team 25
        </p>
    """, unsafe_allow_html=True
               )


def body():
    if "signals" not in st.session_state:
        st.session_state.signals = []
        st.session_state.signals.append(["default",1,1,"sin"])
    if "signal_name" not in st.session_state:
        st.session_state.signal_name = []
        st.session_state.signal_name.append("default")
    file = st.file_uploader("Upload file", type="csv")
    with st.sidebar:
        form = st.form("signal_form")
        with form:
            col4, col3 = st.columns(2)
            with col3:
                name = st.text_input("Signal Name",value="untitled")
            with col4:
                phase = st.selectbox("type signal", ["sin", "cos"], key=1)
            col1, col2 ,col3 = st.columns(3)
            with col1:
                freq = st.slider("Frequency", min_value=0, max_value=20 ,value =1)
            with col2:
                amplitude = st.slider(
                    "Amplitude", min_value=-0, max_value=20 , value = 1 , step = 1)
            with col3:
                plot_add = st.form_submit_button("Add")

    if (not file) and (len(st.session_state.signals) == 0):
        data = pd.DataFrame({"x": [0, 0, 0], "y": [0, 0, 0]})
        draw_signal(data, freq=0, sampling_freq=0)
        
    if plot_add:
            if name in st.session_state.signal_name:
                with st.sidebar:
                    st.error("this name is already used")
            elif name == "":  
                with st.sidebar:     
                    st.error("invalid name")
            else:
                st.session_state.signals.append([name, amplitude, freq, phase])
                st.session_state.signal_name.append(name)
                st.experimental_rerun()
            
    if file or len(st.session_state.signals) > 0 :
        if file:
            if "siganl_file" not in st.session_state:
                data = pd.read_csv(file)
                st.session_state.signal_file = data

        with st.sidebar:
            delete_form = st.form("delete_form")
            with delete_form:
                col13,col14=st.columns(2)
                with col13:
                    to_be_deleted = st.selectbox("Select Signal", st.session_state.signal_name)
                    
                with col14:
                    delete = st.form_submit_button("Delete Signal")
                
        if delete:
            index = 0
            for sig in st.session_state.signal_name:
                if sig == to_be_deleted:
                    st.session_state.signals.pop(index)
                    st.session_state.signal_name.pop(index)
                    break
                index += 1
            st.experimental_rerun()
        data_compose = convert_to_dataframe()
        with st.sidebar:
            col9, col10 = st.columns(2)
            with col9:
                max_freq_compose = st.number_input(
                    "Max Frequency", step=1, min_value=0, value=2)
            with col10:
                sampling_slider_compose = st.slider(
                    "sampling frequency", min_value=0, max_value=int(max_sampling(max_freq_compose)), value=2*max_freq_compose, step=1)
            col11 , col12 = st.columns(2)
            with col11:
                add_noise_compose = st.checkbox("Add Noise")
        if not add_noise_compose:
            sampling_points_compose = draw_signal(
                data_compose, max_freq_compose, sampling_slider_compose)
            if sampling_slider_compose > 0:
                reconstruction(data_compose, sampling_points_compose)
        if add_noise_compose:
            with st.sidebar:
                with col12:
                    noise_slider = st.slider(
                        "Noise SNR", min_value=0, max_value=100, value=25, step=1)
            noised_data_compose = noise(data_compose, noise_slider)
            sampling_points_compose = draw_signal(
                noised_data_compose, max_freq_compose, sampling_slider_compose)
            if sampling_slider_compose > 0:
                reconstruction(noised_data_compose,
                               sampling_points_compose)
        with st.sidebar:
            save_form = st.form("save_form")
            with save_form:
                col6, col7 = st.columns(2)
                with col6:
                    name = st.text_input("File Name")
                with col7:
                    save = st.form_submit_button("Save")
            if save:
                save_file(name)

if __name__ == "__main__":
    head()
    body()
