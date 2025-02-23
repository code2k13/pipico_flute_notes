import board
import busio as io
import adafruit_ssd1306
import time
import analogio
import digitalio
import ulab
import gc
import math

i2c = io.I2C(board.GP19, board.GP18)
oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)
oled.fill(0)

button = digitalio.DigitalInOut(board.GP21)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.DOWN

frequency_table = [
    {'center_freq': 384, 'symbol': 'Sa'},   # 500 Hz -> 'A'
    {'center_freq': 433, 'symbol': 'Re'},  # 1000 Hz -> 'B'
    {'center_freq': 482, 'symbol': 'Ga'},  # 1500 Hz -> 'C'
    {'center_freq': 531, 'symbol': 'Ma'},  # 2000 Hz -> 'D'
    {'center_freq': 580, 'symbol': 'Pa'},  # 2000 Hz -> 'D'
    {'center_freq': 650, 'symbol': 'Dha'},  # 2000 Hz -> 'D'
    {'center_freq': 713, 'symbol': 'Ni'},  # 2000 Hz -> 'D'
    {'center_freq': 769, 'symbol': 'SA'},  # 2000 Hz -> 'D'
]



mic = analogio.AnalogIn(board.A1)



def get_condensed_fft():
    n_samples = 1024
    samples = []
    #start_time = time.monotonic()
    for i in range(n_samples * 14):
        if i % 14 == 0:
            samples.append(10 * ((mic.value * 3.3 / 65536) - 1.65))
    # end_time = time.monotonic() 
    # elapsed_time = end_time - start_time
    # sampling_frequency = n_samples / elapsed_time
    # print(sampling_frequency)
    data_array = ulab.numpy.array(samples, dtype=ulab.numpy.float)
    fft_result = ulab.numpy.fft.fft(data_array)
    # Use dot product to calculate the magnitude of the complex numbers
    real_part = fft_result[0]
    imag_part = fft_result[1]
    
    # Calculate the magnitudes using the dot product (squared real + squared imag)
    magnitude = real_part* real_part + imag_part * imag_part
    print("magnitude",magnitude)
    # Set the first element (DC component) to zero
    magnitude[0] = 0.0
    gc.collect()
    half_fft = magnitude[:len(magnitude) // 2]
    return half_fft.tolist()

def get_highest_frequency(fft_data, sampling_rate=7182):
    bin_size = sampling_rate / len(fft_data) / 2
    max_amplitude_index = fft_data.index(max(fft_data))
    highest_frequency = max_amplitude_index * bin_size
    return highest_frequency


def find_symbol_for_frequency(highest_frequency, tolerance=0.05):
    for entry in frequency_table:
        center_freq = entry['center_freq']
        symbol = entry['symbol']
        # Calculate the frequency range based on tolerance
        lower_bound = center_freq * (1 - tolerance)
        upper_bound = center_freq * (1 + tolerance)
        # If the highest frequency is within the tolerance range, return the symbol
        if lower_bound <= highest_frequency <= upper_bound:
            return symbol
    return "??"  # If no matching frequency is found

while True:
    if button.value:
        oled.fill(0)
        oled.text("Starting...", 5, 10, 1)
        oled.show()
        time.sleep(1)

        for _ in range(500):
            fft_data = get_condensed_fft()
            highest_frequency = get_highest_frequency(fft_data)
            symbol = find_symbol_for_frequency(highest_frequency)
            oled.fill(0)
            oled.text(f"Note: {symbol} ", 5, 20, 4)
            oled.text(f"Freq: {highest_frequency} Hz ", 5, 40, 1)
            oled.show()
            gc.collect()

        oled.fill(0)
        oled.text("Done", 5, 20, 1)
        oled.show()
        time.sleep(2)
        oled.fill(0)
        oled.show()
    time.sleep(0.1)
