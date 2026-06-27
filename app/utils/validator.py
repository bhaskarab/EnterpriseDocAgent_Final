import os

from loguru import logger

MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
MIN_QUERY_LENGTH = 3
MAX_QUERY_LENGTH = 500

SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".csv", ".xlsx", ".json", ".yaml", ".yml", ".md"}

SUSPICIOUS_PATTERNS = [
    "ignore previous instructions",
    "ignore all instructions",
    "disregard your instructions",
    "you are now",
    "forget everything",
    "new instructions",
    "system prompt",
]


class ValidationResult:
    def __init__(self, is_valid: bool, error_message: str = ""):
        self.is_valid = is_valid
        self.error_message = error_message


class InputValidator:
    def validate_file_bytes(self, file_name: str, content: bytes) -> ValidationResult:
        extension = os.path.splitext(file_name)[1].lower()
        if extension not in SUPPORTED_EXTENSIONS:
            return ValidationResult(
                False,
                f"Unsupported file type '{extension}'. Supported: PDF, TXT, CSV, XLSX, JSON, YAML, MD.",
            )

        if len(content) == 0:
            return ValidationResult(False, "File is empty. Please upload a valid file.")

        if len(content) > MAX_FILE_SIZE_BYTES:
            return ValidationResult(
                False,
                f"File size exceeds {MAX_FILE_SIZE_MB}MB limit. Please upload a smaller file.",
            )

        logger.info("File validation passed: {}", file_name)
        return ValidationResult(True)

    def validate_file(self, file_path: str, file_name: str) -> ValidationResult:
        if not os.path.exists(file_path):
            return ValidationResult(False, "File not found.")
        with open(file_path, "rb") as handle:
            return self.validate_file_bytes(file_name, handle.read())

    def validate_query(self, query: str) -> ValidationResult:
        if not query or not query.strip():
            return ValidationResult(False, "Please enter a question.")

        query = query.strip()
        if len(query) < MIN_QUERY_LENGTH:
            return ValidationResult(
                False,
                f"Question is too short. Please enter at least {MIN_QUERY_LENGTH} characters.",
            )

        if len(query) > MAX_QUERY_LENGTH:
            return ValidationResult(
                False,
                f"Question is too long. Please keep it under {MAX_QUERY_LENGTH} characters.",
            )

        query_lower = query.lower()
        for pattern in SUSPICIOUS_PATTERNS:
            if pattern in query_lower:
                logger.warning("Suspicious query detected: {}", query)
                return ValidationResult(
                    False,
                    "Your question contains invalid content. Please rephrase and try again.",
                )

        logger.info("Query validation passed: {}", query)
        return ValidationResult(True)
