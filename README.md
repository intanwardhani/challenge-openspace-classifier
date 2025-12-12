# Let's assign seats randomly!

![](https://img.shields.io/badge/Python-14354C?style=flat&logo=python&logoColor=white) ![](https://img.shields.io/badge/Markdown-000000?style=flat&logo=markdown&logoColor=white) ![](https://img.shields.io/badge/macOS-000000?style=flat&logo=apple&logoColor=white)

# The Programme  
Imagine a conference room filled with tables and each table has a number of seats. Now imagine some people are going to this conference and we want to assign a seat to each of them randomly. How do we do that?  
  
Luckily you don't have to deal with it manually, because it is what the _this_ programme does! It even goes so far as to renew the assignment every time you run the programme.  
  
# The Main Features  
📥 The programme takes a filepath as an argument to load the names of the people.  
🪑 The programme distributes the people to existing tables and returns how many seats are left.  
🧮 The programme deals with the possibility of having too many people in the room.  
  
# The Extra Features  
The programme...  
📝 allows the possibility to define the room setup from a config.json file  
🚁 allows the possibility to change dynamically the setup and re-run the program  
👯‍♀️ is dynamic and interactive so you can add a new person in the room and add a table if all tables are occupied  
🤹🏽 rearranges the seating in case someone is alone at a table  
📮 recognises requests such as "I (don't) want to be seated with this person at the table!"  
🗝️ gives answers to questions:  
  - How many seats are there in the room?  
  - How many people are there in the room?  
  - How many seats are free?

# Project Structure

```markdown
openspace-organisr
├── LICENSE
├── README.md
├── config.json
├── dev_notebook.ipynb
├── main.py
├── people.csv
├── seating.csv
└── src
    ├── __pycache__
    │   └── table.cpython-313.pyc
    ├── openspace.py
    ├── table.py
    └── utils.py
```





