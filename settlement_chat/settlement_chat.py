import autogen
import sys
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent

class SettlementChat:
    def __init__(self,
                 log_file,
                 system_message_file,
                 config_file="CONFIG_LIST.json",
                 first_llm="gemini",
                 second_llm="gpt-3.5-turbo-1106",
                 max_round=12,
                 docs_path=None):
        self.log_file = log_file
        self.config_file = config_file
        self.first_llm = first_llm
        self.second_llm = second_llm
        self.system_message_file = system_message_file
        self.max_round = max_round
        self.logger = self.Logger(self.log_file)
        sys.stdout = self.logger
        self.first_agent = None
        self.second_agent = None
        self.manager = None
        self.docs_path = docs_path

    class Logger(object):
        def __init__(self, file_path):
            self.terminal = sys.stdout
            self.log = open(file_path, "a")
            self.log.truncate(0)

        def write(self, message):
            self.terminal.write(message)
            self.log.write(message)

        def flush(self):
            self.log.flush()

        def close(self):
            self.flush()
            self.log.close()

        def switch(self, new_file):
            self.close()
            self.log = open(new_file, "a")
            self.log.truncate(0)

    @staticmethod
    def termination_msg(msg):
        content = msg.get("content")
        if content.lower() in ("exit", "quit", "stop", "done", "terminate"):
            return True
        return False

    def run(self, message):
        first_model_filter = {"model": [self.first_llm]}
        first_config_list = autogen.config_list_from_json(
            env_or_file=self.config_file, filter_dict=first_model_filter
        )
        first_llm_config = {
            "config_list": first_config_list,
            "timeout": 120,
            "seed": 45,
        }

        seconf_model_filter = {"model": [self.second_llm]}
        second_config_list = autogen.config_list_from_json(
            env_or_file=self.config_file, filter_dict=seconf_model_filter
        )
        second_llm_config = {
            "config_list": second_config_list,
            "timeout": 120,
            "seed": 45,
        }

        system_message = ""
        with open(self.system_message_file, "r") as file:
            system_message = file.read().rstrip("\\n")


        retrieve_config={ "task": "qa", "docs_path": "" }
        if self.docs_path:
            retrieve_config["docs_path"] = self.docs_path

        self.second_agent = RetrieveUserProxyAgent(
            name="First_agent",
            is_termination_msg=self.termination_msg,
            system_message=system_message,
            llm_config=second_llm_config,
            human_input_mode="NEVER",
            retrieve_config=retrieve_config,
            code_execution_config=False
        )

        self.first_agent = RetrieveUserProxyAgent(
            name="Second_agent",
            is_termination_msg=self.termination_msg,
            system_message=system_message,
            llm_config=first_llm_config,
            human_input_mode="NEVER",
            retrieve_config=retrieve_config,
            code_execution_config=False
        )

        groupchat = autogen.GroupChat(
            agents=[self.second_agent, self.first_agent],
            messages=[],
            max_round=self.max_round,
            speaker_selection_method="round_robin"
        )
        self.manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=second_llm_config)
        self.manager.initiate_chat(self.manager, message=message)
        self.chat_messages=str(self.manager.chat_messages)
        self.manager.clear_history()
        return self.chat_messages
    
    def get_summary(self):
        PRE_PROMPT = "Please provide an informative detailed summary of the following: "
        POST_PROMPT = "\nDo not miss any details, make your summary accurate clear and well defined."
        PROMPT = PRE_PROMPT + self.chat_messages + POST_PROMPT
        NAME = "Summerizing agent"
        self.first_agent.reset()
        userproxyagent = autogen.UserProxyAgent(name=NAME,
                                                human_input_mode="NEVER",
                                                max_consecutive_auto_reply=1)
        userproxyagent.initiate_chat(self.first_agent, message=PROMPT)
        product_details = sorted(userproxyagent.chat_messages.items())[0][1][1]['content']
        return product_details
    
    def get_code(self):
        PRE_PROMPT = "Please provide concluded code result of the following conversation: "
        POST_PROMPT = """\nClear the conversation from duplications,
                            collect all code sections, and write them in the right order,
                            clear and well defined."""
        PROMPT = PRE_PROMPT + self.chat_messages + POST_PROMPT
        NAME = "Code agent"
        self.first_agent.reset()
        userproxyagent = autogen.UserProxyAgent(name=NAME,
                                                human_input_mode="NEVER",
                                                max_consecutive_auto_reply=1,
                                                code_execution_config=False)
        userproxyagent.initiate_chat(self.first_agent, message=PROMPT)
        product_code = sorted(userproxyagent.chat_messages.items())[0][1][1]['content']
        return product_code