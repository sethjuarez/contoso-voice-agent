import json
from typing import List, Union
import prompty
import prompty.azure
from prompty.tracer import trace


chat_prompty = prompty.load("chat.prompty")


@trace
async def create_response(
    customer: str,
    question: str,
    context: List[str] = [],
    image: Union[str, None] = None,
):
    inputs = {"customer": customer, "question": question, "context": context}
    if image:
        inputs["image"] = image

    response = await prompty.execute_async(chat_prompty, inputs=inputs)
    r = json.loads(response)
    return r


if __name__ == "__main__":
    import asyncio

    customer = "Seth Juarez"
    question = "My friend just sent me this and I'm worried I don't have the right gear for my camping trip. Can you help me? CALL ME"
    context: List[str] = []
    image = "winter.jpg"

    asyncio.run(create_response(customer, question, context, image))
