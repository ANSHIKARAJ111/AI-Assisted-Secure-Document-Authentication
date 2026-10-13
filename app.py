
import streamlit as st
from PIL import Image
from io import BytesIO
from pathlib import Path
import uuid
import json
import hashlib

from src.dwt_watermark import (
    embed_watermark,
    calculate_psnr
)

from src.lsb_steganography import (
    embed_message,
    extract_message
)

from src.authentication import (
    sign_document,
    verify_document
)

from src.ai_tampering import detect_tampering


# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="AI Secure Document Authentication",
    page_icon="🔐",
    layout="wide"
)


# ==================================================
# LOAD CUSTOM CSS
# ==================================================

css_path = Path(__file__).parent / "assets" / "style.css"

if css_path.exists():
    with open(css_path, "r", encoding="utf-8") as css_file:
        st.markdown(
            f"<style>{css_file.read()}</style>",
            unsafe_allow_html=True
        )


# ==================================================
# APPLICATION HEADER
# ==================================================

st.title("AI-Assisted Secure Document Authentication")

st.subheader(
    "Using Digital Watermarking and Steganography"
)

st.markdown(
    "Protect and verify digital documents using "
    "**DWT watermarking, LSB steganography, "
    "SHA-256 hashing, Ed25519 digital signatures "
    "and AI-assisted tampering detection.**"
)


# ==================================================
# SESSION STATE
# ==================================================

if "document_id" not in st.session_state:
    st.session_state["document_id"] = str(uuid.uuid4())[:8]


# ==================================================
# APPLICATION TABS
# ==================================================

tab1, tab2, tab3 = st.tabs([
    "🔐 Protect Document",
    "🔎 Verify Document",
    "🧠 AI Tampering Detection"
])


# ==================================================
# TAB 1 - DOCUMENT PROTECTION
# ==================================================

with tab1:

    st.header("Document Protection")

    st.write(
        "Upload a certificate or document image to "
        "embed a DWT watermark, hide authentication "
        "metadata and generate a digital signature."
    )

    uploaded_file = st.file_uploader(
        "Upload a document image",
        type=["png", "jpg", "jpeg"],
        key="protect_upload"
    )

    if uploaded_file is not None:

        try:
            original = Image.open(
                BytesIO(uploaded_file.getvalue())
            ).convert("RGB")

            st.image(
                original,
                caption="Original Document",
                width="stretch"
            )

            document_id = st.text_input(
                "Document ID",
                key="document_id"
            )

            if st.button(
                "🔐 Protect Document",
                type="primary"
            ):

                if not document_id.strip():
                    st.error("Please enter a valid Document ID.")

                else:
                    try:
                        with st.spinner(
                            "Applying watermarking, steganography "
                            "and digital authentication..."
                        ):

                            # STEP 1: DWT WATERMARKING

                            watermarked, watermark = embed_watermark(
                                original,
                                strength=5.0
                            )

                            # STEP 2: LSB STEGANOGRAPHY

                            secret_message = (
                                f"DOC_ID:{document_id}"
                            )

                            protected = embed_message(
                                watermarked,
                                secret_message
                            )

                            # STEP 3: IMAGE QUALITY

                            psnr = calculate_psnr(
                                original,
                                protected
                            )

                            # STEP 4: SAVE LOSSLESS PNG

                            buffer = BytesIO()

                            protected.save(
                                buffer,
                                format="PNG"
                            )

                            protected_bytes = buffer.getvalue()

                            # STEP 5: SHA-256 + ED25519

                            signed_record = sign_document(
                                protected_bytes,
                                document_id
                            )

                            # STEP 6: STORE RESULTS

                            st.session_state["protected_bytes"] = (
                                protected_bytes
                            )

                            st.session_state["protected_id"] = (
                                document_id
                            )

                            st.session_state["protected_psnr"] = psnr

                            st.session_state["signed_record"] = (
                                signed_record
                            )

                            st.session_state["protected_source"] = (
                                uploaded_file.getvalue(),
                                document_id
                            )

                    except Exception as error:
                        st.error(
                            f"Document protection failed: {error}"
                        )

            current_source = (
                uploaded_file.getvalue(),
                document_id
            )

            if (
                "protected_bytes" in st.session_state
                and "signed_record" in st.session_state
                and st.session_state.get("protected_source")
                == current_source
            ):

                st.success(
                    "Document protection completed successfully!"
                )

                protected_image = Image.open(
                    BytesIO(
                        st.session_state["protected_bytes"]
                    )
                )

                st.image(
                    protected_image,
                    caption="Protected Document",
                    width="stretch"
                )

                st.subheader("Protection Results")

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric(
                        "Image Quality (PSNR)",
                        f"{st.session_state['protected_psnr']:.2f} dB"
                    )

                with col2:
                    st.metric(
                        "Watermarking",
                        "DWT Applied"
                    )

                with col3:
                    st.metric(
                        "Steganography",
                        "LSB Applied"
                    )

                st.subheader("Authentication Details")

                record = st.session_state["signed_record"]

                st.write(
                    "**Document ID:**",
                    record["document_id"]
                )

                st.write("**Hash Algorithm:** SHA-256")

                st.code(
                    record["sha256"],
                    language=None
                )

                st.write(
                    "**Digital Signature Algorithm:** Ed25519"
                )

                st.info(
                    "The document's SHA-256 fingerprint has "
                    "been digitally signed. Download both "
                    "files for verification."
                )

                col1, col2 = st.columns(2)

                with col1:
                    st.download_button(
                        label="⬇️ Download Protected Document",
                        data=st.session_state["protected_bytes"],
                        file_name="protected_document.png",
                        mime="image/png",
                        use_container_width=True
                    )

                with col2:
                    st.download_button(
                        label="⬇️ Download Authentication Record",
                        data=json.dumps(record, indent=4),
                        file_name="authentication_record.json",
                        mime="application/json",
                        use_container_width=True
                    )

        except Exception as error:
            st.error(
                f"Unable to open uploaded document: {error}"
            )


