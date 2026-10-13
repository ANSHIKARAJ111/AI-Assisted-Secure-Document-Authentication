
from src.authentication import sign_document, verify_document

original = b"University Certificate - Student A - Grade A"

record = sign_document(original, "CERT2026")

valid, message = verify_document(original, record)
print("Original:", valid, message)
assert valid

tampered = b"University Certificate - Student A - Grade A+"

valid, message = verify_document(tampered, record)
print("Tampered:", valid, message)
assert not valid

modified_record = record.copy()
modified_record["document_id"] = "FAKE2026"

valid, message = verify_document(original, modified_record)
print("Forged record:", valid, message)
assert not valid

print("AUTHENTICATION TESTS PASSED!")
