import json
import os
#sys.path.append("/Users/rstaudinger/code/isupportu-/app/backend")
from datetime import datetime
from mongoengine import connect, disconnect
from institution.institution import Institution
from app.backend.user_profile.profile_internal import Profile
from settings.settings import Settings
from conversation.topic import Topic
from conversation.conversation import Conversation
from conversation.chat_message import ChatMessage


def main():
    settings = Settings(_env_file="app/backend/.env")
    connect(settings.model_extra["mongo_db"], host=settings.model_extra["mongo_conn_str"])

    # Create an institution if it doesn't exist
    inst = Institution.objects(institution_id="demo").first()
    if (inst is None):
        inst = Institution(
            institution_id="demo",
            name="FSU-demo",
            website="https://www.fsu.edu/",
            logo="https://www.fsu.edu/_/s3.3/img/fsu-seals/fsu-seal-3d-160x160.png"
        )
        inst.save()

    print(inst.to_json())

    # Create a profile
    profile = Profile(
        institution=inst,
        user_id="jjacksonville",
        full_name="Jamal Jacksonville",
        avatar="jamal",
        interests=["team sports", "mental health"],
        demographics={"ethnicity": "African American", "gender": "Male",  "Academic Year": "3"},
        academics={"Major": "Physics", "Minor": "History"},
        courses=["MAC X311", "MAC X312", "MAC X313", "CHM X045", "CHM X045L", "PHY X048C", "PHY 1090",
        "PHY 2048C", "PHY 2049C", "PHY 3045", "PHY 3091", "PHY 3101", "PHY 3221", "PHY 4222",   
        "PHY 4324"]
    )
    profile.save()

    # Print the institution and profile
    print(inst.to_json())
    print(profile.to_json())

    disconnect()


if __name__ == "__main__":
    main()


def setup_demo_profiles():
    inst = Institution.objects(institution_id="demo").first()
    if (inst is None):
        inst = Institution(
            institution_id="demo",
            name="FSU-demo",
            website="https://www.fsu.edu/",
            logo="https://www.fsu.edu/_/s3.3/img/fsu-seals/fsu-seal-3d-160x160.png"
        )
        inst.save()

    # create demo profiles
    jamal = Profile.objects(user_id="jjacksonville").first()
    if (jamal is not None):
        jamal.delete()

    jamal = Profile(
        institution=inst,
        user_id="jjacksonville",
        full_name="Jamal Jacksonville",
        avatar="jamal",
        interests=[
            "team sports", 
            "mental health"
        ],
        demographics={
            "ethnicity": "African American", 
            "gender": "Male",  
            "Academic Year": "3"
        },
        academics={"Major": "Physics", "Minor": "History"},
        courses=["MAC X311", "MAC X312", "MAC X313", "CHM X045", "CHM X045L", "PHY X048C", "PHY 1090",
        "PHY 2048C", "PHY 2049C", "PHY 3045", "PHY 3091", "PHY 3101", "PHY 3221", "PHY 4222",   
        "PHY 4324"]
    )
    jamal.save()

    tif = Profile.objects(user_id="ttallahassee").first()
    if (tif is not None):
        tif.delete()

    tif = Profile(
        institution=inst,
        user_id="ttallahassee",
        full_name="Tiffany Tallahassee",
        avatar="tiffany",
        interests=[
            "languages",
            "outdoor activities",
            "watersports",
            "peforming arts"
        ],
        demographics={
            "ethnicity": "white", 
            "gender": "Female"
        },
        academics={
            "Academic Year": "2",
            "Major": "Computer Engineering", 
            "Minor": ""
        },
        courses=[ "MAC X311", "MAC X312", "MAPX302", "CHM X045/X045L", "CHM X046/X046L", 
          "PHY X048/X048L", "PHY X049/X049L", "EEL 3135", "EEL 3705"]
    )
    tif.save()

    dylan = Profile.objects(user_id="ddaytona").first()
    if (dylan is not None):
        dylan.delete()

    dylan = Profile(
        institution=inst,
        user_id="ddaytona",
        full_name="Dylan Daytona",
        avatar="dylan",
        interests=[
            "languages",
            "outdoor activities",
            "watersports",
            "peforming arts"
        ],
        demographics={
            "ethnicity": "white", 
            "gender": "Male"
        },
        academics={
            "Academic Year": "1",
            "Major": "Business Administration", 
            "Minor": ""
        },
        courses=[]
    )
    dylan.save()

    return inst


def setup_topics(institution):

    # Load the data from demo file
    path = os.path.realpath(os.path.dirname(__file__) + "/../data/demo_topics.json")
    with open(path, 'r') as f:
        data = json.load(f)

    #save topics
    for element in data:
        topic = Topic(
            institution=institution,
            topic=element["topic"],
            question=element["question"],
            answer=element["answer"],
            related_interests=element["related_interests"]
        )
        topic.save()


def setup_conversations(institution):
    user = Profile.objects(user_id="jjacksonville").first()
    convo = Conversation(user=user, topic="team sports")
    convo.save()

    message = ChatMessage(
        user=user,
        conversation=convo,
        user_question="I'm interested in team sports",
        bot_response="I see you're interested in team sports.  I'm not sure how I can help you with that."
    )
    message.save()
    message = ChatMessage(
        user=user,
        conversation=convo,
        user_question="How many more courses do I need to take?",
        bot_response="Based on what I know, you have a lot of courses to take.  I can help you with that."
    )
    message.save()

    convo.end_time = datetime.now()
    convo.save()

    user = Profile.objects(user_id="ddaytona").first()
    convo = Conversation(user=user, topic="poetry")
    convo.save()

    message = ChatMessage(
        user=user,
        conversation=convo,
        user_question="I'm interested in poetry",
        bot_response="I see you're interested in poetry.  I'm not sure how I can help you with that."
    )
    message.save()
    message = ChatMessage(
        user=user,
        conversation=convo,
        user_question="What degrees should I pursue to become a poet?",
        bot_response="Poets come from many educational backgrounds, but English is a popular choice to pursue a career as a writer."
    )
    message.save()

    convo.end_time = datetime.now()
    convo.save()
        

