
# WieldyMarkup - Nicer than HTML

## Why?

1. I wanted to demonstrate how to make a Python module by doing it.
2. I wanted to make something that I could actually use.

## What is it?

Well, it's probably not as good as [Haml](http://haml.info) or [Jade](http://jade-lang.com/), but everyone has to start somewhere. Basically, it's an HTML abstraction markup language. My priorities were as follows, in order:

1. Minimize, absolutely, the amount of stuff that the developer needs to write while retaining 98% of functionality.
2. Use whitespace and CSS selectors, and integrate with Underscore and Mustache templates.

## What are you talking about?

Before:

```
`<!DOCTYPE html>
html lang=en
  head
    title <My Website>
  body
    div#application
      div.navbar
        div.navbar-inner
          a.brand href=# <Title>
          ul.nav
            li.active
              a href=# <Home>
            li
              a href=# <Link>
      form enctype=multipart/form-data
        `<% var d = new Date(); %>
        input type=text readonly= value=`<%= d.getDate() %>` /
        p <`<%= val %>` Lorem ipsum dolor sit amet, consectetur adipisicing elit,
          sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.>
```

After:

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <title>My Website</title>
  </head>
  <body>
    <div id="application">
      <div class="navbar">
        <div class="navbar-inner">
          <a class="brand" href="#">Title</a>
          <ul class="nav">
            <li class="active">
              <a href="#">Home</a>
            </li>
            <li>
              <a href="#">Link</a>
            </li>
          </ul>
        </div>
      </div>
      <form enctype="multipart/form-data">
        <% var d = new Date(); %>
        <input type="text" readonly="" value="<%= d.getDate() %>" />
        <p><%= val %> Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</p>
      </form>
    </div>
  </body>
</html>
```


