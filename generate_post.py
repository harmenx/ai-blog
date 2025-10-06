import os
import sys
import datetime
import requests
import re

from openai import OpenAI

def generate_post_content(topic, poe_api_key):
    prompt = f"""
Please generate a blog post about "{topic}". The post should be well-structured, informative, and engaging.

Here is the desired structure:

- **Title:** A catchy and descriptive title for the blog post.
- **Introduction:** A brief introduction to the topic, grabbing the reader's attention.
- **Main Content:** A detailed exploration of the topic, with clear headings and subheadings.
- **Conclusion:** A summary of the key points and a call to action.

Please make sure the content is original and not plagiarized.
"""

    client = OpenAI(
        api_key=os.getenv("POE_API_KEY"),
        base_url="https://api.poe.com/v1"
    )
    
    completion = client.chat.completions.create(
        model="claude-3-opus", 
        messages=[{"role": "user", "content": prompt}],
        max_tokens=2048,
    )

    return completion.choices[0].message.content

def create_jekyll_post(topic, content):
    title = topic.replace("-", " ").title()
    seo_description = f"A blog post about {topic}."
    categories = ["AI Tools"]
    tags = ["AI"]
    author = "Gemini"
    featured_image = "/assets/images/default.jpg"

    # Generate filename
    today = datetime.datetime.now()
    filename_date = today.strftime("%Y-%m-%d")
    filename_title = title.lower().replace(" ", "-").replace(":", "").replace(",", "").replace("'", "")
    filename = f"{filename_date}-{filename_title}.md"

    # Construct front matter
    front_matter = f"""
---
layout: post
title: \"{title}\" 
date: {today.strftime("%Y-%m-%d %H:%M:%S %z")}
categories: {categories}
tags: {tags}
author: {author}
featured_image: {featured_image}
seo_title: \"{title}\" 
description: \"{seo_description}\" 
---

"""
    return filename, front_matter + content

def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_post.py \"Your Blog Post Topic\"")
        sys.exit(1)

    blog_topic = sys.argv[1]
    poe_api_key = os.getenv("POE_API_KEY")

    if not poe_api_key:
        print("Error: POE_API_KEY environment variable not set.")
        sys.exit(1)

    print(f"Generating post for topic: {blog_topic}")
    try:
        generated_content = generate_post_content(blog_topic, poe_api_key)
        filename, full_content = create_jekyll_post(blog_topic, generated_content)

        posts_dir = "_posts"
        os.makedirs(posts_dir, exist_ok=True)
        filepath = os.path.join(posts_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(full_content)
        print(f"Successfully created post: {filepath}")
    except requests.exceptions.RequestException as e:
        print(f"Error communicating with Poe API: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
