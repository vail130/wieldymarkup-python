import six

if six.PY3:
  import unittest
else:
  import unittest2 as unittest

from wieldymarkup.compile import Compiler, CompilerException

class TestCompiler(unittest.TestCase):

  def setUp(self):
    pass

  def test_init_values(self):
    c = Compiler()
    comparison_values = [
      ('output', ''),
      ('open_tags', []),
      ('indent_token', ''),
      ('current_level', 0),
      ('previous_level', None),
      ('text', ''),
      ('line_number', 0),
      ('embedding_token', '`'),
      ('compress', False),
    ]
    
    for cv in comparison_values:
      self.assertEqual(getattr(c, cv[0]), cv[1])
  
  def test_remove_grouped_text(self):
    c = Compiler()
    sample = "The cat ran 'into the big 'home!"
    expected = "The cat ran home!"
    self.assertEqual(c.__class__.remove_grouped_text(sample, "'"), expected)
    
    c = Compiler()
    sample = "The cat ran 'into the big home!"
    expected = "The cat ran "
    self.assertEqual(c.__class__.remove_grouped_text(sample, "'"), expected)
    
    c = Compiler()
    sample = "The cat ran `into the big `home!"
    expected = "The cat ran home!"
    self.assertEqual(c.__class__.remove_grouped_text(sample, "`"), expected)
  
  def test_process_next_line(self):
    c = Compiler()
    c.text = "div\ndiv"
    c.process_next_line()
    self.assertEqual(c.line, "div")
    self.assertEqual(c.text, "div")
   
    c = Compiler()
    c.text = "div.class#id data-val=val data-val2=val2\ndiv\n"
    c.process_next_line()
    self.assertEqual(c.line, "div.class#id data-val=val data-val2=val2")
    self.assertEqual(c.text, "div\n")
    
    c = Compiler()
    c.text = "div.class#id data-val=val data-val2=val2 <Content goes here>\ndiv"
    c.process_next_line()
    self.assertEqual(c.line, "div.class#id data-val=val data-val2=val2 <Content goes here>")
    self.assertEqual(c.inner_text_exists, True)
    self.assertEqual(c.line_starts_with_tick, False)
    
    c = Compiler()
    c.text = "input.class#id type=text value=Content goes here / \ndiv"
    c.process_next_line()
    self.assertEqual(c.line, "input.class#id type=text value=Content goes here")
    self.assertEqual(c.self_closing, True)
    
    c = Compiler()
    c.text = "div.class#id data-val=val data-val2=val2 <Content goes\nhere>\ndiv"
    c.process_next_line()
    self.assertEqual(c.line, "div.class#id data-val=val data-val2=val2 <Content goes here>")
    self.assertEqual(c.inner_text_exists, True)
    
    c = Compiler()
    c.text = "div.class#id data-val=val data-val2=val2 <Content goes\nhere\ndiv"
    self.assertRaises(CompilerException, c.process_next_line)
    
    c = Compiler()
    c.text = "    div.class#id data-val=val data-val2=`<%= val2 %>` <Content `<i>haya!</i>` goes\nhere>\ndiv"
    c.process_next_line()
    self.assertEqual(c.line, "    div.class#id data-val=val data-val2=`<%= val2 %>` <Content `<i>haya!</i>` goes here>")
    self.assertEqual(c.stripped_line, "div.class#id data-val=val data-val2=`<%= val2 %>` <Content `<i>haya!</i>` goes here>")
    self.assertEqual(c.inner_text_exists, True)
    
    c = Compiler()
    c.text = "`<div class='class' id='id'>Content goes here</div>\ndiv"
    c.process_next_line()
    self.assertEqual(c.line, "<div class='class' id='id'>Content goes here</div>")
    self.assertEqual(c.line_starts_with_tick, True)
    
  def test_process_leading_whitespace(self):
    c = Compiler()
    c.line = "    `<div class='class' id='id'>Content goes here</div>"
    c.process_leading_whitespace()
    self.assertEqual(c.leading_whitespace, "    ")
    
    c = Compiler()
    c.line = "\t\tdiv.class#id data-val=val data-val2=`<%= val2 %>` <Content `<i>haya!</i>` goes here>"
    c.process_leading_whitespace()
    self.assertEqual(c.leading_whitespace, "\t\t")
    
    c = Compiler()
    c.line = "\n  div.class#id data-val=val data-val2=`<%= val2 %>` <Content `<i>haya!</i>` goes here>"
    c.process_leading_whitespace()
    self.assertEqual(c.leading_whitespace, "")
  
  def test_process_current_level(self):
    c = Compiler()
    c.leading_whitespace = "    "
    c.process_current_level()
    self.assertEqual(c.current_level, 1)
    self.assertEqual(c.indent_token, "    ")
    
    c = Compiler()
    c.leading_whitespace = "    "
    c.indent_token = "  "
    c.process_current_level()
    self.assertEqual(c.current_level, 2)
    self.assertEqual(c.indent_token, "  ")
    
    c = Compiler()
    c.leading_whitespace = "\t\t"
    c.indent_token = "\t"
    c.process_current_level()
    self.assertEqual(c.current_level, 2)
    self.assertEqual(c.indent_token, "\t")
    
  def test_close_tag(self):
    c = Compiler()
    c.indent_token = "  "
    c.open_tags = [(0, "div")]
    c.close_tag()
    self.assertEqual(c.output, "</div>\n")
    self.assertEqual(c.open_tags, [])
    
    c = Compiler('', compress=True)
    c.indent_token = "  "
    c.open_tags = [(0, "div")]
    c.close_tag()
    self.assertEqual(c.output, "</div>")
    self.assertEqual(c.open_tags, [])
  
  def test_close_lower_level_tags(self):
    c = Compiler()
    c.current_level = 0
    c.previous_level = 2
    c.indent_token = "  "
    c.open_tags = [
      (0, "div"),
      (1, "div"),
      (2, "span"),
    ]
    c.close_lower_level_tags()
    self.assertEqual(c.output, "    </span>\n  </div>\n</div>\n")
    
    c = Compiler('', compress=True)
    c.current_level = 0
    c.previous_level = 2
    c.indent_token = "  "
    c.open_tags = [
      (0, "div"),
      (1, "div"),
      (2, "span"),
    ]
    c.close_lower_level_tags()
    self.assertEqual(c.output, "</span></div></div>")
  
  def test_split_line(self):
    c = Compiler()
    c.stripped_line = "div"
    c.inner_text_exists = False
    c.split_line()
    self.assertEqual(c.selector, "div")
    self.assertEqual(c.attribute_string, "")
    self.assertEqual(c.inner_text, None)
    
    c = Compiler()
    c.stripped_line = "div.class#id data-val=val"
    c.inner_text_exists = False
    c.split_line()
    self.assertEqual(c.selector, "div.class#id")
    self.assertEqual(c.attribute_string, "data-val=val")
    self.assertEqual(c.inner_text, None)
    
    c = Compiler()
    c.inner_text_exists = True
    c.stripped_line = "div.class#id data-val=val data-val2=`<%= val2 %>` <Content `<i>haya!</i>` goes here>"
    c.split_line()
    self.assertEqual(c.selector, "div.class#id")
    self.assertEqual(c.attribute_string, "data-val=val data-val2=`<%= val2 %>`")
    self.assertEqual(c.inner_text, "Content <i>haya!</i> goes here")
  
  def test_process_selector(self):
    c = Compiler()
    c.selector = "div"
    c.process_selector()
    self.assertEqual(c.tag, "div")
    self.assertEqual(c.tag_id, None)
    self.assertEqual(c.tag_classes, [])
    
    c = Compiler()
    c.selector = ".class#id"
    c.process_selector()
    self.assertEqual(c.tag, "div")
    self.assertEqual(c.tag_id, "id")
    self.assertEqual(c.tag_classes, ['class'])
    
    c = Compiler()
    c.selector = "input.class1#id1.class2#id2"
    c.process_selector()
    self.assertEqual(c.tag, "input")
    self.assertEqual(c.tag_id, "id2")
    self.assertEqual(c.tag_classes, ['class1', 'class2'])
  
  def test_process_attributes(self):
    pass
  
  def test_add_html_to_output(self):
    pass
  
