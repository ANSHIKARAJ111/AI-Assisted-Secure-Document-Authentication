
import numpy as np
import pywt
from PIL import Image


def embed_watermark(image, strength=5.0):
    """
    Embed a binary checkerboard watermark
    using Haar Discrete Wavelet Transform.
    """
    image = image.convert("RGB")
    pixels = np.asarray(image, dtype=np.float64).copy()

    channel = pixels[:, :, 2]

    LL, (LH, HL, HH) = pywt.dwt2(channel, "haar")

    rows, cols = LH.shape
    y, x = np.indices((rows, cols))

    watermark = ((x + y) % 2).astype(np.uint8)

    # Convert to signed floating-point values BEFORE subtraction.
    signed_watermark = (
        2.0 * watermark.astype(np.float64) - 1.0
    )

    modified_LH = LH + strength * signed_watermark

    reconstructed = pywt.idwt2(
        (LL, (modified_LH, HL, HH)),
        "haar"
    )

    reconstructed = reconstructed[
        :channel.shape[0],
        :channel.shape[1]
    ]

    pixels[:, :, 2] = np.clip(
        np.rint(reconstructed), 0, 255
    )

    result = Image.fromarray(
        pixels.astype(np.uint8)
    )

    return result, watermark


def calculate_psnr(original, watermarked):
    """
    Calculate Peak Signal-to-Noise Ratio.
    """
    a = np.asarray(original.convert("RGB"), dtype=np.float64)
    b = np.asarray(watermarked.convert("RGB"), dtype=np.float64)

    if a.shape != b.shape:
        raise ValueError("Image dimensions do not match.")

    mse = np.mean((a - b) ** 2)

    if mse == 0:
        return float("inf")

    return 10 * np.log10((255.0 ** 2) / mse)
