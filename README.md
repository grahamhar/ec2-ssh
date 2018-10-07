# ssh-ec2
Make ssh to EC2 instances easier

Install:

```
pip install ssh-ec2
```

Setup:
 
Add the following to your shell rc (.bashrc, .bash_profile, .zshrc):

```
#compdef ssh_ec2
_ssh_ec2() {
  eval $(env COMMANDLINE="${words[1,$CURRENT]}" _SSH_EC2_COMPLETE=complete-zsh  ssh_ec2)
}
if [[ "$(basename -- ${(%):-%x})" != "_ssh_ec2" ]]; then
  autoload -U compinit && compinit
  compdef _ssh_ec2 ssh_ec2
fi
```

Example Usage:

```
ssh_ec2 select [TAG NAME] [TAG VALUE] [IP ADDRESS|all|random]

Usage: ssh_ec2 [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  select
```

Tab completion for all commands and arguments. If you don't need a specific IP then use random to select one of the hosts at random or all to go to each host in turn.

Note:

If tag names have a `:` in them they are replaced with `_COLON_` this is due to zsh treating text after a colon as help text
