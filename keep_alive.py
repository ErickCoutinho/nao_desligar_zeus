"""Mantém o headset sem fio ligado enviando um pulso de tom inaudível periodicamente.

O headset desliga sozinho quando fica um tempo sem receber áudio. Um pulso de
zeros absolutos pode ser tratado como silêncio pelo headset, por isso o script
envia um tom grave de amplitude muito baixa, imperceptível ao ouvido.

O programa roda sem janela, com um ícone na bandeja do sistema para encerrar.
"""

import array
import ctypes
import math
import sys
import threading
from datetime import datetime

import pystray
import sounddevice as sd
from PIL import Image, ImageDraw

APP_NAME = "Não desligar Zeus"
DEVICE_NAME_FRAGMENT = "H510-PRO"
PULSE_INTERVAL_SECONDS = 4 * 60 + 50
PULSE_DURATION_SECONDS = 1.0
TONE_FREQUENCY_HZ = 50.0
# Aproximadamente -40 dBFS. Um tom mais fraco e mais grave (-60 dBFS a 20 Hz)
# é tratado como silêncio pelo headset, que desliga mesmo recebendo os pulsos.
TONE_AMPLITUDE = 0.01
INT16_MAX = 32767
MESSAGE_BOX_ICON_ERROR = 0x10


class DeviceNotFoundError(Exception):
    pass


def show_error(message: str) -> None:
    ctypes.windll.user32.MessageBoxW(None, message, APP_NAME, MESSAGE_BOX_ICON_ERROR)


def find_output_device(name_fragment: str) -> int:
    for index, device in enumerate(sd.query_devices()):
        if name_fragment.lower() in device["name"].lower() and device["max_output_channels"] > 0:
            return index

    raise DeviceNotFoundError(
        f"Nenhum dispositivo de saída contendo '{name_fragment}' foi encontrado. "
        "Verifique se o adaptador USB do headset está conectado."
    )


def build_tone_pulse(sample_rate: float) -> bytes:
    frame_count = int(sample_rate * PULSE_DURATION_SECONDS)
    phase_step = 2 * math.pi * TONE_FREQUENCY_HZ / sample_rate
    peak = int(TONE_AMPLITUDE * INT16_MAX)
    samples = array.array("h", (int(peak * math.sin(frame * phase_step)) for frame in range(frame_count)))
    return samples.tobytes()


def play_pulse(device_index: int, sample_rate: float, pulse: bytes) -> None:
    with sd.RawOutputStream(device=device_index, samplerate=sample_rate, channels=1, dtype="int16") as stream:
        stream.write(pulse)


def build_headphones_image(size: int = 256) -> Image.Image:
    """Desenha um fone de ouvido vermelho em fundo transparente."""
    color = (220, 30, 40, 255)
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    def scaled(*values: float) -> tuple[int, ...]:
        return tuple(round(value * size / 256) for value in values)

    draw.arc(scaled(36, 28, 220, 212), start=180, end=360, fill=color, width=scaled(22)[0])
    draw.rounded_rectangle(scaled(20, 116, 84, 228), radius=scaled(22)[0], fill=color)
    draw.rounded_rectangle(scaled(172, 116, 236, 228), radius=scaled(22)[0], fill=color)
    draw.rectangle(scaled(36, 110, 58, 130), fill=color)
    draw.rectangle(scaled(198, 110, 220, 130), fill=color)
    return image


def run_keep_alive_loop(device_index: int, icon: pystray.Icon, stop_event: threading.Event) -> None:
    sample_rate = sd.query_devices(device_index)["default_samplerate"]
    pulse = build_tone_pulse(sample_rate)

    try:
        while not stop_event.is_set():
            play_pulse(device_index, sample_rate, pulse)
            icon.title = f"{APP_NAME} — último sinal às {datetime.now():%H:%M:%S}"
            stop_event.wait(PULSE_INTERVAL_SECONDS)
    except sd.PortAudioError as error:
        show_error(f"Não foi possível enviar o sinal ao headset. Verifique o adaptador USB.\n\n{error}")
        icon.stop()


def main() -> int:
    try:
        device_index = find_output_device(DEVICE_NAME_FRAGMENT)
    except DeviceNotFoundError as error:
        show_error(str(error))
        return 1

    stop_event = threading.Event()

    def quit_app(icon: pystray.Icon) -> None:
        stop_event.set()
        icon.stop()

    icon = pystray.Icon(
        "nao_desligar_zeus",
        build_headphones_image(64),
        APP_NAME,
        menu=pystray.Menu(pystray.MenuItem("Sair", quit_app)),
    )
    worker = threading.Thread(target=run_keep_alive_loop, args=(device_index, icon, stop_event), daemon=True)
    worker.start()
    icon.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
