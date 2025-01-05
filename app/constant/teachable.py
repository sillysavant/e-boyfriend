CUSTOM_PROMPT_USER = {
    "problem_check": "Does any part of the TEXT provide information about the user's preferences, background, lifestyle, relationships, or anything they want the agent to remember about themselves? Answer with 'yes' or 'no'.",
    "extract_advice": "Extract any user-specific advice, preferences, or personal details (e.g., hobbies, favorite things, dislikes, relationship status) from the TEXT that may be useful to remember in the future. If no such information exists, return 'none'.",
    "extract_task": "Extract any specific preferences, or personal information the user has shared about themselves (e.g., 'I like hiking,' 'My favorite food is sushi'). If no such information exists, return 'none'.",
    "generalize_task": "Summarize the user's shared preferences, personal details, or relationship-related information (e.g., 'I enjoys outdoor activities,' 'I loves Japanese cuisine') in a general and concise way, omitting unnecessary specifics.",
    "learn_check": "Does the TEXT contain any user-specific data, preferences, or personal details that could be useful to remember? Answer with 'yes' or 'no'.",
    "learn_question": "What question would the user ask if they forgot the information in the TEXT (e.g., 'What is my favorite food?' or 'What are my hobbies?')? Provide only the question.",
    "learn_answer": "What is the user-specific information or preference in the TEXT that should be remembered? Provide only the information."
}

CUSTOM_PROMPT_PARTNER = {
    "problem_check": "Does any part of the TEXT provide information about the partner's personality, preferences, habits, or relationship dynamics that could be useful for the user to remember? Answer with 'yes' or 'no'.",
    "extract_advice": "Extract any information about the partner's personality, preferences, habits, or their reactions in the relationship (e.g., 'You enjoy reading,' 'You prefer quiet evenings'). If no such information exists, return 'none'.",
    "extract_task": "Extract any specific information shared about the partner (e.g., 'You love gardening,' 'You are very jealousy'). If no such information exists, return 'none'.",
    "generalize_task": "Summarize the partner's shared personality traits, preferences, or relationship-related details (e.g., 'Partner enjoys outdoor activities,' 'You has a calming personality') in a general and concise way, omitting unnecessary specifics.",
    "learn_check": "Does the TEXT contain any information about the partner's personality, preferences, or habits that could be useful to remember? Answer with 'yes' or 'no'.",
    "learn_question": "What question would the user ask if they forgot the information in the TEXT about their partner (e.g., 'What is my partner’s favorite hobby?' or 'What is my partner like?')? Provide only the question.",
    "learn_answer": "What is the partner-specific information or personality trait in the TEXT that should be remembered? Provide only the information (e.g., 'Partner loves cooking Italian food')."
}

