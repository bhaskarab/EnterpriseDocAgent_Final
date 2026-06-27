from loguru import logger

NO_ANSWER_PHRASES = [
    "i don't have enough information",
    "i cannot find",
    "not found in the documents",
    "no relevant documents were found",
    "no relevant information",
    "i don't know",
    "unable to find",
    "not mentioned in",
    "no information available",
]

MIN_RESPONSE_LENGTH = 20


class GuardrailsService:
    def validate_response(self, response: str, query: str) -> dict:
        if not response or not response.strip():
            logger.warning("Empty response received")
            return {
                "answer": "I was unable to generate a response. Please try again.",
                "is_grounded": False,
                "warning": "Empty response",
            }

        response = response.strip()
        if len(response) < MIN_RESPONSE_LENGTH:
            logger.warning("Response too short for query: {}", query)
            return {
                "answer": "I could not find enough information to answer your question. Please try rephrasing.",
                "is_grounded": False,
                "warning": "Response too short",
            }

        response_lower = response.lower()
        for phrase in NO_ANSWER_PHRASES:
            if phrase in response_lower:
                logger.info("Agent indicated no answer found for: {}", query)
                return {
                    "answer": response,
                    "is_grounded": False,
                    "warning": "Agent could not find relevant information",
                }

        logger.info("Response passed guardrails checks")
        return {"answer": response, "is_grounded": True, "warning": None}

    def format_response(self, validated_response: dict) -> str:
        answer = validated_response["answer"]
        warning = validated_response["warning"]
        is_grounded = validated_response["is_grounded"]

        if not is_grounded and warning:
            return (
                f"{answer}\n\n---\n"
                "*Note: This response may not be fully grounded in the uploaded documents.*"
            )
        return answer
