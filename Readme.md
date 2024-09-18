dependency:
- mkdocs = 1.6.1
- mkdocs-material = 1.16.0

In order to deploy the documentation to Github Pages, 
you need to generate a public key (e.g. via fork) and add it to your account. 
See [Github Docs](https://docs.github.com/en/github/authenticating-to-github/connecting-to-github-with-ssh) for more information.

And it is necessary to add a config file to your account folder/.ssh:

```bash
Host github.com
  IdentityFile ~/.ssh/id_rsa
```

Change the `~/.ssh/id_rsa` to your own public key path and name.
