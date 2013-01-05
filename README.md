
# PyLMTH - HTML Markup Backwards, in Python

## Why?

1. I wanted to make a Python module.
2. I like Python and CoffeeScript, and I indent my HTML anyway, so why not get rid of all the other crap?
3. Selectors are wonderful; let's use those (except bracket notation for attributes, because who needs brackets?).
4. The side carets aren't all bad; let's throw them in there for something, at least!

## What are you talking about?

Before:

```
`<!DOCTYPE html>`
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
      form enctype=multipart/formdata
        -input type=text readonly=

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
      <form enctype="multipart/formdata">
        <input type="text" readonly="" />
      </form>
    </div>
  </body>
</html>
```