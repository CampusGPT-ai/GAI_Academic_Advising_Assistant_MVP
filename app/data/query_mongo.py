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
            'conversation_id', 'message_id', 'message_content', 'message_timestamp'
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
                        'message_timestamp': format_datetime(msg_content.created_at)
                    }
                    writer.writerow(data)

if __name__ == '__main__':
    export_messages_to_csv('exported_messages.csv')
