# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from langchain_core.messages import AIMessage, HumanMessage

from assistant.src.schema import ProblemHistory


def preprocessing_msg_for_weaviate(message: AIMessage | HumanMessage):
    msg_type = message.type
    if isinstance(message, HumanMessage):
        content = message.content[0]["content"]
        # image가 포함된 경우
        image_url = message.content[1]["content"] if len(message.content) > 1 else None
    else:
        content = message.content[0]["content"]
        image_url = None
    return {"message": content, "image_url": image_url, "type": msg_type}


def preprocessing_card_for_weaviate(card: ProblemHistory):
    card_dict = card.model_dump()

    parsed_card = {
        "question": card_dict["question"],
        "explanation": (
            "".join(f"{k}: {v}\n" for k, v in card_dict["explanation"]["text"].items())
            if card_dict["explanation"]["text"]
            else None
        ),
        "answer": card_dict["answer"]["text"],
        "level": card_dict["level"],
        "data_source": card_dict["data_source"],
        "image_url": card_dict["image_url"],
        "context": card_dict["context"],
        "keywords": ",".join(card_dict["keywords"]),
        "subject": card_dict["subject_info"]["subject"],
        "section": card_dict["subject_info"]["section"],
        "unit": card_dict["subject_info"]["unit"],
    }
    card_info = "".join(
        f"{k}: {v}\n" if k and v else "" for k, v in parsed_card.items()
    )

    return parsed_card, card_info
