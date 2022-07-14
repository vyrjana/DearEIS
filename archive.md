---
layout: default
title: "Archive"
---

## Archive

<ul>
  {% for post in site.posts %}
    <li>
      <a href="{{ site.baseurl }}{{ post.url }}">{{ post.title }} ({{ post.date | date: "%Y-%m-%d" }})</a>
    </li>
  {% endfor %}
</ul>
