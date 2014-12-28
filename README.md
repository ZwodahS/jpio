
A Simple Json reader/writer for python.

# Usage

## Query
```
.varname to select a element in the dictionary
.int to select an item in the list
.[query] to select part of the list, i.e 3:4, or 3:
.[*].<query> to perform query on the entire list and return the output in a new list
```

## Example
```
{
    "version" : "v0.0.1",
    "input" : [
        {
            "file" : "test1.json",
            "type" : "json",
        },
        {
            "file" : "test2.json",
            "type" : "json",
        },
        {
            "file" : "test3.txt",
            "type" : "text",
        }
    ]
}
```

To get the version
```
cat test.json | jpio '.version'
```

output:
```
v0.0.1
```

To get all file name in a list

```
cat test.json | jpio '.input.[*].file'
```

output:
```
["test.json", "test2.json", "test3.txt"]
```

To print each file name in a new line
```
cat test.json | jpio -s '.input.[*].file'
```

output:
```
test.json
test2.json
test3.txt
```

To only print part of the list
```
cat test.json | jpio -s '.input.[1:].[*].file'
```

output:
```
test2.json
test3.txt
```
