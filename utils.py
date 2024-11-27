import requests
from openai import OpenAI


def get_image_summary(base64_image, filters, api_key):
    client = OpenAI(
        api_key=api_key,
    )

    filters_prompt = ""
    if len(filters):
        filters_prompt = "The following filters were applied: "
        for key, values in filters.items():
            # Convert the list of values to a comma-separated string
            values_str = ", ".join(str(value) for value in values)
            filters_prompt += f"{key} in [{values_str}]; "  # Adding square brackets for clarity

    # Optional: Remove the trailing semicolon and space
    filters_prompt = filters_prompt.rstrip("; ")
    print(filters_prompt)

    response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
        "role": "user",
        "content": [
            {
            "type": "text",
            "text": "Summarise the most important points and any trend in atmost 50 words.",
            },
            {
            "type": "image_url",
            "image_url": {
                "url":  f"data:image/jpeg;base64,{base64_image}"
            },
            },
        ],
        }
    ],
    )

    print(response.choices[0])
    return response.choices[0].message.content

def get_path_summary(node_summary, filters, api_key):
    prompt = "We did an analysis on our data with multiple viz. "
    for i in range(len(node_summary)):
        prompt += f"Summary of first node: {node_summary[i]}."
        if (len(filters[i])):
            filters_prompt = "The following filters were applied: "
            for key in filters[i]:
                values_str = ", ".join(str(value) for value in filters[i][key])
                filters_prompt += f"{key} in [{values_str}]; "
            filters_prompt = filters_prompt.rstrip("; ")  # Remove trailing characters
            filters_prompt += ". "
            prompt += filters_prompt
    
    prompt += " Summarise the analysis."
    print(prompt)

    client = OpenAI(
        api_key=api_key,
    )
    response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": prompt,
            }
        ],
        }
    ],
    )

    print(response.choices[0])
    return response.choices[0].message.content


def fetch_answer_png(node, bearer_token, answer_fetch_url):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {bearer_token}',
    }
    data = {
        "metadata_identifier": node.data['lbId'],
        "file_format": "PNG",
        "visualization_identifiers": [node.data['vizId']]
    }
    response = requests.post(answer_fetch_url, headers=headers, json=data)

    # Check the response
    if response.status_code == 200:
        return response.content
    else:
        print("Error:", response.status_code, response.text)


def merge_filters(parent_filters, child_filters):
    merged_filters = child_filters.copy()
    
    for parent_key, parent_values in parent_filters.items():
        if parent_key in merged_filters:
            # If key exists in both parent and child, merge unique values
            merged_filters[parent_key] = list(set(merged_filters[parent_key] + parent_values))
        else:
            # If key only exists in parent, add it to child filters
            merged_filters[parent_key] = parent_values
    
    return merged_filters