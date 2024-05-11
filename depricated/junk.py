@DeprecationWarning
def open_ai_res():
    response = OpenAI().chat.completions.create(
    model=model_open,
    messages=[
        {"role": "user", "content": question},
        ]
    )

    return response.choices[0].message.content