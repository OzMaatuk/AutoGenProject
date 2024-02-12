import autogen
import sys
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent

class SettlementChat:
    def __init__(self, log_file, config_file, system_message_file, max_round=12, docs_path=None):
        self.log_file = log_file
        self.config_file = config_file
        self.system_message_file = system_message_file
        self.max_round = max_round
        self.logger = self.Logger(self.log_file)
        sys.stdout = self.logger
        self.bard_pm = None
        self.oai_pm = None
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
        filter_bard_dict = {"model": ["gemini"]}
        bard_config_list = autogen.config_list_from_json(
            env_or_file=self.config_file, filter_dict=filter_bard_dict
        )
        bard_llm_config = {
            "config_list": bard_config_list,
            "timeout": 120,
            "seed": 45,
        }

        filter_oai_dict = {"model": ["gpt-3.5-turbo-1106"]}
        oai_config_list = autogen.config_list_from_json(
            env_or_file=self.config_file, filter_dict=filter_oai_dict
        )
        oai_llm_config = {
            "config_list": oai_config_list,
            "timeout": 120,
            "seed": 45,
        }

        system_message = ""
        with open(self.system_message_file, "r") as file:
            system_message = file.read().rstrip("\\n")


        retrieve_config={ "task": "qa", "docs_path": "" }
        if self.docs_path:
            retrieve_config["docs_path"] = self.docs_path

        self.oai_pm = RetrieveUserProxyAgent(
            name="Openai_agent",
            is_termination_msg=self.termination_msg,
            system_message=system_message,
            llm_config=oai_llm_config,
            human_input_mode="NEVER",
            retrieve_config=retrieve_config
        )

        self.bard_pm = RetrieveUserProxyAgent(
            name="Google_agent",
            is_termination_msg=self.termination_msg,
            system_message=system_message,
            llm_config=bard_llm_config,
            human_input_mode="NEVER",
            retrieve_config=retrieve_config
        )

        groupchat = autogen.GroupChat(
            agents=[self.oai_pm, self.bard_pm],
            messages=[],
            max_round=self.max_round,
            speaker_selection_method="round_robin"
        )
        self.manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=oai_llm_config)
        self.manager.initiate_chat(self.manager, message=message)
        self.chat_messages=str(self.manager.chat_messages)
        self.manager.clear_history()
        return self.chat_messages
    
    def get_summary(self):
        PRE_PROMPT = "Please provide an informative detailed summary of the following: "
        POST_PROMPT = "\nDo not miss any details, make your summary accurate clear and well defined."
        PROMPT = PRE_PROMPT + self.chat_messages + POST_PROMPT
        NAME = "Summerizing agent"
        self.bard_pm.reset()
        userproxyagent = autogen.UserProxyAgent(name=NAME, human_input_mode="NEVER", max_consecutive_auto_reply=1)
        userproxyagent.initiate_chat(self.bard_pm, message=PROMPT)
        product_details = sorted(userproxyagent.chat_messages.items())[0][1][1]['content']
        return product_details