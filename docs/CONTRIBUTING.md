Contributing to Ansible Agnostic Deployer
================

If you're reading this, hopefully you are considering helping out with the Ansible Agnostic Deployer for Red Hat enablement.

Herein lies the contribution guidelines for helping out with this project. Do take the guidelines here literally, if you find issue with any of them or you see room for improvement, please let us know via a GitHub issue.

## Rules ##

* The Ansible [Code of Conduct][coc] still applies.
* For git messages, branch names, ..., follow [Git Style Guide][gitstyle].
* Should you wish to work on a completely new standard, GREAT, but please file an issue for tracking.
* To contribute, fork and make a pull request against the `development` branch.
* All tasks should be in YAML literal.

```yml
# This
- name: Create a directory
  file:
      state: directory
      path: /tmp/deletethis

# Not this
- name: Create a directory
  file: state=directory path=/tmpt/deletethis
```

* There should be no space before a task hyphen

```yml
# This
- name: Do something

# Not this
   - name: Do something
```

* Module arguments should be indented two spaces

```yml
# This
- name: Create a directory
  file:
    state: directory
    path: /tmp/deletethis

# Not This
- name: Create a directory
  file:
      state: directory
      path: /tmp/deletethis
```

* There should be a single line break between tasks
* Tags should be in multi-line format and indented two spaces just like module arguments above

```yml
# This
- name: "Check hosts.equiv"
  stat:
    path: /etc/hosts.equiv
  register: hosts_equiv_audit
  always_run: yes
  tags:
    - tag1
    - tag2


# Not This
- name: "Check hosts.equiv"
  stat:
      path: /etc/hosts.equiv
  register: hosts_equiv_audit
  always_run: yes
  tags: [tag1,tag2]
```

* Every task must be named and provide brief descriptions about the task being accomplished.

### Git ###
Please follow [Git style guide][gitstyle].

Note: during the review process, you may add new commits to address review comments or change existing commits. However, before getting your PR merged, please squash commits to a minimum set of meaningful commits.

If you've broken your work up into a set of sequential changes and each commit pass the tests on their own then that's fine. If you've got commits fixing typos or other problems introduced by previous commits in the same PR, then those should be squashed before merging.

If you are new to Git, these links might help:

* https://git-scm.com/book/en/v2/Git-Tools-Rewriting-History
* http://gitready.com/advanced/2009/02/10/squashing-commits-with-rebase.html

[coc]:http://docs.ansible.com/ansible/community.html#community-code-of-conduct
[gitstyle]:https://github.com/agis/git-style-guide
