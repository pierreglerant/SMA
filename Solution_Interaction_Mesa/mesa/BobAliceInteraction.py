#!/usr/bin/env python3

import random

from mesa import Model


from communication.agent.CommunicatingAgent import CommunicatingAgent
from communication.message.Message import Message
from communication.message.MessagePerformative import MessagePerformative
from communication.message.MessageService import MessageService


class SpeakingAgent(CommunicatingAgent):
    """ """
    def __init__(self, model, name):
        super().__init__(model, name)
        self.__v = random.randint(0, 1000)

    def step(self):
        super().step()
        list_messages = self.get_new_messages()
        for message in list_messages:
            print(message)
            if message.get_performative() == MessagePerformative.QUERY_REF:
                if message.get_content() == "value of v":
                    self.send_message(Message(self.get_name(), message.get_exp(), MessagePerformative.INFORM_REF, self.__v))
                if isinstance(message.get_content(), int):
                    self.__v = message.get_content()
                    self.send_message(Message(self.get_name(), message.get_exp(), MessagePerformative.INFORM_REF, self.__v))
            if message.get_performative() == MessagePerformative.INFORM_REF:
                if message.get_content != self.__v:
                    self.send_message(Message(self.get_name(), message.get_exp(), MessagePerformative.QUERY_REF, self.__v))


class SpeakingModel(Model):
    """ """
    def __init__(self):
        super().__init__()
        
        self.__messages_service = MessageService(self)
        self.running = True

    def step(self):
        self.__messages_service.dispatch_messages()
        self.agents.shuffle_do("step")



if __name__ == "__main__":
    # Init the model and the agents
    speaking_model = SpeakingModel()
    MessageService.get_instance().set_instant_delivery(False)

    alice = SpeakingAgent(speaking_model, "Alice")
    #speaking_model.schedule.add(alice)

    bob = SpeakingAgent(speaking_model, "Bob")
    #speaking_model.schedule.add(bob)

    charles = SpeakingAgent(speaking_model, "Charles")
    #speaking_model.schedule.add(charles)

   
  

    # Communication part

    alice.send_message(Message(alice.get_name(), charles.get_name(), MessagePerformative.QUERY_REF, "value of v"))
    bob.send_message(Message(bob.get_name(), charles.get_name(), MessagePerformative.QUERY_REF, "value of v"))

    step = 0
    while step < 10:
        speaking_model.step()
        step += 1
