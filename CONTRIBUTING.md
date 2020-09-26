# How to contribute

Welcome! Happy to see you willing to make the project better.
Bug reports and pull requests from users are what keep this project working.


## Development Environment

### Pre commit hook

It is important to install [pre-commit](https://pre-commit.com) and pre commit
hook to ensure all code run against `black` and `flake8` before committing it 
and pushing to remote.

To install `pre-commit`, run below,

```bash
pip install pre-commit==2.2.0
```

After `pre-commit` installed in your system, please run below command to setup pre-commit hook.

```bash
pre-commit install
```

Now, your environment is ready and whenever you commit, `pre-commit` automatically trigger.


## Basics

1. Create an issue and describe your idea
1. [Fork it](https://github.com/amrit3701/FreeCAD-Reinforcement/fork)
1. Create your feature branch (`git checkout -b my-new-feature`)
1. Commit your changes (`git commit`) with [well-written](https://chris.beams.io/posts/git-commit) commit message.
1. Publish the branch (`git push origin my-new-feature`)
1. Create a new Pull Request


## Write documentation

Make sure to update the [README.md](https://github.com/amrit3701/FreeCAD-Reinforcement/blob/master/README.md) and [Wiki](https://wiki.freecadweb.org/Reinforcement_Workbench) with the features added or changed once the PR is merged.


## Finally

Thanks again for your interest in improving the project! You're taking action when most
people decide to sit and watch.