
from PIL import Image
from src.lsb_steganography import (
    embed_message,
    extract_message
)

# Create a sample document image.
original = Image.new(
    "RGB",
    (500, 500),
    color="white"
)

secret = "Document ID: DOC12345 | Status: Authentic"

# Hide the secret message.
protected = embed_message(original, secret)

# Save protected image as lossless PNG.
protected.save("outputs/protected/test_document.png")

# Extract the hidden message.
extracted = extract_message(protected)

print("Original message:", secret)
print("Extracted message:", extracted)

assert extracted == secret

print("LSB STEGANOGRAPHY TEST PASSED!")
