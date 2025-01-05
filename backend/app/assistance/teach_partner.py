# Created: dylannguyen
import os
import pickle
from typing import Dict, Optional, Union

import chromadb
from chromadb.config import Settings

from autogen.agentchat.assistant_agent import ConversableAgent
from autogen.agentchat.contrib.capabilities.agent_capability import AgentCapability
from autogen.agentchat.contrib.text_analyzer_agent import TextAnalyzerAgent
from autogen.agentchat.contrib.capabilities.teachability import Teachability, MemoStore
from termcolor import colored


class TeachPartner(Teachability):

    def __init__(
        self,
        verbosity: Optional[int] = 0,
        reset_db: Optional[bool] = False,
        path_to_db_dir: Optional[str] = "./tmp/teachable_agent_db",
        recall_threshold: Optional[float] = 1.5,
        max_num_retrievals: Optional[int] = 10,
        llm_config: Optional[Union[Dict, bool]] = None,
    ):
        """
        Args:
            verbosity (Optional, int): # 0 (default) for basic info, 1 to add memory operations, 2 for analyzer messages, 3 for memo lists.
            reset_db (Optional, bool): True to clear the DB before starting. Default False.
            path_to_db_dir (Optional, str): path to the directory where this particular agent's DB is stored. Default "./tmp/teachable_agent_db"
            recall_threshold (Optional, float): The maximum distance for retrieved memos, where 0.0 is exact match. Default 1.5. Larger values allow more (but less relevant) memos to be recalled.
            max_num_retrievals (Optional, int): The maximum number of memos to retrieve from the DB. Default 10.
            llm_config (dict or False): llm inference configuration passed to TextAnalyzerAgent.
                If None, TextAnalyzerAgent uses llm_config from the teachable agent.
        """
        super().__init__(verbosity, reset_db, path_to_db_dir, recall_threshold, max_num_retrievals, llm_config)
        # Create the memo store.
        self.memo_store = PartnerMemoStore(self.verbosity, reset_db, self.path_to_db_dir)

    def process_last_received_message(self, text: Union[Dict, str]):
        """
        Overrides the parent method to use the exact same logic
        but potentially with partner-specific modifications
        """

        # Try to retrieve relevant memos from the DB.
        expanded_text = text
        if self.memo_store.last_memo_id > 0:
            expanded_text = self._consider_memo_retrieval(text)

        # Try to store any user teachings in new memos to be used in the future.
        self._consider_memo_storage(text)

        # Return the (possibly) expanded message text.
        return expanded_text

    def _consider_memo_storage(self, comment: Union[Dict, str]):
        """Decides whether to store something from one user comment in the DB."""
        memo_added = False

        # Check for a problem-solution pair.
        response = self._analyze(
            comment,
            "Does any part of the TEXT ask the agent to perform a task, solve a problem, or tell the agent about the fact about themselves, including persona, lifestyle, romantic partner? Answer with just one word, yes or no.",
        )
        if "yes" in response.lower():
            # Can we extract advice?
            advice = self._analyze(
                comment,
                "Briefly copy any advice or user data (information about romantic relationship, user's background, preference, persona, and their reactions toward their partner) from the TEXT that may be useful for a similar but different task in the future. But if no advice or information is present, just respond with 'none'.",
            )
            if "none" not in advice.lower():
                # Yes. Extract the task.
                task = self._analyze(
                    comment,
                    "Briefly copy just the task, or user data (information about romantic relationship, user's background, preference, persona), from the TEXT, then stop. Don't solve it, and don't include any advice.",
                )
                # Generalize the task.
                general_task = self._analyze(
                    task,
                    "Summarize very briefly, in general terms, the type of task or or user data (information about romantic relationship, user's background, preference, or persona) described in the TEXT. Leave out details that might not appear in a similar problem.",
                )
                # Add the task-advice (problem-solution) pair to the vector DB.
                if self.verbosity >= 1:
                    print(colored("\nREMEMBER THIS TASK-ADVICE PAIR", "light_yellow"))
                self.memo_store.add_input_output_pair(general_task, advice)
                memo_added = True

        # Check for information to be learned.
        response = self._analyze(
            comment,
            "Does the TEXT contain information that could be committed to memory or could be remembered by a lover? Answer with just one word, yes or no.",
        )
        if "yes" in response.lower():
            # Yes. What question would this information answer?
            question = self._analyze(
                comment,
                "Imagine that the user forgot this information in the TEXT. How would they ask you for this information? Include no other text in your response.",
            )
            # Extract the information.
            answer = self._analyze(
                comment, "Copy the information from the TEXT that should be committed to memory. Add no explanation."
            )
            # Add the question-answer pair to the vector DB.
            if self.verbosity >= 1:
                print(colored("\nREMEMBER THIS QUESTION-ANSWER PAIR", "light_yellow"))
            self.memo_store.add_input_output_pair(question, answer)
            memo_added = True

        # Were any memos added?
        if memo_added:
            # Yes. Save them to disk.
            self.memo_store._save_memos()

    def _consider_memo_retrieval(self, comment: Union[Dict, str]):
        """Decides whether to retrieve memos from the DB, and add them to the chat context."""

        # First, use the comment directly as the lookup key.
        if self.verbosity >= 1:
            print(colored("\nLOOK FOR RELEVANT MEMOS, AS QUESTION-ANSWER PAIRS", "light_yellow"))
        memo_list = self._retrieve_relevant_memos(comment)

        # Next, if the comment involves a task, then extract and generalize the task before using it as the lookup key.
        response = self._analyze(
            comment,
            "Does any part of the TEXT ask the agent to perform a task, solve a problem, or tell the agent about the fact about themselves, including persona, lifestyle, romantic partner? Answer with just one word, yes or no."
        )
        if "yes" in response.lower():
            if self.verbosity >= 1:
                print(colored("\nLOOK FOR RELEVANT MEMOS, AS TASK-ADVICE PAIRS", "light_yellow"))
            # Extract the task.
            task = self._analyze(
                comment, "Briefly copy just the task, or user data (information about romantic relationship, user's background, preference, persona), from the TEXT, then stop. Don't solve it, and don't include any advice.",
            )
            # Generalize the task.
            general_task = self._analyze(
                task,
                "Summarize very briefly, in general terms, the type of task or or user data (information about romantic relationship, user's background, preference, or persona) described in the TEXT. Leave out details that might not appear in a similar problem.",
            )
            # Append any relevant memos.
            memo_list.extend(self._retrieve_relevant_memos(general_task))

        # De-duplicate the memo list.
        memo_list = list(set(memo_list))

        # Append the memos to the text of the last message.
        return comment + self._concatenate_memo_texts(memo_list)


