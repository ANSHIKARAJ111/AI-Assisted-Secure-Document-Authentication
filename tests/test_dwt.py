
from PIL import Image
from src.dwt_watermark import (
    embed_watermark,
    calculate_psnr
)

original = Image.new(
    "RGB",
    (512, 512),
    color="white"
)

watermarked, reference = embed_watermark(
    original,
    strength=5.0
)

watermarked.save(
    "outputs/protected/dwt_test.png"
)

psnr = calculate_psnr(original, watermarked)

print("Watermark dimensions:", reference.shape)
print("PSNR:", round(psnr, 2), "dB")

assert watermarked.size == original.size
assert psnr > 30

print("DWT WATERMARKING TEST PASSED!")
