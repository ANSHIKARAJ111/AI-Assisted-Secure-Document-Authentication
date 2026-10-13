\# AI-Assisted Secure Document Authentication



An AI-assisted document authentication system designed to protect digital documents against unauthorized modifications, detect potential tampering, and support document integrity verification using digital watermarking, steganography, cryptographic authentication, and image analysis.



The project provides a Streamlit-based interface for working with document protection and authentication features.



\## Tech Stack



\- \*\*Language:\*\* Python

\- \*\*Frontend:\*\* Streamlit

\- \*\*Image Processing:\*\* Digital image analysis and processing

\- \*\*Watermarking:\*\* Discrete Wavelet Transform (DWT)

\- \*\*Steganography:\*\* Least Significant Bit (LSB)

\- \*\*Authentication:\*\* Cryptographic verification

\- \*\*AI-Assisted Analysis:\*\* Document tampering detection



\## Key Features



\### 1. AI-Assisted Tampering Detection



\- Analyzes document images for potential modifications.

\- Supports identifying suspicious regions and visual inconsistencies.

\- Provides an additional analysis layer during document verification.



\### 2. DWT-Based Digital Watermarking



\- Uses Discrete Wavelet Transform techniques for watermarking.

\- Supports embedding information within document images.

\- Helps assess document integrity through watermark analysis.



\### 3. LSB Steganography



\- Uses Least Significant Bit techniques to conceal information within images.

\- Supports embedding and extraction of hidden information.

\- Demonstrates information-hiding techniques for document protection.



\### 4. Cryptographic Document Authentication



\- Uses cryptographic authentication techniques.

\- Supports document authenticity and integrity verification.

\- Separates public verification keys from private signing keys.



\### 5. Interactive Streamlit Application



\- Provides a web-based user interface.

\- Integrates document protection and analysis modules.

\- Supports a more accessible authentication workflow.



\## Project Structure



```text

AI\_Secure\_Document\_Authentication/

|

|-- app.py

|-- assets/

|   |-- style.css

|   |-- .streamlit/

|       |-- config.toml

|-- src/

|   |-- \_\_init\_\_.py

|   |-- ai\_tampering.py

|   |-- authentication.py

|   |-- dwt\_watermark.py

|   |-- lsb\_steganography.py

|-- keys/

|   |-- public\_key.pem

|-- outputs/

|   |-- protected/

|-- tests/

|   |-- test\_authentication.py

|   |-- test\_dwt.py

|   |-- test\_lsb.py

|-- requirements.txt

|-- README.md

```



\## Installation and Setup



\*\*1. Clone the repository\*\*



```bash

git clone https://github.com/ANSHIKARAJ111/AI-Assisted-Secure-Document-Authentication.git

```



\*\*2. Navigate to the project directory\*\*



```bash

cd AI-Assisted-Secure-Document-Authentication

```



\*\*3. Create a virtual environment\*\*



```bash

python -m venv .venv

```



\*\*4. Activate the environment on Windows\*\*



```cmd

.venv\\Scripts\\activate

```



\*\*5. Install dependencies\*\*



```bash

pip install -r requirements.txt

```



\*\*6. Run the application\*\*



```bash

streamlit run app.py

```



Open the local URL displayed by Streamlit in your browser.



\## System Workflow



1\. \*\*Document Input:\*\* The user provides a document image.

2\. \*\*Document Protection:\*\* Watermarking and steganography techniques can be applied.

3\. \*\*Authentication:\*\* Cryptographic verification helps assess document authenticity.

4\. \*\*Tampering Analysis:\*\* The AI-assisted module analyzes possible modifications.

5\. \*\*Results:\*\* The application presents verification and analysis information.



\## Testing



The project contains dedicated test modules for authentication, DWT watermarking, and LSB steganography.



Run the tests using:



```bash

python -m pytest tests/

```



\## Security Considerations



\- Never commit private cryptographic keys.

\- Keep sensitive documents and authentication secrets outside the public repository.

\- Use test documents for public demonstrations.

\- Treat AI tampering analysis as supporting evidence rather than definitive proof of forgery.



\## Applications



\- Digital document integrity verification

\- Academic certificate authentication

\- Document forgery research

\- Secure document management

\- Cybersecurity and digital forensics education



\## Future Enhancements



\- Advanced AI-based forgery localization

\- Support for additional document formats

\- Improved robustness against image transformations

\- Automated verification reporting

\- Enhanced document authentication workflows



\## Author



\*\*Anshika Raj\*\*



GitHub: \[ANSHIKARAJ111](https://github.com/ANSHIKARAJ111)



\## Disclaimer



This project is intended for educational, research, and document security demonstration purposes.

