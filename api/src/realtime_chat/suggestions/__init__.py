import asyncio
import prompty
import prompty.azure
from typing import List

from pydantic import BaseModel
from prompty.tracer import trace

suggestions_prompty = prompty.load("suggestions.prompty")
writeup_prompty = prompty.load("writeup.prompty")

class SimpleMessage(BaseModel):
    name: str
    text: str

@trace
async def create_suggestion(customer: str, messages: List[SimpleMessage]):
    inputs = {
        "customer": customer,
        "context": [
            {
                "name": message.name,
                "text": message.text,
            }
            for message in messages
        ],
    }

    result = await prompty.execute_async(
        suggestions_prompty,
        parameters={"stream": True},
        inputs=inputs,
    )

    async for item in result:
        yield item


@trace
async def suggestion_requested(messages: List[SimpleMessage]):
    result: str = await prompty.execute_async(
        writeup_prompty,
        inputs={
            "context": [
                {
                    "name": message.name,
                    "text": message.text,
                }
                for message in messages
            ],
        },
    )

    return result.lower().startswith("y")


async def render(messages: List[SimpleMessage]):
    async for item in create_suggestion(messages):
        print(item, end="")


if __name__ == "__main__":
    messages = [
        SimpleMessage(
            name="user",
            text="I just want to make this trip happen without me breathing to death or, you know, the like. So anything you can give to me or show me.",
        ),
        SimpleMessage(
            name="assistant",
            text="I understand you're gearing up for a snow camping trip and want to stay warm and safe out there. With the image you shared earlier of a tent in snowy conditions, it looks like you're well-prepared with your SkyView 2-Person Tent. Before we dive into product recommendations, is there anything else I should know about your trip?",
        ),
        SimpleMessage(name="user", text="Oh, what do you got for me?"),
        SimpleMessage(
            name="assistant",
            text="For your snow camping adventure, let's ensure you're fully equipped!\n\n1. **MountainDream Sleeping Bag**: This bag is perfect for cold conditions, keeping you warm even when temperatures drop to 15\u00b0F. It's water-resistant and has a contoured mummy shape for heat retention.\n\n2. **RainGuard Hiking Jacket**: It\u2019s waterproof and breathable, with an adjustable hood and ventilation zippers, keeping you dry and comfortable.\n\n3. **TrekReady Hiking Boots**: These sturdy, insulated boots will provide warmth, support, and excellent traction in snowy conditions.\n\nLet's get you set up for a warm and safe trip! Are there any other items you're interested in?",
        ),
    ]

    asyncio.run(render(messages))
