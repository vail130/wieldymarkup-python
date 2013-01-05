# -*- coding: utf-8 -*-

"""
PyLMTH.compile
~~~~~~~~~~~~

This module implements PyLMTH.

:copyright: (c) 2013 by Vail Gold.
:license: 

"""
import string

class Compiler(object):
  
  # TODO: Add support for multiple tags in a single line via "\" delimeter
  # TODO: Add some decent error reporting for bad syntax
  
  def __init__(self, text):
    self.output = ""
    self.open_tags = []
    self.indent_token = ""
    self.current_level = 0
    self.previous_level = None
    self.text = text
    self.compile()
  
  def compile(self):
    while self.text != "":
      self.save_current_level_as_previous().process_next_line()
      
      if not self.embedded_html and len(self.stripped_line) > 0:
        self.process_leading_whitespace().process_current_level().close_lower_level_tags(
        ).split_line().process_selector().process_attributes().add_html_to_output()
      
      elif self.embedded_html:
        self.add_html_to_output()
    
    # Iterate remaining indentation levels
    while len(self.open_tags) > 0:
      closing_tag_tuple = self.open_tags.pop()
      # Append closing HTML tags for indentation level with appropriate indentation at beginning of line
      self.output += closing_tag_tuple[0] * self.indent_token + "</" + closing_tag_tuple[1] + ">\n"
    
    return self
  
  def save_current_level_as_previous(self):
    self.previous_level = self.current_level
    return self
  
  def process_next_line(self):
    self.line = ""
    self.embedded_html = False
    
    if "\n" in self.text:
      self.line = self.text[:self.text.index("\n")+1]
    else:
      self.line = self.text
    
    if '`' in self.line:
      first_tick_index = self.line.index('`')
      if "`" not in self.text[first_tick_index:]:
        self.text += "`"
      
      second_tick_index = self.text[first_tick_index:].index("`")
      if "\n" not in self.text[second_tick_index:]:
        self.text += "\n"
      
      line_break_after_second_tick_index = self.text[second_tick_index:].index("\n")
      self.line = self.text[:line_break_after_second_tick_index+1]
      self.embedded_html = True
     
    elif "<" in self.line:
      if ">" not in self.text:
        self.text += ">"
      
      close_text_marker_index = self.text.index(">")
      if "\n" in self.text[close_text_marker_index+1:]:
        self.line = self.text[:close_text_marker_index+1]
      else:
        self.line = self.text
    
    self.text = self.text[len(self.line):]
    self.stripped_line = self.line.strip()
    return self
  
  def process_leading_whitespace(self):
    self.leading_whitespace = ""
    for i, char in enumerate(self.line):
      if char not in string.whitespace:
        self.leading_whitespace = self.line[:i]
        break
    return self
  
  def process_current_level(self):
    if self.leading_whitespace == "":
      self.current_level = 0
    
    # If there is leading whitespace but indent_token is still empty string
    elif self.indent_token == "":
      self.indent_token = self.leading_whitespace
      self.current_level = 1
    
    # Else, set current_level to number of repetitions of index_token in leading_whitespace
    else:
      i = 0
      while self.leading_whitespace.startswith(self.indent_token):
        i += 1
        self.leading_whitespace = self.leading_whitespace[len(self.indent_token):]
      
      self.current_level = i
    
    return self
  
  def close_lower_level_tags(self):
    # If indentation level is less than or equal to previous level
    if self.current_level <= self.previous_level:
      # Close all indentations greater than or equal to indentation level of this line
      while len(self.open_tags) > 0 and self.open_tags[len(self.open_tags) - 1][0] >= self.current_level:
        closing_tag_tuple = self.open_tags.pop()
        self.output += closing_tag_tuple[0] * self.indent_token + "</" + closing_tag_tuple[1] + ">\n"
        
    return self
  
  def split_line(self):
    # Find first occurence of whitespace
    first_whitespace_index = None
    for i, char in enumerate(self.stripped_line):
      if char in string.whitespace:
        first_whitespace_index = i
        break
    
    # Split the stripped_line into 2 pieces at the first occurence of whitespace
    if first_whitespace_index is None:
      self.selector = self.stripped_line
      everything_else = ""
    
    else:
      self.selector = self.stripped_line[0:first_whitespace_index]
      everything_else = self.stripped_line[first_whitespace_index:].strip()
    
    if '<' in everything_else:
      open_text_marker_index = everything_else.index('<')
      self.inner_text = everything_else[open_text_marker_index:].strip(string.whitespace + '<>')
      self.attribute_string = everything_else[:open_text_marker_index].strip()
      
    else:
      self.inner_text = None
      self.attribute_string = everything_else
    
    return self
  
  def process_selector(self):
    # Check for self-closing designation
    if len(self.selector) > 0 and self.selector[0] == '-':
      self.self_closing = True
      self.self_closing_type = 1
      self.selector = self.selector[1:]
    
    elif len(self.selector) > 0 and self.selector[0] == '=':
      self.self_closing = True
      self.self_closing_type = 2
      self.selector = self.selector[1:]
    
    else:
      self.self_closing = False
    
    # Parse the first piece as a selector, defaulting to DIV tag if none is specified
    if len(self.selector) > 0 and self.selector[0] in ['#', '.']:
      self.tag = 'div'
    else:
      delimiter_index = None
      for i, char in enumerate(self.selector):
        if char in ['#', '.']:
          delimiter_index = i
          break
      
      if delimiter_index is None:
        self.tag = self.selector
        self.selector = ""
      else:
        self.tag = self.selector[:delimiter_index]
        self.selector = self.selector[len(self.tag):]
    
    self.tag_id = None
    self.tag_classes = []
    while True:
      next_delimiter_index = None
      if self.selector == "":
        break
      
      else:
        for i, char in enumerate(self.selector):
          if i > 0 and char in ['#', '.']:
            next_delimiter_index = i
            break
        
        if next_delimiter_index is None:
          if self.selector[0] == '#':
            self.tag_id = self.selector[1:]
          elif self.selector[0] == ".":
            self.tag_classes.append(self.selector[1:])
          
          self.selector = ""
        
        else:
          if self.selector[0] == '#':
            self.tag_id = self.selector[1:next_delimiter_index]
          elif self.selector[0] == ".":
            tag_classes.append(self.selector[1:next_delimiter_index])
          
          self.selector = self.selector[next_delimiter_index:]
    
    return self
    
  def process_attributes(self):
    self.tag_attributes = []
    while self.attribute_string != "":
      try:
        first_equals_index = self.attribute_string.index('=')
      except (IndexError, ValueError):
        self.attribute_string = ""
      else:
        
        try:
          second_equals_index = self.attribute_string[first_equals_index+1:].index('=')
        except (IndexError, ValueError):
          current_attribute = self.attribute_string
          self.attribute_string = ""
        else:
          reversed_letters_between_equals = list(self.attribute_string[first_equals_index+1:second_equals_index])
          reversed_letters_between_equals.reverse()
          
          whitespace_index = None
          for i, char in enumerate(reversed_letters_between_equals):
            try:
              string.whitespace.index(char)
            except (IndexError, ValueError):
              pass
            else:
              whitespace_index = second_equals_index - i
              break
          
          if whitespace_index is None:
            # TODO: Do some error reporting here
            break
          
          current_attribute = self.attribute_string[:whitespace_index].strip()
          self.attribute_string = self.attribute_string[whitespace_index:]
        
        equals_index = current_attribute.index('=')
        self.tag_attributes.append(
          ' ' + current_attribute[:equals_index] + '="' + current_attribute[equals_index+1:] + '"'
        )
    
    return self

  def add_html_to_output(self):
    if self.embedded_html:
      self.output += self.line.replace('`', '')
    
    else:
      tag_html = "<" + self.tag
      
      if self.tag_id is not None:
        tag_html += ' id="' + self.tag_id + '"'
        
      if len(self.tag_classes) > 0:
        tag_html += ' class="' + ' '.join(self.tag_classes) + '"'
      
      if len(self.tag_attributes) > 0:
        tag_html += ''.join(self.tag_attributes)
      
      if self.self_closing:
        if self.self_closing_type is 2:
          tag_html += '>'
        else:
          tag_html += ' />'
        
        self.output += self.current_level * self.indent_token + tag_html + '\n'
      
      else:
        tag_html += '>'
        
        if self.inner_text is not None:
          tag_html += self.inner_text
        
        self.output += self.current_level * self.indent_token + tag_html
        
        print self.inner_text
        
        if self.inner_text is None:
          self.output += '\n'
          # Add tag data to open_tags list
          self.open_tags.append(
            (self.current_level, self.tag)
          )
    
        else:
          self.output += "</" + self.tag + ">\n"
    
    return self