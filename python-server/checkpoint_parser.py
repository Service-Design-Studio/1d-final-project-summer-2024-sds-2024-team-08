def print_checkpoint(obj):
    for msg in obj["channel_values"]["messages"]:
        print_message(msg)

def print_message(msg):
    max_chars = 60
    msg_kwargs = msg["kwargs"]
    tool_ls = msg_kwargs.get("tool_calls")
    typ = msg_kwargs["type"]

    if typ == "human":
        print("")

    line = typ + "\t"
    match typ:
        case "ai": colour = 32
        case "tool": colour = 90
        case "human": colour = 96
        case _: raise "skfjdghsdfkjlghsdf"

    if tool_ls:
        tools = ', '.join([f'{t["name"]}, {t["id"]}' for t in msg_kwargs.get("tool_calls")])
        line += f"Calling tool(s): {tools}"
    else:
        text = str(msg_kwargs["content"]).replace('\n', ' ')
        if len(text) > max_chars:
            text = f"{text[:max_chars]}... [{len(text) - max_chars}]"
        line += text
        if typ=='tool':
            line += msg_kwargs["tool_call_id"]
    
    print(f"\033[{colour}m{line}\033[0m")
    


if __name__ == "__main__":
    from app.models import Checkpoint_ORM
    from app.database import user_engine
    from sqlalchemy.orm import Session
    from sqlalchemy import select
    import json

    with Session(user_engine) as s:
        stmt = select(Checkpoint_ORM.cp_data).where(Checkpoint_ORM.chat_id == 10)[-1]
        obj = json.loads(s.scalar(stmt))

    print_checkpoint(obj)