# pet_name_generator

Generate unique hostnames with the python petname libary.

## Requirements
Python Libraries:
  - petname

## Role Variables

`pet_name_generator_lookup`  - Default lookup creates a two word unique system name with a blank separator defined.

`pet_name_generator_instances` - set_fact reads this list and sets a pet_name to each item.

```
pet_name_generator_instances:
  - bastion_hostname
  - node1_hostname
  - node2_hostname
```

License
-------

BSD

Author Information
------------------
Wilson Harris
Red Hat, GPTE