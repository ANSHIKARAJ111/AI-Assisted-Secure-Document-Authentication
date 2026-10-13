
import numpy as np
import cv2

from PIL import Image
from sklearn.ensemble import IsolationForest


def extract_patch_features(gray, patch_size=32):
    """
    Extract statistical, edge, noise and texture features
    from non-overlapping image patches.
    """
    features = []
    positions = []

    height, width = gray.shape

    for y in range(0, height - patch_size + 1, patch_size):
        for x in range(0, width - patch_size + 1, patch_size):

            patch = gray[
                y:y + patch_size,
                x:x + patch_size
            ]

            patch_float = patch.astype(np.float32)

            mean = float(np.mean(patch_float))
            std = float(np.std(patch_float))

            edges = cv2.Canny(patch, 80, 160)
            edge_density = float(np.mean(edges > 0))

            laplacian = cv2.Laplacian(
                patch,
                cv2.CV_32F
            )
            sharpness = float(np.var(laplacian))

            blurred = cv2.GaussianBlur(
                patch, (3, 3), 0
            )

            noise = float(np.std(
                patch_float - blurred.astype(np.float32)
            ))

            features.append([
                mean,
                std,
                edge_density,
                np.log1p(sharpness),
                noise
            ])

            positions.append((x, y))

    return np.asarray(features), positions


def detect_tampering(reference_image, test_image,
                     patch_size=32):
    """
    Train an Isolation Forest using patches from a
    trusted reference image and identify anomalous
    patches in a test image.

    This is an experimental anomaly detector,
    not a definitive forgery classifier.
    """

    reference = reference_image.convert("RGB")
    test = test_image.convert("RGB")

    if test.size != reference.size:
        raise ValueError(
            "Reference and test images must have "
            "the same dimensions."
        )

    reference_gray = cv2.cvtColor(
        np.array(reference),
        cv2.COLOR_RGB2GRAY
    )

    test_gray = cv2.cvtColor(
        np.array(test),
        cv2.COLOR_RGB2GRAY
    )

    reference_features, _ = extract_patch_features(
        reference_gray, patch_size
    )

    test_features, positions = extract_patch_features(
        test_gray, patch_size
    )

    if len(reference_features) < 16:
        raise ValueError(
            "Image is too small for this patch size. "
            "Use a larger image or smaller patch size."
        )

    # Train on patches from a trusted reference.
    model = IsolationForest(
        n_estimators=100,
        contamination=0.05,
        random_state=42,
        n_jobs=1
    )

    model.fit(reference_features)

    # Negative scores indicate more unusual patches.
    scores = model.decision_function(test_features)
    predictions = model.predict(test_features)

    # Compare corresponding patches as additional evidence.
    differences = np.mean(
        np.abs(
            test_features - reference_features
        ),
        axis=1
    )

    # Pixel-level difference against reference.
    pixel_difference = cv2.absdiff(
        reference_gray, test_gray
    )

    changed_mask = (
        pixel_difference > 15
    ).astype(np.uint8)

    heatmap = np.zeros(
        test_gray.shape,
        dtype=np.uint8
    )

    suspicious_patches = 0

    for index, (x, y) in enumerate(positions):

        # Flag an anomalous patch if its content
        # differs meaningfully from its reference.
        local_change = changed_mask[
            y:y + patch_size,
            x:x + patch_size
        ].mean()

        is_suspicious = (
            predictions[index] == -1
            and local_change > 0.02
        )

        if is_suspicious:
            suspicious_patches += 1
            heatmap[
                y:y + patch_size,
                x:x + patch_size
            ] = 255

    # Also report exact image differences separately.
    changed_pixel_percentage = float(
        np.mean(changed_mask) * 100
    )

    suspicious_percentage = (
        suspicious_patches / len(positions)
    ) * 100

    # Visualize flagged regions.
    colored_heatmap = cv2.applyColorMap(
        heatmap,
        cv2.COLORMAP_JET
    )

    colored_heatmap[heatmap == 0] = 0

    original_rgb = np.array(test)

    overlay = cv2.addWeighted(
        original_rgb,
        0.75,
        cv2.cvtColor(
            colored_heatmap,
            cv2.COLOR_BGR2RGB
        ),
        0.25,
        0
    )

    return {
        "suspicious_patches": suspicious_patches,
        "total_patches": len(positions),
        "suspicious_percentage": suspicious_percentage,
        "changed_pixel_percentage": changed_pixel_percentage,
        "mean_anomaly_score": float(np.mean(scores)),
        "overlay": Image.fromarray(overlay),
        "heatmap": Image.fromarray(heatmap),
        "status": (
            "Suspicious visual anomalies detected"
            if suspicious_patches > 0
            else "No suspicious patches flagged"
        )
    }