# ==================================================
# TAB 2 - DOCUMENT VERIFICATION
# ==================================================

with tab2:

    st.header("Document Verification")

    st.write(
        "Upload the protected PNG and its authentication "
        "record to check document integrity and "
        "digital signature validity."
    )

    verify_file = st.file_uploader(
        "Upload Protected Document (PNG)",
        type=["png"],
        key="verify_upload"
    )

    record_file = st.file_uploader(
        "Upload Authentication Record (JSON)",
        type=["json"],
        key="record_upload"
    )

    if verify_file is not None:

        try:
            verify_image = Image.open(
                BytesIO(verify_file.getvalue())
            ).convert("RGB")

            st.image(
                verify_image,
                caption="Document Under Verification",
                width="stretch"
            )

            st.subheader("Hidden Metadata Extraction")

            if st.button("🔍 Extract Hidden Metadata"):

                try:
                    extracted_message = extract_message(
                        verify_image
                    )

                    if extracted_message.startswith("DOC_ID:"):

                        st.success(
                            "Hidden metadata extracted successfully!"
                        )

                        st.code(
                            extracted_message,
                            language=None
                        )

                    else:
                        st.warning(
                            "Unexpected hidden metadata format."
                        )

                    st.info(
                        "Metadata extraction alone does not "
                        "establish document authenticity."
                    )

                except (ValueError, UnicodeDecodeError) as error:
                    st.error(
                        f"Metadata extraction failed: {error}"
                    )

        except Exception as error:
            st.error(
                f"Unable to read document image: {error}"
            )

    # CRYPTOGRAPHIC AUTHENTICATION

    st.subheader("Cryptographic Authentication")

    if verify_file is not None and record_file is not None:

        if st.button(
            "🛡️ Verify Document Authenticity",
            type="primary"
        ):

            try:
                document_bytes = verify_file.getvalue()

                record = json.loads(
                    record_file.getvalue().decode("utf-8")
                )

                valid, message = verify_document(
                    document_bytes,
                    record
                )

                actual_hash = hashlib.sha256(
                    document_bytes
                ).hexdigest()

                if valid:

                    st.success("✅ AUTHENTIC DOCUMENT")
                    st.write(message)

                    st.write(
                        "**Document ID:**",
                        record["document_id"]
                    )

                    st.write("**SHA-256 Hash:**")
                    st.code(actual_hash, language=None)

                    # VERIFY HIDDEN DOCUMENT ID

                    try:
                        hidden_message = extract_message(
                            Image.open(
                                BytesIO(document_bytes)
                            ).convert("RGB")
                        )

                        expected_message = (
                            f"DOC_ID:{record['document_id']}"
                        )

                        if hidden_message == expected_message:

                            st.success(
                                "Hidden Document ID matches "
                                "the signed authentication record."
                            )

                        else:
                            st.error(
                                "Hidden Document ID does not "
                                "match the signed record."
                            )

                    except (ValueError, UnicodeDecodeError):

                        st.warning(
                            "Digital signature is valid, but "
                            "hidden metadata could not be extracted."
                        )

                else:

                    st.error(
                        "❌ DOCUMENT VERIFICATION FAILED"
                    )

                    st.write(message)

                    if actual_hash != record.get("sha256"):

                        st.warning(
                            "The uploaded document differs "
                            "from the signed document."
                        )

            except (
                json.JSONDecodeError,
                UnicodeDecodeError,
                TypeError
            ):
                st.error("Invalid authentication JSON file.")

            except Exception as error:
                st.error(
                    f"Verification failed: {error}"
                )

    else:

        st.info(
            "Upload both the protected PNG and "
            "authentication JSON to enable verification."
        )


# ==================================================
# TAB 3 - AI TAMPERING DETECTION
# ==================================================

