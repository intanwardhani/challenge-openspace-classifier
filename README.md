# Let's assign seats randomly!

![](https://img.shields.io/badge/Python-14354C?style=flat&logo=python&logoColor=white) ![](https://img.shields.io/badge/Markdown-000000?style=flat&logo=markdown&logoColor=white) ![](https://img.shields.io/badge/macOS-000000?style=flat&logo=apple&logoColor=white)

# The Programme  
Imagine a conference room filled with tables and each table has a number of seats. Now imagine some people are going to this conference and we want to assign a seat to each of them randomly. How do we do that?  
  
Luckily you don't have to deal with it manually, because it is what the _this_ programme does! It even goes so far as to renew the assignment every time you run the programme.  
  
# The Main Features
The programme...  
✦ takes a filepath as an argument to load the names of the people.  
✦ distributes the people to existing tables and returns how many seats are left.  
✦ deals with the possibility of having too many people in the room.  
  
# The Extra Features  
The programme...  
✪ allows the possibility to define the room setup from a config.json file.  
✪ allows the possibility to change dynamically the setup and re-run the program.  
✪ is dynamic and interactive so you can add a new person in the room and add a table if all tables are occupied.  
    ⇒ the function tries to balance the table's size if a new table is added. For example, if there are 20 people and 4 tables = 5 people per table, the new arrangement with an extra table will be 20 people and 5 tables = 4 people per table. This function also supports balancing odd numbers.
✪ rearranges the seating in case someone is alone at a table.  
✪ recognises preferences such as "I (don't) want to be seated with this person at the table!"  
    ⇒ this function uses a full two-way clustering. For example, Aleksei → Brigi + Imran and Imran → Jens. The final seating will be: Aleksei, Brigi, Imran, and Jens on the same table.  
    ⇒ the "don't want" preference overrides the "want" preference by minimally removing the violating edge. For example, Aleksei → Brigi + Imran, Imran → Jens, but Aleksei ↛ Jens. The final seating will be: Aleksei + Brigi on one table, Imran + Jens on another table. 
    ⇒ people without preferences are treated as single-person clusters.
✪ gives answers to questions:  
  - How many seats are there in the room?  
  - How many people are there in the room?  
  - How many seats are free?

# Project Structure

```markdown
openspace-organisr
├── LICENSE
├── README.md
├── config.json
├── main.py
├── people.csv
├── seating.csv
└── src
    ├── openspace.py
    ├── table.py
    └── utils.py
```





