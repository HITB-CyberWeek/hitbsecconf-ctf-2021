import pathlib

__all__ = ["challenge_responses"]

challenge_responses = {}

challenges = pathlib.Path(__file__).parent / "challenges.txt"
for line in challenges.read_text().split():
    prefix, suffix = line[:8], line[8:]
    challenge_responses[prefix] = suffix