with tab3:

    st.header("🧠 AI-Assisted Tampering Detection")

    st.write(
        "Compare a trusted reference document with a "
        "suspected document using Isolation Forest "
        "machine learning and image difference analysis."
    )

    reference_file = st.file_uploader(
        "Upload Trusted Reference Document",
        type=["png", "jpg", "jpeg"],
        key="ai_reference"
    )

    test_file = st.file_uploader(
        "Upload Suspected / Modified Document",
        type=["png", "jpg", "jpeg"],
        key="ai_test"
    )

    if reference_file is not None and test_file is not None:

        try:
            # LOAD REFERENCE IMAGE

            reference_image = Image.open(
                BytesIO(reference_file.getvalue())
            ).convert("RGB")

            # LOAD SUSPECTED IMAGE

            test_image = Image.open(
                BytesIO(test_file.getvalue())
            ).convert("RGB")

            # ==========================================
            # AUTOMATIC IMAGE DIMENSION CORRECTION
            # ==========================================

            reference_size = reference_image.size
            original_test_size = test_image.size

            if test_image.size != reference_image.size:

                test_image = test_image.resize(
                    reference_image.size,
                    Image.Resampling.LANCZOS
                )

                st.info(
                    "Image dimensions automatically adjusted "
                    f"from {original_test_size} "
                    f"to {reference_size}."
                )

                st.warning(
                    "The suspected image was resized for "
                    "comparison. Resizing and layout differences "
                    "can affect changed-pixel and anomaly results. "
                    "For accurate testing, edit a copy of the "
                    "original document without changing its size."
                )

            # ==========================================
            # DISPLAY DOCUMENTS
            # ==========================================

            col1, col2 = st.columns(2)

            with col1:
                st.image(
                    reference_image,
                    caption="Trusted Reference Document",
                    width="stretch"
                )

            with col2:
                st.image(
                    test_image,
                    caption="Suspected / Modified Document",
                    width="stretch"
                )

            st.divider()

            # ==========================================
            # RUN AI DETECTION
            # ==========================================

            if st.button(
                "🧠 Run AI Tampering Detection",
                type="primary"
            ):

                try:
                    with st.spinner(
                        "Extracting image features and "
                        "running Isolation Forest..."
                    ):

                        result = detect_tampering(
                            reference_image,
                            test_image
                        )

                    st.subheader("Detection Results")

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric(
                            "Suspicious Patches",
                            result["suspicious_patches"]
                        )

                    with col2:
                        st.metric(
                            "Suspicious Patch %",
                            f"{result['suspicious_percentage']:.2f}%"
                        )

                    with col3:
                        st.metric(
                            "Changed Pixels",
                            f"{result['changed_pixel_percentage']:.2f}%"
                        )

                    # ==================================
                    # DETECTION STATUS
                    # ==================================

                    if result["suspicious_patches"] > 0:

                        st.warning(
                            "⚠️ Suspicious visual anomalies detected."
                        )

                    else:

                        st.success(
                            "No suspicious patches flagged "
                            "by the anomaly detection model."
                        )

                    if result["changed_pixel_percentage"] > 0:

                        st.info(
                            "Pixel differences were detected "
                            "between the reference and "
                            "suspected documents."
                        )

                    # ==================================
                    # HEATMAP VISUALIZATION
                    # ==================================

                    st.subheader("Tampering Visualization")

                    st.image(
                        result["overlay"],
                        caption="AI Suspicious Region Overlay",
                        width="stretch"
                    )

                    st.image(
                        result["heatmap"],
                        caption="Suspicious Patch Mask",
                        width="stretch"
                    )

                    # ==================================
                    # ANALYSIS SUMMARY
                    # ==================================

                    st.subheader("Analysis Summary")

                    st.write(
                        "**Total Image Patches:**",
                        result["total_patches"]
                    )

                    st.write(
                        "**Suspicious Patches:**",
                        result["suspicious_patches"]
                    )

                    st.write(
                        "**Changed Pixel Percentage:**",
                        f"{result['changed_pixel_percentage']:.2f}%"
                    )

                    st.write(
                        "**Mean Anomaly Score:**",
                        f"{result['mean_anomaly_score']:.4f}"
                    )

                    st.info(
                        "AI-assisted analysis identifies "
                        "possible visual anomalies. "
                        "These results do not independently "
                        "prove document forgery. "
                        "Cryptographic verification is required "
                        "for exact signed-file integrity."
                    )

                except Exception as error:

                    st.error(
                        f"AI Detection Error: {error}"
                    )

        except Exception as error:

            st.error(
                f"Unable to read document images: {error}"
            )

    else:

        st.info(
            "Upload both the trusted reference "
            "and suspected document to begin analysis."
        )


# ==================================================
# FOOTER
# ==================================================

st.divider()

st.caption(
    "AI-Assisted Secure Document Authentication | "
    "DWT • LSB • SHA-256 • Ed25519 • Isolation Forest | "
    "Academic Project"
)
