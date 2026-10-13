
import numpy as np
from PIL import Image


def embed_message(image, secret_message):
    """
    Hide a UTF-8 message inside an RGB image
    using Least Significant Bit steganography.
    """
    image = image.convert("RGB")
    image_array = np.array(image, dtype=np.uint8).copy()

    message_bytes = secret_message.encode("utf-8")
    message_length = len(message_bytes)

    # First 32 bits store the message length.
    header = f"{message_length:032b}"

    message_bits = "".join(
        f"{byte:08b}" for byte in message_bytes
    )

    binary_data = header + message_bits

    flat_pixels = image_array.reshape(-1)

    if len(binary_data) > len(flat_pixels):
        raise ValueError(
            "Message is too large for this image."
        )

    for i, bit in enumerate(binary_data):
        flat_pixels[i] = (
            int(flat_pixels[i]) & 254
        ) | int(bit)

    stego_array = flat_pixels.reshape(image_array.shape)

    return Image.fromarray(stego_array, mode="RGB")


def extract_message(image):
    """
    Extract a hidden UTF-8 message from
    an LSB-encoded RGB image.
    """
    image = image.convert("RGB")
    image_array = np.array(image, dtype=np.uint8)

    flat_pixels = image_array.reshape(-1)

    if len(flat_pixels) < 32:
        raise ValueError("Image is too small.")

    length_bits = "".join(
        str(int(pixel) & 1)
        for pixel in flat_pixels[:32]
    )

    message_length = int(length_bits, 2)

    total_bits = 32 + message_length * 8

    if total_bits > len(flat_pixels):
        raise ValueError(
            "No valid hidden message found."
        )

    message_bits = "".join(
        str(int(pixel) & 1)
        for pixel in flat_pixels[32:total_bits]
    )

    message_bytes = bytes(
        int(message_bits[i:i + 8], 2)
        for i in range(0, len(message_bits), 8)
    )

    return message_bytes.decode("utf-8")
