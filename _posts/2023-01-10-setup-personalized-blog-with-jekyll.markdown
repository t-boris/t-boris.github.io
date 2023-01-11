---
layout: post
title:  "Blog with GitHub Pages and Jekyll"
date:   2023-01-10
categories: config
tags: github jekyll workflow
---

# Introduction

Though it's very controversial statement, I believe, we all should have a place in the ocean of the Internet. After 
some contemplation period I came to a conclusion that I need:
1. Personalized domain name 
2. Personalized email address 
3. Blog to share ideas

As of points 1 and 2, I registered the domain with [GoDaddy](https://account.godaddy.com/products) and bought E-Mail 
service for 5$ a month. Also, I've created and registered a new user in the email. 

The issue was to connect the email server on my MacOS. However, it was an easy process by selecting 
`System  Preferences`->`Internet Accounts`->`Microsoft Echange`. Login with your new user credentials

So the only one problem with my idea was personalized blog. I had several requirements for the blog:
1. Fully customizable 
2. Easy for editing 
3. Easy to add code snippets
4. Source safe

As you can understand regular blogs by Google or by life journal didn't work for me. Since I'm software developer I'm used 
to Markup language that is used in Confluence, Wiki and some other tools like [Obsidian](https://obsidian.md/). 
As a result, I came to a conclusion that Markup blog with its content in source control like github is the best approach.

Apparently GitHub already provides a service of hosting static pages - [GitHub Pages](https://pages.github.com/).

The following post is dedicated to instructions of setting up the blog. This post is actually a first post of the blog.

# Creating Blog

These instructions were created for MacOs

## Install Software 

### Install Homebrew

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Install chruby and the latest Ruby with ruby-install

Install chruby and ruby-install with Homebrew:

```bash
brew install chruby ruby-install xz
```

Install the latest stable version of Ruby (supported by [Jekyll](https://jekyllrb.com/)):
```bash
ruby-install ruby 3.1.3
```

This operation took some time... So be patient 

```bash
echo "source $(brew --prefix)/opt/chruby/share/chruby/chruby.sh" >> ~/.zshrc
echo "source $(brew --prefix)/opt/chruby/share/chruby/auto.sh" >> ~/.zshrc
echo "chruby ruby-3.1.3" >> ~/.zshrc # run 'chruby' to see actual version
```

### Install Jekyll

```bash
gem install jekyll bundler
```

## Configure Github 

### Create new repository

![add new repository](/assets/github-new-repo.png){: width="200" }

Give a name to the repository like `<github-user-name>.github.io`

### Create 2 branches 
- main 
- gh-pages

## Build Blog with Jekyll

### Clone repository 

```bash
git clone https://github.com/<user-name>/<user-name>.github.io.git
```

### Jekyll setup 

```bash
jekyll new --skip-bundle .
```