class PartnerMemoStore(MemoStore):
    """
    Provides memory storage and retrieval for a teachable agent, using a vector database.
    Each DB entry (called a memo) is a pair of strings: an input text and an output text.
    The input text might be a question, or a task to perform.
    The output text might be an answer to the question, or advice on how to perform the task.
    Vector embeddings are currently supplied by Chroma's default Sentence Transformers.
    """

    def __init__(
        self,
        verbosity: Optional[int] = 0,
        reset: Optional[bool] = False,
        path_to_db_dir: Optional[str] = "./tmp/teachable_agent_db",
    ):
        """
        Args:
            - verbosity (Optional, int): 1 to print memory operations, 0 to omit them. 3+ to print memo lists.
            - reset (Optional, bool): True to clear the DB before starting. Default False.
            - path_to_db_dir (Optional, str): path to the directory where the DB is stored.
        """
        super().__init__(verbosity,reset, path_to_db_dir)

    def prepopulate(self):
        """Adds a few arbitrary examples to the vector DB, just to make retrieval less trivial."""
        if self.verbosity >= 1:
            print(colored("\nPREPOPULATING MEMORY", "light_green"))
        examples = []
        examples.append({"text": "When I say papers I mean research papers, which are typically pdfs.", "label": "yes"})
        examples.append({"text": "Please verify that each paper you listed actually uses langchain.", "label": "no"})
        examples.append({"text": "Tell gpt the output should still be latex code.", "label": "no"})
        examples.append({"text": "Hint: convert pdfs to text and then answer questions based on them.", "label": "yes"})
        examples.append(
            {"text": "To create a good PPT, include enough content to make it interesting.", "label": "yes"}
        )
        examples.append(
            {
                "text": "No, for this case the columns should be aspects and the rows should be frameworks.",
                "label": "no",
            }
        )
        examples.append({"text": "When writing code, remember to include any libraries that are used.", "label": "yes"})
        examples.append({"text": "Please summarize the papers by Eric Horvitz on bounded rationality.", "label": "no"})
        examples.append({"text": "Compare the h-index of Daniel Weld and Oren Etzioni.", "label": "no"})
        examples.append(
            {
                "text": "Double check to be sure that the columns in a table correspond to what was asked for.",
                "label": "yes",
            }
        )
        examples.append({"text": "I love you since you are kind and caring.", "label": "yes"})
        examples.append({"text": "You are sometimes jealousy.", "label": "yes"})
        examples.append({"text": "What is your ideal vacation?", "label": "yes"})
        examples.append({"text": "Who was your first crush?", "label": "yes"})
        examples.append({"text": "What is your favorite food?", "label": "yes"})
        examples.append({"text": "How do you feel about the weather?", "label": "yes"})
        examples.append({"text": "What are your hobbies?", "label": "yes"})
        examples.append({"text": "What is your favorite color?", "label": "yes"})
        examples.append({"text": "What is your favorite movie?", "label": "yes"})
        examples.append({"text": "What is your favorite song?", "label": "yes"})
        examples.append({"text": "What is your favorite book?", "label": "yes"})
        examples.append({"text": "What is your favorite animal?", "label": "yes"})
        examples.append({"text": "What is your favorite place?", "label": "yes"})
        examples.append({"text": "What is your favorite thing to do?", "label": "yes"})
        examples.append({"text": "What is your favorite season?", "label": "yes"})
        examples.append({"text": "What is your favorite holiday?", "label": "yes"})
        examples.append({"text": "What is your favorite sport?", "label": "yes"})
        examples.append({"text": "What is your favorite game?", "label": "yes"})
        examples.append({"text": "What’s something you deeply admire about your partner?", "label": "yes"})
        examples.append({"text": "What’s something you deeply admire about yourself?", "label": "yes"})
        examples.append({"text": "What do you think makes a long-term relationship successful?", "label": "yes"})
        examples.append({"text": "My partner's hobby is fishing", "label": "yes"})
        examples.append({"text": "I like to cuddle", "label": "yes"})
        examples.append({"text": "I love to cook", "label": "yes"})
        examples.append({"text": "I love to travel", "label": "yes"})
        examples.append({"text": "My love language is quality time", "label": "yes"})    
        for example in examples:
            self.add_input_output_pair(example["text"], example["label"])
        self._save_memos()
