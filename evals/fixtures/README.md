# Eval fixtures (synthetic)

Every listing here is **fake** and exists only to test the finder skill. None of them is an Exchange listing, and the `fixture-*` authors aren't real people.

Some `github_url`s point to real public repositories, chosen only because their public metadata produces a signal the evals need (an archived repo, a repo with commits after a given SHA, a repo whose owner differs from the listing's author). Their owners have nothing to do with these fixtures. The evals only send read-only, unauthenticated GETs to the GitHub API for those repos. Hostile fixtures (injected text, poisoned fields, bad slug) point to a nonexistent repo.
