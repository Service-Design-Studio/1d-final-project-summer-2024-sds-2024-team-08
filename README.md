[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-24ddc0f5d75046c5622901739e7c5dd533143b0c8e959d652212380cedb1ea36.svg)](https://classroom.github.com/a/QpCtzJAE)
[![Open in Visual Studio Code](https://classroom.github.com/assets/open-in-vscode-718a45dd9cf7e7f842a935f5ebbe5719a5e09af4491e668f4dbf3b35d5cca122.svg)](https://classroom.github.com/online_ide?assignment_repo_id=15048531&assignment_repo_type=AssignmentRepo)
will remove links later 

<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>

# Global Infleunce Insight: Natural Language Business Intelligence Assistant 
This project was done in collaboration with The Stakeholder Company (TSC). Using data scraped from the internet or bought through various sources, we are able to leverage the power of LLMs (notably Google Gemini) to provide powerful insights from our data. 

<img src="https://cdn.prod.website-files.com/642e4d2d40f4d8ae99d811e1/642e51bd6932b7e24ff238a0_TSC%20logo.svg" loading="lazy" alt="TSC Ai" class="logo">

## Features 
* Store different chat for different users 
* Have chat history for each chat 
* Draw network graphs that connect different stakeholders 
* Draw insights from media and piece together connections 

## UX Design 
We made the interface similar to the familiar ChatGPT that everyone knows as familiar designs are more likely to be easily understood and navigated by the user. Since we are making something similar to a chatbot, we want the users to quickly understand that. 

## Problem Statement 


## Project Architecture 
Insert architecture diagram here eg (rails - python - gemini)

![Ruby](https://img.shields.io/badge/Ruby-CC342D.svg?logo=ruby&logoColor=white)
![Python](https://img.shields.io/badge/Python-14354C.svg?logo=python&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-323330.svg?logo=javascript&logoColor=F7DF1E)
![HTML5](https://img.shields.io/badge/HTML5-E34F26.svg?logo=html5&logoColor=white)
![CSS](https://img.shields.io/badge/CSS-239120.svg?logo=css3&logoColor=white)

The main web page is served by a Ruby on Rails server, while all the processing is done on a separate server written in Python. For the rest of the Readme, we will use the terms Rails server and Python server. 

Due to the heavy emphasis on AI, we choose to use LangChain and LangGraph to simplify our process. Both LangChain and LangGraph are primarily written in Python, with minimal support written in Ruby. Therefore, we chose to take advantage of these 2 libraries and write our main AI processing server in Python. The Python server then provides an API endpoint with FastAPI for the Rails server to interact with. 

### LangGraph 
[LangGraph](https://langchain-ai.github.io/langgraph/) is a library for building stateful, multi-actor applications with LLMs, used to create agent and multi-agent workflows.

### Ruby on Rails
[Rails](https://guides.rubyonrails.org/getting_started.html) is a web application development framework written in the Ruby programming language. It is designed to make programming web applications easier by making assumptions about what every developer needs to get started.

Rails is opinionated software. It makes the assumption that there is a "best" way to do things, and it's designed to encourage that way - and in some cases to discourage alternatives.

# Demo 
Insert youtube demo here 

# Getting Started 
This project requires both Ruby, with Ruby on Rails and Python to work. 

Clone the repo and open 2 separate terminal windows, one for the Rails server and one for the Python server. 

Install all dependencies for Rails. Please change the path according to where you cloned the repo. 
```sh
bundle install --gemfile /path_to_repo/1d-final-project-summer-2024-sds-2024-team-08/rails-server/Gemfile
```

Start Rails server
```sh
rails s 
```

(Optional) If develop Rails locally with Postgres database in cloud, download cloud SQL proxy to allow Rails to connect to the cloud db. Follow this guide [here](https://cloud.google.com/sql/docs/mysql/sql-proxy). Run the cloud sql proxy in another terminal at the same time as ```rails s```

It would be advisable to use a [virtual environment](https://docs.python.org/3/library/venv.html) for the packages required in the Python server to prevent messing up system packages and versions. 

Create a venv for Python packages 
```sh
python3 -m venv .venv  
```

Activate the venv, command depends on OS. 
|Shell|Command to activate venv|
|--|--|
|POSIX bash/zsh |```source  venv/bin/activate``` |
|Windows cmd.exe|```venv\Scripts\activate.bat```|

Install all dependencies for Python server
```sh
python3 -m venv .venv  
```

Start Python server 

how??

### Postgres Database 
We are using a Postgres database for both development and production. The production version is set up on Google Cloud, see below for more details. 

HOW TO SET UP??? 

# Deployment 
![Google Cloud](https://img.shields.io/badge/Google%20Cloud-4285F4?logo=google-cloud&logoColor=white)
![postgres](https://img.shields.io/badge/postgres-316192.svg?logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)


# Testing 
![Cucumber](https://img.shields.io/badge/Cucumber-43B02A?style=for-the-badge&logo=cucumber&logoColor=white)

## Rails Server 
Run the tests

```sh
bundle exec cucumber 
```

## Python Server 

