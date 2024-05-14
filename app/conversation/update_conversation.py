
from data.models import MessageContent, RawChatMessage
import logging
logger = logging.getLogger(__name__)

def update_conversation_topic(user_session, user_question, conversation):
    from conversation.run_graph import GraphFinder
    finder = GraphFinder(user_session, user_question)
    topic = finder.get_topic_from_question()
    conversation.topic = topic
    conversation.save()
    return

def update_conversation_history_with_feedback(feedback, conversation, message_id, user_session): 
    raw_chat_messages = RawChatMessage.objects(user_session_id=user_session)
    logger.info(f"RAW CHATS: {raw_chat_messages}")
    for r in raw_chat_messages:
        logger.info(f"Raw: {r}")
        for m in r.message:
            logger.info(f"Message: {m._id}, Looking for {message_id}")
            if str(m._id) == message_id:
                logger.info(f"Found target message {message_id}")
                m.feedback = feedback.dict()
                # Update feedback field
                logger.info(f"Updating message with feedback: {feedback}")
        r.save()

    # Return
    return

def update_conversation_history(responses, conversation, rag_results, user_session, user_question):

        def create_message_content(role, message):
            if role == 'system':
                return MessageContent(role=role, message=message, rag_results=rag_results)
            else:
                return MessageContent(role=role, message=message)
        
        def create_raw_chat_message(messages):
            return RawChatMessage(user_session_id=user_session, message=messages)

        def assemble_messages():
            rag = ''
            follow_up = ''
            full_response = ''
            rag_response =  responses.get('rag_response')
            rag = rag_response.get('response')
            kickback_response = responses.get('kickback_response')
            follow_up = kickback_response.get('follow_up_question')
            if rag != '':
                full_response = rag + " " + follow_up 
            else:
                full_response = "I'm sorry, I'm having trouble understanding your question.  Can you provide more information?"
            messages = [
                create_message_content('user', user_question),
                create_message_content('system', full_response)
            ]
            return messages, rag_response
        try:
        
            messages, rag_response = assemble_messages()
            raw_chat_message = create_raw_chat_message(messages)
            raw_chat_message.save()

            print(f"Raw chat message saved: {raw_chat_message}")
            
            conversation.history.append(raw_chat_message)
            conversation.topic = rag_response.get('topic') if rag_response.get('topic') else "No topic"
            conversation.save()

            print(f"Conversation saved: {conversation}")
            return
        except Exception as e:
            logger.error(f"Error saving conversation: {e}")
            raise e

if __name__ == "__main__":
    result = update_conversation_history()
