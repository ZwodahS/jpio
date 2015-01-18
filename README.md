
# JPIO + JsTQL
Json Python IO or JPIO is a simple Json reader/writer written in python that can be used in the command line.
It uses JsTQL, a simple Json Transformation and Query Language that is created just for this purpose.

JsTQL can be imported in any python program and it contains a parser and a runtime.
JPIO is simply a wrapper around it.

# Usage
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
            "name" : "That guy that made Json"
        },
        {   
            "name" : "That guy that created Python"
        },
        {
            "name" : "ZwodahS"
        }
    ]
}
```
## Query
To query a single element, for example version
```
> cat sample/books.json | jpio '.version'
output:
{"patch": 0, "minor": 0, "major": 1}
> cat sample/books.json | jpio '.version.major'
output:
1
```

To get all the books in a list or partial list
```
> cat sample/books.json | jpio '.books'
[{"isbn": "M19165029", "author": "1", "name": "Introduction to Json"}, {"isbn": "M35123115", "author": "2", "name": "Introduction to Python"}, {"isbn": "M51236131", "author": "3", "name": "Crazy JPIO"}]
> cat sample/books.json | jpio '.books.[:2]'
[{"author": "1", "name": "Introduction to Json", "isbn": "M19165029"}, {"author": "2", "name": "Introduction to Python", "isbn": "M35123115"}]
```

To get all the authors value 
```
> cat sample/books.json | jpio '.books.[*].author'
["1", "2", "3"]
```

Or split the list into lines
```
> cat sample/books.json | jpio -s '.books.[*].author'
1
2
3
```

Set the value of each books collection
```
> cat sample/books.json | jpio '.books.[*].price=30'
output:
{"books": [{"author": "1", "price": 30, "name": "Introduction to Json", "isbn": "M19165029"}, {"author": "2", "price": 30, "name": "Introduction to Python", "isbn": "M35123115"}, {"author": "3", "price": 30, "name": "Crazy JPIO", "isbn": "M51236131"}], "version": {"minor": 0, "patch": 0, "major": 1}, "authors": [{"name": "That guy that made Json"}, {"name": "That guy that created Python"}, {"name": "ZwodahS"}]}
```

## Planned Feature ??

### Statement as selector
```
> cat sample/books.json | jpio '.books.[*].author=(.$root.authors.[(.author)])'
```
This should denormalize the data and store the author dict in the books.

### Functions
Several functions will be implemented, like upper, lower for string, sort, pop for list, delete for dict etc.

### String intepolation
Need not say more

