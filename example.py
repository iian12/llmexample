from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_message_histories import RedisChatMessageHistory
import redis


REDIS_URL = "redis://localhost:6379/0"

model = Ollama(model="llama3:latest")

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You're an assistant."),
        MessagesPlaceholder(variable_name="history"),
        ("user", "{input}"),
    ]
)
runnable = prompt | model | StrOutputParser()

id_session = "test123"


def get_message_history(session_id: str) -> RedisChatMessageHistory:
    return RedisChatMessageHistory(session_id, url=REDIS_URL)


with_message_history = RunnableWithMessageHistory(
    runnable,
    get_message_history,
    input_messages_key="input",
    history_messages_key="history",
)

print('--------------------------------------------------')
print('            Assistant Chatbot v.1                 ')
print(' If you want to end the conversation, type "bye". ')
print('--------------------------------------------------')

while True:

    input_text = input("User : ")

    if input_text == "bye":
        print("The conversation is over")
        break

    result = with_message_history.invoke(
        {"input": input_text},
        config={"configurable": {"session_id": id_session}}
    )

    print("AI : ", result)

print('---------------------------------')
print("History : ")
print(RedisChatMessageHistory("test123", url=REDIS_URL))


def delete_chat_history(session_id: str):
    # redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
    redis_client = redis.from_url(REDIS_URL)
    # Deleting the key associated with session_id
    _del = redis_client.delete(session_id)

    if _del == 1:
        print("session delete success!!")
    else:
        print("session delete failure!!")


delete_chat_history("message_store:" + id_session)
