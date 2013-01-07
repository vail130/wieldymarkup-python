
# WieldyMarkup - Nicer than HTML

## tl;dr

WieldyMarkup is an HTML abstraction markup language, similar in many ways to [Haml](http://haml.info) and [Jade](http://jade-lang.com/). However, WieldyMarkup is meant to be part of the build & deploy process, not the page serving process. It's probably best for writing static HTML pages and Underscore / jQuery / Mustache templates.

## Usage

### Nested HTML

```shell
python /path/to/wieldymarkup /path/to/text_file_1.txt /path/to/text_file_2.txt
```

### Compressed HTML

```shell
python /path/to/wieldymarkup -c /path/to/text_file_1.txt /path/to/text_file_2.txt
```

## Indicative Example

### WieldyMarkup:

```
`<!DOCTYPE html>
html lang=en
  head
    title <My Website>
  body
    #application
      .navbar
        .navbar-inner
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

### Corresponding HTML Output:

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

## Guide

There are four parts to each line of WieldyMarkup:

1. Leading whitespace
2. Selector
3. Attributes
4. InnerText or self-closing designation

### Leading Whitespace

Each line's Leading whitespace is used to detect it's nesting level. Use either tabs or spaces for indentation, but not both. The number of tabs or spaces that comprises an indentation is determined on the first line with any leading tabs or spaces, and then that is the standard used for the rest of the file.

### Selector

Tag designations are modelled after CSS selectors. WieldyMarkup currently only supports tag, class, and ID as part of the selector.

* If you want to specify a tag, then it must come before classes or ID.
* If there is no ID or class, then you must specify a tag.
* If there is at least one class or an ID, then no tag will default to a `DIV`.
* If multiple IDs are present, only the last one will be used.

### Attributes

The list of attributes begins after the first whitespace character after the beginning of the selector. Key-value pairs are identified by three elements:

1. A key containing no whitespace characters or an equals sign (`=`)
2. An equals sign (`=`)
3. Either:
   a string starting with a back tick and ending with the next back tick, between which all characters are ignored
   Or:
   a string ending either at the innerText designation, the last whitespace character before the next `=`, or the end of the line

### InnerText and Self-Closing Designation

If the line ends with `/`, then the tag will be treated as self-closing. If `<` occurs outside of back ticks in the line, then the compiler will consider everything after `<` and before the next `>` in the entire file to be the innerText of the current tag. Anything grouped inside of back ticks within the opening `<` and closing `>` is ignored, even `<` and `>` themselves. The compiler will raise an exception if a closing `>` is not found. Leading whitespace for continuing lines of innerText is ignored and transformed into a single space.
