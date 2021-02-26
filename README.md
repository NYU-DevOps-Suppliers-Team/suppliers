# suppliers
NYU DevOps Suppliers Team

## Run project

This repo has a Vagrantfile so the easiest way to play with it is to:

```
vagrant up
vagrant ssh
cd /vagrant
```

## Working with branches

1. Make sure you have the latest changes form master

```
git checkout master  // this will get you to the master branch is case you are not there
git pull             // this will bring the latest changes from master to your local environment
```

2. Create a BRANCH to work on your ISSUE

Everytime we work on the project we need to create a new branch.

```
git checkout -b branch-name
```

The branch name should be related to the issue
TBD: branch convention name

3. COMMIT changes to that branch

```
git add
git commit -m "[branch-name] Description of what your commit is doing"
```
TBD: commit convention.

4. PUSH your changes to the Remote branch

```
git checkout master // we need to make sure our branch has the latest changes
git pull

git checkout branch-name
git merge master    // once we pull in master we merge those changes to out branch
// you may have MERGE CONFLICTS, in that case you need to solve them and commit again
git push -u origin branch-name
```

5. Issue a PULL REQUEST to have your work reviewed
6. MERGE your code to master and close the ISSUE

