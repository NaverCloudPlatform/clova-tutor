# CLOVA Tutor
# Copyright (c) 2026-present NAVER Cloud Corp.
# MIT

from assistant.src.utils.load_utils import load_content_template


def generate_voca_basic_markdown(source: dict, template: dict) -> str:
    row_template = template["row"]

    curr_row = ""
    for definition in source["definitions"]:
        curr_row += row_template.format(
            definition=definition["definition"],
            part_of_speech=definition["part_of_speech"],
            example=definition["example"],
            interpretation=definition["interpretation"],
        )
    return template["template"].format(
        voca=source["word"], pronunciation=source["pronunciation"], rows=curr_row
    )


def generate_voca_synonym_markdown(source: dict, template: dict) -> str:
    row_template = template["row"]

    synonym_row = ""
    for definition in source["definitions"]:
        for synonym in definition["synonyms"]:
            synonym_row += row_template.format(
                voca=synonym["synonym"],
                definition=synonym["definition"],
                example=synonym["example"],
                interpretation=synonym["interpretation"],
            )
    if synonym_row:
        synonym_table = template["template"].format(
            voca=source["word"], synonym_rows=synonym_row
        )
        return synonym_table
    else:
        return ""


def generate_voca_antonym_markdown(source: dict, template: dict) -> str:
    row_template = template["row"]

    antonym_row = ""
    for definition in source["definitions"]:
        for antonym in definition["antonyms"]:
            antonym_row += row_template.format(
                voca=antonym["antonym"],
                definition=antonym["definition"],
                example=antonym["example"],
                interpretation=antonym["interpretation"],
            )
    if antonym_row:
        antonym_table = template["template"].format(
            voca=source["word"], antonym_rows=antonym_row
        )
        return antonym_table
    else:
        return ""


def generate_voca_origin_markdown(source: dict, template: dict) -> str:
    morpheme_table_template = template["morpheme_table"]
    row_template = template["morpheme_row"]

    morpheme_rows = ""
    if source["morphemes"]:
        for morpheme in source["morphemes"]:
            synonym = morpheme.get("synonym", "")
            if synonym == "None":
                synonym = "-"
            morpheme_rows += row_template.format(
                voca=morpheme["morpheme"],
                type=morpheme["type"],
                definition=morpheme["definition"],
                synonyms=synonym,
            )
    if morpheme_rows:
        morpheme_table = morpheme_table_template.format(
            voca=source["word"], morpheme_rows=morpheme_rows
        )
    else:
        morpheme_table = ""

    definitions = [
        f"{i+1}. {definition['definition']}"
        for i, definition in enumerate(source["definitions"])
    ]
    definitions = "\n".join(definitions)
    return (
        template["template"]
        .format(
            voca=source["word"],
            definitions=definitions,
            origin=source["origin"],
            morpheme_table=morpheme_table,
        )
        .strip("\n")
    )


def generate_voca_inflection_markdown(source: dict, template: dict) -> str:
    row_template = template["row"]

    curr_row = ""
    if source["inflections"]:
        for inflection in source["inflections"]:
            for _inflection in inflection["inflections"]:
                curr_row += row_template.format(
                    type=_inflection["type"],
                    voca=_inflection["inflection"],
                    example=_inflection["example"],
                    interpretation=_inflection["interpretation"],
                )
        return template["template"].format(voca=source["word"], rows=curr_row)
    else:
        return ""


def generate_voca_idiom_markdown(source: dict, template: dict) -> str:
    row_template = template["row"]

    curr_row = ""
    if source["idioms"]:
        for idiom in source["idioms"]:
            curr_row += row_template.format(
                idiom=idiom["idiom"],
                definition=idiom["definition"],
                example=idiom["example"],
                interpretation=idiom["interpretation"],
            )
        return template["template"].format(voca=source["word"], rows=curr_row)
    else:
        return ""


def generate_markdown(source: dict, content_type: str, subject: str = "영어") -> str:
    """
    Generates a markdown string from a source dictionary and a template.

    Args:
        source (dict): The source dictionary containing the data to be formatted.
        content_type (str): The type of content to be generated (e.g., "voca_basic").
        subject (str): The subject for which the markdown is being generated.

    Returns:
        str: The generated markdown string.
    """
    # get markdown template
    if subject == "영어":
        template = load_content_template("eng").get(content_type, "")
    else:
        raise ValueError(f"Unsupported subject: {subject}")

    if not template:
        raise ValueError(f"Template for content type '{content_type}' not found.")

    if content_type == "voca_basic":
        return generate_voca_basic_markdown(source, template)
    elif content_type == "voca_synonym":
        return generate_voca_synonym_markdown(source, template)
    elif content_type == "voca_antonym":
        return generate_voca_antonym_markdown(source, template)
    elif content_type == "voca_origin":
        return generate_voca_origin_markdown(source, template)
    elif content_type == "voca_inflection":
        return generate_voca_inflection_markdown(source, template)
    elif content_type == "voca_idiom":
        return generate_voca_idiom_markdown(source, template)
    else:
        raise ValueError(f"Unsupported content type: {content_type}.")
