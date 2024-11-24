import prompty
import prompty.azure
from pydantic import BaseModel
from prompty.tracer import trace, Tracer, PromptyTracer


# local_trace = PromptyTracer()
# Tracer.add("local", local_trace.tracer)

actions_prompty = prompty.load("actions.prompty")


class ToolCall(BaseModel):
    id: str
    name: str
    arguments: str


@trace
async def create_actions(scene: str, input: str):
    tools = await prompty.execute_async(
        actions_prompty, inputs={"scene": scene, "input": input}
    )

    return [
        ToolCall(id=tool.id, name=tool.name, arguments=tool.arguments) for tool in tools
    ]


if __name__ == "__main__":
    import asyncio

    scene = """
- id: x-black
  position: Left
  name: Xbox Series S - Black (Certified Refurbished)
  price: $299.99
- id: s-white
  position: Front Center
  name: Xbox Series S - All-Digital - White
  price: $349.99
- id: x-black
  position: Right
  name: Xbox Series X - Disc Drive - Black
  price: $499.99
- id: x-galaxy
  position: Back Right
  name: Xbox Series X - Disc Drive - Galaxy Black Special Edition
  price: $599.99
- id: x-white
  position: Back Left
  name: Xbox Series X - All-Digital - White
  price: $449.99
""".strip()

    input = "can you show me the one in the back?"
    asyncio.run(create_actions(scene, input))
