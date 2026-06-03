import json
import os

import daily_longform_upload as base


_generate_gemini = base.generate_gemini
_generate_openai = base.generate_openai

_TOPIC_PROMPT_USER = (
    "Create one fresh Korean YouTube longform general health explainer topic as strict JSON. "
    "Avoid every used topic. The tone should be calm, informative, practical, and suitable for a Korean audience. "
    "Choose a concrete general health subject about prevention, body mechanisms, infection routes, lifestyle risk, or early warning signs. "
    "Do not provide personalized medical diagnosis, treatment instructions, medication dosing, emergency instructions, celebrity topics, politics, or sensational fear content. "
    "The topic must naturally support 17 different visual scenes, including anatomical cutaways, affected organs, viruses, bacteria, inflammation, blood vessels, or lifestyle prevention actions. "
    "Fields required: id, topic, title, description, tags, subject, problem, solution, example. "
    "description must include two short paragraphs, one sentence reminding viewers to consult a clinician for symptoms or personal care, and 5 Korean hashtags. "
    "tags must be a list of 5 to 7 Korean strings. "
    "subject must be an English visual prompt for realistic Korean medical documentary imagery, with a visible organ, virus, affected body area, or prevention action. "
    "problem, solution, and example must be concise Korean phrases using standard Korean spelling. "
    "example must describe a concrete Korean real-life situation and must not include English. "
    "Do not use slang, intentionally misspelled Korean, or unclear abbreviations.\n\n"
    "Used topics:\n{used_topics}"
)


def generate_gemini_with_fallback(prompt, path):
    try:
        _generate_gemini(prompt, path)
        if not path.exists() or path.stat().st_size == 0:
            raise RuntimeError("Gemini returned an empty image")
    except Exception as exc:
        print(f"Gemini image generation failed; falling back to OpenAI: {exc}")
        _generate_openai(prompt, path)


def generate_openai_with_fallback(prompt, path):
    try:
        _generate_openai(prompt, path)
    except Exception as exc:
        print(f"OpenAI image generation failed; falling back to Gemini: {exc}")
        _generate_gemini(prompt, path)


def _parse_and_validate_topic(raw, used_topics):
    text = raw.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    topic = json.loads(text)
    required = {"id", "topic", "title", "description", "tags", "subject", "problem", "solution", "example"}
    missing = sorted(required - set(topic))
    if missing:
        raise RuntimeError(f"Generated topic is missing fields: {missing}")
    if topic["topic"] in used_topics:
        raise RuntimeError("Generated topic duplicated a used topic")
    return topic


def _generate_topic_openai(used_topics):
    client = base.OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    response = client.chat.completions.create(
        model=os.getenv("OPENAI_TEXT_MODEL", "gpt-4o-mini"),
        messages=[
            {
                "role": "system",
                "content": "You return only valid JSON. Do not include markdown fences or commentary.",
            },
            {
                "role": "user",
                "content": _TOPIC_PROMPT_USER.format(
                    used_topics=json.dumps(used_topics, ensure_ascii=False)
                ),
            },
        ],
        temperature=0.85,
    )
    return _parse_and_validate_topic(response.choices[0].message.content, used_topics)


def _generate_topic_gemini(used_topics):
    from google import genai

    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY") or os.environ["GOOGLE_API_KEY"]
    )
    prompt = (
        "You return only valid JSON. Do not include markdown fences or commentary.\n\n"
        + _TOPIC_PROMPT_USER.format(
            used_topics=json.dumps(used_topics, ensure_ascii=False)
        )
    )
    response = client.models.generate_content(
        model=os.getenv("GEMINI_TEXT_MODEL", "gemini-2.5-flash"),
        contents=prompt,
    )
    return _parse_and_validate_topic(response.text, used_topics)


def generate_topic(history):
    used_topics = [x.get("topic", "") for x in history if x.get("topic")]
    try:
        return _generate_topic_openai(used_topics)
    except Exception as exc:
        print(f"OpenAI topic generation failed; falling back to Gemini: {exc}")
        return _generate_topic_gemini(used_topics)


def pick_topic(history):
    used = {x.get("topic") for x in history}
    for topic in base.TOPICS:
        if topic["topic"] not in used:
            return topic
    return generate_topic(history)


base.pick_topic = pick_topic
base.generate_gemini = generate_gemini_with_fallback
base.generate_openai = generate_openai_with_fallback


if __name__ == "__main__":
    base.main()
