
# Requirement
```
    - python 3
```

# Installation
```
pip3 install jpio
alias jpio='python3 -m jpio'
```
Note: The alias will be fix in the future

# JPIO + JsTQL
Json Python IO or JPIO is a simple Json reader/writer written in python that can be used in the command line.
It uses JsTQL, a simple Json Transformation and Query Language that is created just for this purpose.

JsTQL can be imported in any python program and it contains a parser and a runtime.
JPIO is simply a wrapper around it.

# Simple Usage
## Example Json
```
{
    "version" : {
        "major" : 1,
        "minor" : 0,
        "patch" : 0
    },
    "books" : [
        {
            "name" : "Introduction to Json",
            "isbn" : "M19165029",
            "author" : "1"
        },
        {
            "name" : "Introduction to Python",
            "isbn" : "M35123115",
            "author" : "2"
        },
        {
            "name" : "Crazy JPIO",
            "isbn" : "M51236131",
            "author" : "3"
        }
    ],
    "authors": [
        {
            "id": 1,
            "name" : "That guy that made Json"
        },
        {
            "id": 2,
            "name" : "That guy that created Python"
        },
        {
            "id": 3,
            "name" : "ZwodahS"
        }
    ]
}
```
## Query

### Single Element
```
$ cat sample/books.json | jpio '.version'
output:
{"patch": 0, "minor": 0, "major": 1}
$ cat sample/books.json | jpio '.version.major'
output:
1
```

### List or Partial List
```
$ cat sample/books.json | jpio '.books'
[{"isbn": "M19165029", "author": "1", "name": "Introduction to Json"}, {"isbn": "M35123115", "author": "2", "name": "Introduction to Python"}, {"isbn": "M51236131", "author": "3", "name": "Crazy JPIO"}]
$ cat sample/books.json | jpio '.books.[:2]'
[{"author": "1", "name": "Introduction to Json", "isbn": "M19165029"}, {"author": "2", "name": "Introduction to Python", "isbn": "M35123115"}]
```

### Getting inner values of a list
```
$ cat sample/books.json | jpio '.books.[*].author'
["1", "2", "3"]
```

### Split the list into lines
```
$ cat sample/books.json | jpio -s '.books.[*].author'
1
2
3
```

### Set the value of each books collection
```
$ cat sample/books.json | jpio '.books.[*].price=30'
output:
{
    "books": [
        {"author": "1", "price": 30, "name": "Introduction to Json", "isbn": "M19165029"},
        {"author": "2", "price": 30, "name": "Introduction to Python", "isbn": "M35123115"},
        {"author": "3", "price": 30, "name": "Crazy JPIO", "isbn": "M51236131"}
    ],
    "version": {"minor": 0, "patch": 0, "major": 1},
    "authors": [{"name": "That guy that made Json"}, {"name": "That guy that created Python"}, {"name": "ZwodahS"}]
}
```

### Set the value of a specific item
```
$ cat sample/books.json | jpio '.books.[1].price=30'
{
    "version": { "major": 1, "patch": 0, "minor": 0 },
    "authors": [
        { "name": "That guy that made Json" },
        { "name": "That guy that created Python" },
        { "name": "ZwodahS" }
    ],
    "books": [
        { "author": "1", "name": "Introduction to Json", "isbn": "M19165029" },
        { "author": "2", "name": "Introduction to Python", "price": 30, "isbn": "M35123115" },
        { "author": "3", "name": "Crazy JPIO", "isbn": "M51236131" }
    ]
}
```

## Creating data from scratch

```
$ echo '{}' | jpio '.version=j({"major":1, "minor":0, "patch":0})'
output:
{"version": {"patch": 0, "major": 1, "minor": 0}}

$ echo '{}' | jpio '.values=j([5,4,3,2,1])'
output:
{"values": [5, 4, 3, 2, 1]}
```

## Simple functions

### Sorting a list
```
$ echo '{"values": [5, 4, 3, 2, 1]}' | jpio '.values#sort()'
output:
{"values": [1, 2, 3, 4, 5]}
```

### Sort by key
```
$ echo '{"values": [ {"a":3}, {"a":5}, {"a":1} ]}' | jpio '.values#sort(a)'
output:
{"values": [{"a": 1}, {"a": 3}, {"a": 5}]}
```

### Gettings keys from a dictionary
```
$ echo '{ "values": { "a": 1, "b": 2, "c": 3} }' | jpio '.values#keys()'
or
$ echo '{ "a": 1, "b": 2, "c": 3}' | jpio '#keys()' # if object is at root level
```

## Planned Feature ??

### Using Statement as selector
```
$ cat sample/books.json | jpio '.books.[*].author=(.$root.authors.[(.author)])'
```
This should denormalize the data and store the author dict in the books.

### String intepolation
The ability to construct strings from various data.

### Find and modify
```
$ cat sample/books.json | jpio '.books#find(author=2).price=30'
```

## More Guide
Coming soon ...
