# One-Stop Academic Advising Assistant by Campus Evolve 
Campus Evolve is partnering with Axim Collaborative on an exciting new project aimed at bringing the power of generative AI to higher education academic advising.  The purpose of this repository is to share code and implementation instructions for an AI academic adivising assistant that combines Retrieval Augmented Generation with Large Language Model Integration to allow universities to implement an online assistant for one-stop advising:

![image](https://github.com/CampusGPT-ai/GAI_Academic_Adivising_Assistant_MVP/assets/142542882/c3a2215e-12b2-486b-a175-47a892dbac3f)

## The Problem
Academic Advising is a critical service offered to students aimed at helping the successfully navigate the financial, academic and social complexities that are part of the education process.  Yet, roughly 50% of students are unaware of most major student services at their institution and only around 20% utilize those services apart from academic advising (Source: Tyton Partners, “Listening to Learners: Increasing Belonging in and out of the Classroom” 2023​) 

### Advising Gap
​​The ratio of students to advisors is 296:1 in most US colleges, making it impossible for students to get the personalized advice and support they need.

### Student Challenges 
The most common causes of student drop-out in higher education are financial issues, academic mis-alignment, and outside pressures such as family, work, and health. The most challenged students are often the ones who don’t know where to go for help and don’t make use of advising and support services

### Advisor Challenges
Advisors must navigate a labyrinth of degree program requirements, student records, financial aid, and course credits. The time spent answering logistical questions hinders advisors from more holistic discussions.

### Drop Out Costs
When students drop out, colleges face reduced public funding, lower tuition fees, higher recruitment costs, and many more challenges, creating a cycle of decline

## Table of Contents

## Features

### AI Service Definitions
This codebase provides a structured approach to connect with the Azure Open AI service. It defines several client classes to interact with different aspects of the service, such as chat and embeddings, across various deployment environments like Azure, LangChain, and OpenAI.

#### Usage
To use these clients, you need to have the necessary credentials and access to the Azure Open AI services. Import the relevant classes and instantiate them with the appropriate parameters. You can then use these instances to interact with the Azure Open AI services, like sending chat messages or embedding texts.

#### Classes and Main Methods
AILLMClients
An abstract base class for AI Language Model (LLM) clients.

#### Methods
chat(): Abstract method to be implemented for sending chat messages.
embed(): Abstract method to be implemented for embedding text.

#### LangChainLLMClients
A class for LangChain Language Model clients.

#### Parameters
deployment (str): The deployment environment.
version (str): The version of the language model.
endpoint (str): The endpoint URL.
#### Attributes
client (AzureChatOpenAI): The Azure Chat OpenAI client.
embeddings (AzureOpenAIEmbeddings): The Azure OpenAI Embeddings client.
#### Methods
chat(messages: List[Message]) -> Any: Sends chat messages and returns the response.
embed(text: str) -> List[float]: Embeds text using the embedding model.

#### AzureLLMClients
A class for Azure Language Model clients.

#### Parameters
azure_endpoint (str): The Azure endpoint URL.
model (str): The model name.
embedding_model (str): The embedding model name.
deployment (str): The deployment environment.
api_version (str): The API version.
#### Methods
chat(messages: List[Message], json_mode: bool): Sends chat messages and returns the response.
embed(text: str): Embeds text and returns embedding.
embed_many(inputs: List[str]): Embeds multiple texts.

#### OpenAILLMClients
A class for OpenAI language model clients.

#### Parameters
model (str): The language model name.
embedding_model (str): The embedding model name.
api_key (str): The API key.
#### Methods
chat(is_streaming: bool, messages: List[Message]): Sends chat messages and returns the response.
embed(text: str) -> openai_response_objects.Embedding: Embeds text and returns the embedding.

#### Utility Functions
#### normalize_text(s: str, sep_token: str = " \n ")
Normalizes the input text by removing extra spaces and unwanted characters.

#### get_tokens(text: str) -> List[int]
Tokenizes the given text using a specified tokenizer.

#### convert_to_langchain(messages: List[Message]) -> List[Either[HumanMessage, SystemMessage]]
Converts a list of Message objects into LangChain's HumanMessage or SystemMessage objects.

#### get_llm_client(...)
Instantiates and returns an appropriate LLM client based on the specified API type and other parameters.

#### Additional Information
Ensure you have the necessary dependencies installed, like openai, azure.identity, and custom modules like openai_response_objects.
Proper Azure credentials and access rights are needed to use these clients.
Handle exceptions appropriately, especially in network calls and tokenization processes.
Logging is configured to output to stdout for better monitoring and debugging.
This framework provides a flexible and consistent way to integrate and utilize the Azure Open AI services in various applications and environments.

### Vector Indexing and Embedding
### Retrieval Evaluation Framework
### Prompt structure
#### Prompting with History
#### Injecting student profile data
#### Retrieval augmentation with auto-merging retrieval and cosign similarity search
### Response Streaming
###  UI/Client set up

## Environment Set Up

## Running Locally

## Deployment

## Customizing the UI and Theming

## Code Reference 

## Challenges and Potential Extensions

## FAQ and Troubleshooting


