<!--
SPDX-License-Identifier: MIT
Copyright (c) 2020 The Authors.

Authors: Sherif Abdelwahab <@zasherif>
         Phu Tran          <@phudtran>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:The above copyright
notice and this permission notice shall be included in all copies or
substantial portions of the Software.THE SOFTWARE IS PROVIDED "AS IS",
WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE
FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR
THE USE OR OTHER DEALINGS IN THE SOFTWARE.
-->

### Contributor Workflow

Please do not ever hesitate to ask a question or send a pull request.

This is a rough outline of what a contributor's workflow looks like:

- Fork the repository and clone your fork.
```
$ git clone git@github.com:your_username/mizar.git
```
- Add the official mizar repository as an upstream remote.
```
$ git remote add upstream git@github.com:futurewei-cloud/mizar.git
```
- Create a topic branch from where to base the contribution. This is usually master.
```
$ git fetch upstream
$ git checkout upstream/master
$ git checkout -b your_topic_branch_name
$ git push -u origin your_topic_branch_name
```
- Make commits of logical units.
- Make sure commit messages are in the proper format (see below).
- Once ready, rebase with the topic branch, push to your fork, and submit a pull request to [mizar](https://github.com/futurewei-cloud/mizar).
```
$ git fetch upstream
$ git rebase upstream/master
$ git push
```
- The PR must receive approvals from two team members including at least one maintainer.
- If you wish to push commits to an open PR, please make sure to rebase with the upstream topic branch prior to pushing.
```
$ git fetch upstream
$ git rebase upstream/master
$ git push
```

### Directory Organization

We organized the source code as follows:

* src: includes separate modules for the project as follows:
    * src/xdp: XDP programs
    * src/dmn: Transit daemon and userspace APIs
    * src/cli: CLI interface to program the transit daemon
    * src/rpcgen: XDR protocol for interacting with the transit daemon. During compilation, the rpcgen tool populates this directory with generated header and source files.
    * src/include: include directory used by the source or other dependant projects that require linking to the userspace library.
    * src/extern: submodules and external files that we copied from other projects. Make sure to keep the license and copy-rights. **Usually copying the code in such way is for one of the following reasons. Either it is the recommended approach to reuse the code, or we ported the code from the kernel, or it is temporary until we have an appropriate dependency handling.**
* mgmt: includes management plane implementation
* test
    * test/conf: Test scenarios
    * test/ansible: Deployment scripts and playbooks for test scenarios
* tools: management and debugging tools

Each directory includes a module.mk files that are referenced by the main Makefile.

### Commits

It is not enough that we have a header for the commits. The commit
needs to have one paragraph describing what it does.  We shall avoid Multi-pages commit messages as much as possible, but we still understand the needs to do otherwise. The format of commit message is explained below.

### Format of the commit message

We follow a rough convention for commit messages that is designed to answer two questions: what changed and why.
The subject line should feature the what and the body of the commit should describe the why.

```
scripts: add test codes for agent

this add some unit test codes to improve code coverage for agent

Fixes #12
```

The format can be described more formally as follows:

```
<subsystem>: <what changed>
<BLANK LINE>
<why this change was made>
<BLANK LINE>
<footer>
```

The first line is the subject and should be no longer than 70 characters, the second line is always blank, and other lines should be wrapped at 80 characters. This allows the message to be easier to read on GitHub as well as in various git tools.

Note: if your pull request isn't getting enough attention, you can use the reach out on Slack to get help finding reviewers.


### Coding Style

We are following the Linux kernel coding style. The  .clang-format  file concretely defines the coding style.  Please use the clang-format tool to ensure consistency.  Several IDEs support running clang-format on the entire directory.

### Documentation and Design Documents

We rely on [Mizar's Github wiki](https://github.com/futurewei-cloud/Mizar/wiki) for documentation.  Being a git repository ensures that documents and designs are reviewed and facilitate onboarding.

To update the documentation/design, clone the wiki locally https://github.com/futurewei-cloud/Mizar.wiki.git, and create a pull request for your changes and send it to the team for review.

### Versioning

We follow the following versioning structure:
Major.Minor-#.  Stable releases versions must have an even Minor number.

### Issue tracking and filing a bug

We use the included GitHub issues to track progress, scope, priority, and assignment of milestones and software changes.

We love feedback! If you would like to help us improve or wants to file a bug, please create an issue.

### Testing

Mizar includes unit and functional tests. We strive to maintain code test coverage as high as possible, particularly for the userspace part of the code. Unit tests do not cover the XDP programs.

1. When contributing new code, please make sure that:
1. Unit tests cover almost all your code
1. You solve all problems discovered by sanitizers
1. Your code changes reflect in the functional tests.

### Compiling Mizar

Make is used to compile Mizar. Enter the mizar directory and run the command below.

```
$ make
```

* You can now optionally run the unit tests and coverage reports by running the commands below.

```
$ make run_unittests
$ make lcov
```