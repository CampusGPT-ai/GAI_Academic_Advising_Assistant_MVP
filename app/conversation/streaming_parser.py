import asyncio
import json
import re

from typing import Any, AsyncIterator, Literal, Union, cast
from langchain.callbacks.streaming_aiter import AsyncIteratorCallbackHandler
from langchain.schema import LLMResult
from models import ChatMessage, Citation
import logging, sys
from util.logger_format import CustomFormatter

ch = logging.StreamHandler(stream=sys.stdout)
ch.setLevel(logging.INFO)
ch.setFormatter(CustomFormatter())
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.handlers.clear()  
logger.addHandler(ch)  

class StreamingParser(AsyncIteratorCallbackHandler):
    def __init__(self, user, conversation, user_question, memory) -> None:
        super().__init__()
        self.invocation = 0
        self.citations =[]
        self.followups =[]
        self.buffer = ""
        self.conversation = conversation
        self.memory = memory
        self.user_question = user_question
        self.bot_response = ""

    async def aiter(self) -> AsyncIterator[str]:
        while not self.queue.empty() or not self.done.is_set():
            # Wait for the next token in the queue,
            # but stop waiting if the done event is set
            done, other = await asyncio.wait(
                [
                    # NOTE: If you add other tasks here, update the code below,
                    # which assumes each set has exactly one task each
                    asyncio.ensure_future(self.queue.get()),
                    asyncio.ensure_future(self.done.wait()),
                ],
                return_when=asyncio.FIRST_COMPLETED,
            )

            # Cancel the other task
            if other:
                other.pop().cancel()

            # Extract the value of the first completed task
            token_or_done = cast(Union[str, Literal[True]], done.pop().result())

            # If the extracted value is the boolean True, the done event was set
            if token_or_done is True:
                if self.invocation == 0:
                    break
                else:
                    yield "<<<META-DATA>>>" + self.prepare_metadata()

            # Otherwise, the extracted value is a token, which we yield
            if (self.invocation == 0):
                yield token_or_done.replace("\n", "<br/> ")
            else: 
                if (token_or_done != True):
                    self.buffer += token_or_done
                continue


    async def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
       
        if (self.invocation == 0):
            self.invocation += 1
            self.bot_response = response.generations[0][0].message.content
            self.parseCitations(self.bot_response)
            
            # save the raw context of the conversation
            self.memory.save_context({"input": self.user_question}, {"output": self.bot_response})

            self.done.clear()
        else:
            self.done.set()
        
    def parseCitations(self, response):
        #logger.info(f"full response completed: {response}")
        parts = re.split(r'\[([^\]]+)\]', response)
        #logger.info(f"split bot response into parts: {parts}")

        self.citations = []
        bot_response = ""
        cit_index = 1
        for i in range(0, len(parts)):
            if (i % 2 == 0):
                bot_response += parts[i]
                if i < len(parts) - 1:
                    bot_response += f"[{cit_index}]"
            else:
                if (self.citations_contain(parts[i]) != True):
                    self.citations.append(
                        Citation(
                            citation_text=parts[i],
                            citation_path=f"{parts[i]}")
                    )
                    cit_index += 1
                #if (self.followups_contain(parts[i]) != True):
                  #  self.followups.append(follow_up_questions=parts[i])
                    
        logger.info(f"parsed response is: {bot_response}")

    def citations_contain(self, citation_text):
        for cit in self.citations:
            if (cit.citation_text == citation_text):
                return True
        return False
    

    def prepare_metadata(self):
        print("getting metadata")
        self.buffer = self.buffer.replace("```", "")
        self.buffer = self.buffer.replace("json", "")
        while (self.buffer.startswith("{") == False):
            self.buffer = self.buffer[1:]
        
 
        # after cleaning the current buffer is a json doc with some of the metadata
        js = json.loads(self.buffer)
        self.followups = js.get("followups")
        print("topic: " + js.get("topic"))
        # if the conversation does not have a topic yet, set it to the topic in this answer
        if (self.conversation.topic is None or self.conversation.topic == ""):
            print("Setting topic to: " + js.get("topic"))
            self.conversation.topic = js.get("topic")

        self.conversation.save()
        
        print(f"print follow up questions {self.followups}")
        
        hist_message = ChatMessage(
            conversation=self.conversation, 
            user="", 
            user_question=self.user_question,
            bot_response=self.bot_response,
            citations=self.citations,
            follow_up_questions=self.followups
        )
        
        hist_message.save()
        print("history saved")   
        
        #create a new json doc to return
        js_rv = {}

        # add citations and the conversation to the json doc
        cits = map(lambda cit: cit.to_json(), self.citations)
        js_rv.update({"citations": list(cits)})  
        js_rv.update({"conversation": self.conversation.to_json()})
        js_rv.update({"followups": js.get("followups")})
        
        return json.dumps(js_rv)