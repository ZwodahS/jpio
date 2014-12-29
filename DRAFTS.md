# Drafts

This file list the possible things that I want to do with jpio

```
".input.0.a=i(3)"
".input.0.a=i(3)|.input.0.b=s(hello)"
".input.list#sort|.input.list.0"
".input.list.[*].a=i(3)"
".input.list.[*].a.[*].b=i(3)"
".input.list.[*]#sort"
".input.list.[*]#move.a=.b" # move all .a to .b for all item in .input.list.[*]
{
    "input" : { "list" : [ {"a" : 1} , {"a" : 2}] }
}
to
{
    "input" : { "list" : [ "b" : 1}, {"b" : 2}] }
}
".input=d({})|.input.a=i(3)" # creates a new dict { "a" : 3 }
".input=d({})|#set(s(a), i(3))" # same as above. # useful if say, your key is an int and not stringj
"#sort" # sort the list pass in.
```
