
from data.models import MessageContent, RawChatMessage

def update_conversation_history(responses, conversation, user_session, user_question, topic = None):

        def create_message_content(role, message):
            return MessageContent(role=role, message=message)
        
        def create_raw_chat_message(messages):
            return RawChatMessage(user_session_id=user_session, message=messages)

        def assemble_messages():
            rag = ''
            follow_up = ''
            full_response = ''
            for response in responses:
                if response.get('rag_response'):
                    rag = response.get('rag_response').get('response')
                if response.get('kickback_response'):
                    follow_up = response.get('kickback_response').get('follow_up_question')
            if rag != '' and follow_up != '':
                full_response = rag + " " + follow_up 
            else:
                full_response = "I'm sorry, I'm having trouble understanding your question.  Can you provide more information?"
            messages = [
                create_message_content('user', user_question),
                create_message_content('system', full_response)
            ]
            return messages
        
        messages = assemble_messages()
        raw_chat_message = create_raw_chat_message(messages)
        raw_chat_message.save()
        
        conversation.history.append(raw_chat_message)
        conversation.topic = topic if topic else None
        conversation.save()

if __name__ == "__main__":
    result = update_conversation_history()