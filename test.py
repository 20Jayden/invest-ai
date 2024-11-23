from youtube_transcript_api import YouTubeTranscriptApi

# Get transcript from YouTube
transcript = YouTubeTranscriptApi.get_transcript("TWINrTppUl4")

# Combine all text into a single variable
combined_text = ' '.join(entry['text'] for entry in transcript)

# Print the result
print(combined_text)