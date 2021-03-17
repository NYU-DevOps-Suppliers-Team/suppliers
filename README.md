# NYU DevOps - Suppliers

### Resource Description
The suppliers resource associates products with the vendor that supplies them to our business. It contains information about the supplier, and a collection of references to the products that they provide.

## API Documentation
### Model

|  Column  |  Type  |
| :----------: | :---------: |
| id | Integer |
| name | String |
| email | String |
| address | String |
| phone_number | String (Optional) |
| product_list | List of Product IDs (Integers) | 

## Dev Resources
### Run project

This repo has a Vagrantfile so the easiest way to play with it is to:


```
vagrant up
vagrant ssh
cd /vagrant
```

To run the tests (Make sure coverage is above 90%)

```
nosetests
```

To run your app

```
  vagrant up
  vagrant ssh
  cd /vagrant
  FLASK_APP=service:app flask run -h 0.0.0.0
```
To shut down vagrant

 ```
 exit
 vagrant halt
```

### Working with branches

1. Make sure you have the latest changes form master

```
git checkout main  // this will get you to the main branch is case you are not there
git pull             // this will bring the latest changes from main to your local environment
```

2. Create a BRANCH to work on your ISSUE

Everytime we work on the project we need to create a new branch.

```
git checkout -b branch-name
```
The branch name should be related to the issue: ISSUE_NUMBER-xxx

3. COMMIT changes to that branch

```
git add
git commit -m "[branch-name] Description of what your commit is doing"
```

4. PUSH your changes to the Remote branch

```
git checkout main // we need to make sure our branch has the latest changes
git pull

git checkout branch-name
git merge main    // once we pull in master we merge those changes to out branch
// you may have MERGE CONFLICTS, in that case you need to solve them and commit again
git push -u origin branch-name
```

5. Issue a PULL REQUEST to have your work reviewed and associate your pull request to your issue

7. MERGE your code to main and close the ISSUE

