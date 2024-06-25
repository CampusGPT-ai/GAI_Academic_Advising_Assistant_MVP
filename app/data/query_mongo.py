import csv, json
from mongoengine import connect
from cloud_services.connect_mongo import MongoConnection
from data.models import ConversationSimple, Profile


mongo_conn = MongoConnection()
mongo_conn.connect()

def format_datetime(dt):
    """Formats the datetime object into a readable string."""
    if dt:
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    return ''

def export_messages_to_csv(filename):
    # Open a CSV file for writing
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        fieldnames = [
            'user_id', 'first_name', 'last_name', 'email', 'considerations', 
            'conversation_id', 'message_id', 'message_content', 'message_timestamp', 'message_role', 'rag_results', 'q1_usefullness_scale', 'q1_uesefullness_comment', 'q2_relevancy_scale', 'q2_relevancy_comment', 'q3_accuracy_scale', 'q3_accuracy_comment'
        ]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        # Fetch all conversations
        for conversation in ConversationSimple.objects:
            # Fetch the user profile for each conversation
            profile = Profile.objects(user_id=conversation.user_id).first()
            if profile:
                considerations_str = json.dumps([dict(consideration) for consideration in profile.considerations])
                first_name = profile.first_name
                last_name = profile.last_name
                email = profile.email
            else:
                considerations_str, first_name, last_name, email = '', '', '', ''

            for raw_message_ref in conversation.history:
                # Accessing referenced RawChatMessage directly
                raw_message = raw_message_ref

                for msg_content in raw_message.message:
                    # Prepare data to write to CSV
                    data = {
                        'user_id': conversation.user_id,
                        'first_name': first_name,
                        'last_name': last_name,
                        'email': email,
                        'considerations': considerations_str,
                        'conversation_id': str(conversation.id),
                        'message_id': str(raw_message.id),
                        'message_content': msg_content.message,
                        'message_timestamp': format_datetime(msg_content.created_at),
                        'message_role': msg_content.role,
                        'rag_results': msg_content.rag_results,
                        'q1_usefullness_scale': msg_content.feedback.get("q1_usefullness").get("scale") if (msg_content.feedback != {} and msg_content.feedback != None) else '',
                        'q1_uesefullness_comment': msg_content.feedback.get("q1_usefullness").get("comment") if (msg_content.feedback != {} and msg_content.feedback != None) else '',
                        'q2_relevancy_scale': msg_content.feedback.get("q2_relevancy").get("scale") if (msg_content.feedback != {} and msg_content.feedback != None) else '',
                        'q2_relevancy_comment': msg_content.feedback.get("q2_relevancy").get("comment") if (msg_content.feedback != {} and msg_content.feedback != None) else '',
                        'q3_accuracy_scale': msg_content.feedback.get("q3_accuracy").get("scale") if (msg_content.feedback != {} and msg_content.feedback != None) else '',
                        'q3_accuracy_comment': msg_content.feedback.get("q3_accuracy").get("comment") if (msg_content.feedback != {} and msg_content.feedback != None) else ''

                    }
                    writer.writerow(data)

if __name__ == '__main__':
    export_messages_to_csv('exported_messages.csv')
