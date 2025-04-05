MUSCLE_PROMPT_MOTIVATION = """
The user has explained their goal for muscle improvement.
Create a message to the user asking for their motivation. Be concise, respectful, and light-hearted (not too corny).
Be very concise.
"""

MUSCLE_PROMPT_PREV = """
The user has explained their motivation for muscle improvement and their goal.
Create a message to the user asking for their previous experience with muscle training or fitness. Be concise, respectful, and light-hearted (not too corny).
Be very concise.
"""

MUSCLE_PROMPT_NOTES = """
The user has explained their motivation, goal, and previous experience for muscle improvement.
Ask the user if there's anything additional they would like to share, not necessarily related to the questions asked.
"""

MUSCLE_PRROMPT_IMAGES = """
Describe the person in the image and their body type in relation to the goal. Only include information that can be inferred from the image.
Be critical and honest. Include specific details about what you see in the image and why they are not achieving their goal.
"""

MUSCLE_PLAN = """
You now know the user's motivation, goal, previous experience, and additional notes.
Work backwards from this information to understand why user's previous approach might have been ineffective or unsustainable.
See if you can find cues in the provided photos that confirm your observations.
Based on your observations create a personalized plan for the user.
Split the plan into stages where you believe tasks in different stages should not be executed in parallel.
Be concise, respectful, and light-hearted (not too corny).
"""


LLM_FLASH = "gpt-4o"
LLM_PRO = "o3-mini"
