# -*- coding: utf-8 -*-
import string, copy, re

class CompilerException(Exception):
  pass

class Compiler(object):
  """
  """
  
  embedding_token = '`'
  
  @staticmethod
  def remove_grouped_text(text, z):
    output = ""
    text_copy = copy.copy(text)
    status = True
    while text_copy != '':
      try:
        grouper_index = text_copy.index(z)
      except (IndexError, ValueError):
        if status:
          output += text_copy
        text_copy = ''
      else:
        if status:
          output += text_copy[:grouper_index]
        try:
          text_copy = text_copy[grouper_index+1:]
        except IndexError:
          text_copy = ''
      status = not status
    return output
  
  @staticmethod
  def get_selector_from_line(line):
    first_whitespace_index = None
    for i, char in enumerate(line):
      if char in string.whitespace:
        first_whitespace_index = i
        break
    if first_whitespace_index is None:
      return line
    else:
      return line[:first_whitespace_index]
  
  @staticmethod
  def get_tag_nest_level(text, open_string='<', close_string='>'):
    text = copy.copy(text)
    nest_level = 0
    while True:
      open_string_index = text.index(open_string) if open_string in text else None
      close_string_index = text.index(close_string) if close_string in text else None
      open_string_first = False
      close_string_first = False
      
      # Only same if both None
      if open_string_index is close_string_index:
        break
      elif open_string_index is not None:
        open_string_first = True
      elif close_string_index is not None:
        close_string_first = True
      else:
        if open_string_index < close_string_index:
          open_string_first = True
        else:
          close_string_first = True
      
      if open_string_first:
        nest_level += 1
        if len(text) is open_string_index+len(open_string):
          break
        else:
          text = text[open_string_index+len(open_string):]
      elif close_string_first:
        nest_level -= 1
        if len(text) is close_string_index+len(close_string):
          break
        else:
          text = text[close_string_index+len(close_string):]
    
    return nest_level
  
  @staticmethod
  def get_leading_whitespace_from_text(text):
    leading_whitespace = ""
    for i, char in enumerate(text):
      if char not in " \t":
        leading_whitespace = text[:i]
        break
    return leading_whitespace
  
  def __init__(self, text="", compress=False):
    self.compile(text, compress)
  
  def compile(self, text="", compress=False):
    self.text = str(text)
    self.compress = not not compress
    self.output = ""
    self.open_tags = []
    self.indent_token = ""
    self.current_level = 0
    self.previous_level = None
    self.text = text
    self.line_number = 0
    
    while self.text != "":
      self.process_current_level().close_lower_level_tags().process_next_line()
      
    while len(self.open_tags) > 0:
      self.close_tag()
    
    return self
  
  def process_current_level(self):
    self.previous_level = self.current_level
    leading_whitespace = self.__class__.get_leading_whitespace_from_text(self.text)
    if leading_whitespace == "":
      self.current_level = 0
    
    # If there is leading whitespace but indent_token is still empty string
    elif self.indent_token == "":
      self.indent_token = leading_whitespace
      self.current_level = 1
    
    # Else, set current_level to number of repetitions of index_token in leading_whitespace
    else:
      i = 0
      while leading_whitespace.startswith(self.indent_token):
        i += 1
        leading_whitespace = leading_whitespace[len(self.indent_token):]
      self.current_level = i
    
    return self
  
  def close_lower_level_tags(self):
    # If indentation level is less than or equal to previous level
    if self.current_level <= self.previous_level:
      # Close all indentations greater than or equal to indentation level of this line
      while len(self.open_tags) > 0 and self.open_tags[len(self.open_tags) - 1][0] >= self.current_level:
        self.close_tag()
    return self
  
  def close_tag(self):
    closing_tag_tuple = self.open_tags.pop()
    if not self.compress:
      self.output += closing_tag_tuple[0] * self.indent_token
    self.output += "</" + closing_tag_tuple[1] + ">"
    if not self.compress:
      self.output += "\n"
    return self
  
  def process_next_line(self):
    self.line_starts_with_tick = False
    self.self_closing = False
    self.inner_text = None
    
    line = ""
    
    if "\n" in self.text:
      line_break_index = self.text.index("\n")
      line = self.text[:line_break_index].strip()
      self.text = self.text[line_break_index+1:]
    else:
      line = self.text.strip()
      self.text = ""
    
    self.line_number += 1
    if len(line) is 0:
      return self
    
    # Whole line embedded HTML, starting with back ticks:
    if line[0] == self.__class__.embedding_token:
      self.process_embedded_line(line)
    
    else:
      # Support multiple tags on one line via "\-\" delimiter
      line_split_list = line.split('\\-\\')
      while len(line_split_list) > 1:
        temp_line = line_split_list.pop(0).strip()
        selector = self.__class__.get_selector_from_line(temp_line)
        self.process_selector(copy.copy(selector))
        rest_of_line = temp_line[len(selector):].strip()
        rest_of_line = self.process_attributes(rest_of_line)
        self.add_html_to_output()
        
        self.tag = None
        self.tag_id = None
        self.tag_classes = []
        self.tag_attributes = []
        self.previous_level = self.current_level
        self.current_level += 1
      
      line = line_split_list[len(line_split_list) - 1].strip()
      selector = self.__class__.get_selector_from_line(line)
      self.process_selector(copy.copy(selector))
      rest_of_line = line[len(selector):].strip()
      rest_of_line = self.process_attributes(rest_of_line)
      
      if rest_of_line.startswith('<'):
        self.inner_text = rest_of_line
        if self.__class__.get_tag_nest_level(self.inner_text) < 0:
          raise CompilerException("Too many '>' found on line " + str(self.line_number))
        
        while self.__class__.get_tag_nest_level(self.inner_text) > 0:
          if self.text == "":
            raise CompilerException("Unmatched '<' found on line " + str(self.line_number))
          
          elif "\n" in self.text:
            line_break_index = self.text.index("\n")
            # Guarantee only one space between text between lines.
            self.inner_text += ' ' + self.text[:line_break_index].strip()
            if len(self.text) == line_break_index + 1:
              self.text = ""
            else:
              self.text = self.text[line_break_index+1:]
          
          else:
            self.inner_text += self.text
            self.text = ""
        
        self.inner_text = self.inner_text.strip()[1:-1]
      
      elif rest_of_line.startswith('/'):
        if len(rest_of_line) > 0 and rest_of_line[-1] == '/':
          self.self_closing = True
      
      self.add_html_to_output()
    
    return self
  
  def process_embedded_line(self, line):
    self.line_starts_with_tick = True
    if not self.compress:
      self.output += self.current_level * self.indent_token
    self.output += line[1:]
    if not self.compress:
      self.output += "\n"
    return self
  
  def process_selector(self, selector):
    # Parse the first piece as a selector, defaulting to DIV tag if none is specified
    if len(selector) > 0 and selector[0] in ['#', '.']:
      self.tag = 'div'
    else:
      delimiter_index = None
      for i, char in enumerate(selector):
        if char in ['#', '.']:
          delimiter_index = i
          break
      
      if delimiter_index is None:
        self.tag = selector
        selector = ""
      else:
        self.tag = selector[:delimiter_index]
        selector = selector[len(self.tag):]
    
    self.tag_id = None
    self.tag_classes = []
    while True:
      next_delimiter_index = None
      if selector == "":
        break
      
      else:
        for i, char in enumerate(selector):
          if i > 0 and char in ['#', '.']:
            next_delimiter_index = i
            break
        
        if next_delimiter_index is None:
          if selector[0] == '#':
            self.tag_id = selector[1:]
          elif selector[0] == ".":
            self.tag_classes.append(selector[1:])
          
          selector = ""
        
        else:
          if selector[0] == '#':
            self.tag_id = selector[1:next_delimiter_index]
          elif selector[0] == ".":
            self.tag_classes.append(selector[1:next_delimiter_index])
          
          selector = selector[next_delimiter_index:]
    
    return self
    
  def process_attributes(self, rest_of_line):
    self.tag_attributes = []
    while rest_of_line != "":
      # If '=' doesn't exist, empty attribute string and break from loop
      if '=' not in rest_of_line:
        break
      elif '=' in rest_of_line and '<' in rest_of_line and rest_of_line.index('<') < rest_of_line.index('='):
        break
      
      first_equals_index = rest_of_line.index('=')
      embedded_attribute = False
      
      if rest_of_line[first_equals_index+1:first_equals_index+3] == '{{':
        embedded_attribute = True
        try:
          close_index = rest_of_line.index('}}')
        except ValueError:
          raise CompilerException("Unmatched '{{' found in line " + str(self.line_number))
      elif rest_of_line[first_equals_index+1:first_equals_index+3] == '<%':
        embedded_attribute = True
        try:
          close_index = rest_of_line.index('%>')
        except ValueError:
          raise CompilerException("Unmatched '<%' found in line " + str(self.line_number))
      
      if embedded_attribute:
        current_attribute = rest_of_line[:close_index+2]
        if len(rest_of_line) == close_index+2:
          rest_of_line = ""
        else:
          rest_of_line = rest_of_line[close_index+2:]
      
      elif len(rest_of_line) == first_equals_index+1:
        current_attribute = rest_of_line.strip()
        rest_of_line = ""
      
      elif '=' not in rest_of_line[first_equals_index+1:]:
        if '<' in rest_of_line:
          current_attribute = rest_of_line[:rest_of_line.index('<')].strip()
          rest_of_line = rest_of_line[rest_of_line.index('<'):]
        else:
          current_attribute = rest_of_line
          rest_of_line = ""
      
      else:
        second_equals_index = rest_of_line[first_equals_index+1:].index('=')
        reversed_letters_between_equals = list(rest_of_line[first_equals_index+1:first_equals_index+1+second_equals_index])
        reversed_letters_between_equals.reverse()
        
        whitespace_index = None
        for i, char in enumerate(reversed_letters_between_equals):
          try:
            string.whitespace.index(char)
          except (IndexError, ValueError):
            pass
          else:
            whitespace_index = first_equals_index+1+second_equals_index - i
            break
        
        if whitespace_index is None:
          # TODO: Do some error reporting here
          break
        
        current_attribute = rest_of_line[:whitespace_index].strip()
        rest_of_line = rest_of_line[whitespace_index:]
      
      if current_attribute is not None:
        equals_index = current_attribute.index('=')
        self.tag_attributes.append(
          ' ' + current_attribute[:equals_index] + '="' + current_attribute[equals_index+1:] + '"'
        )
    
    return rest_of_line.strip()

  def add_html_to_output(self):
    if not self.line_starts_with_tick:
      tag_html = "<" + self.tag
      
      if self.tag_id is not None:
        tag_html += ' id="' + self.tag_id + '"'
        
      if len(self.tag_classes) > 0:
        tag_html += ' class="' + ' '.join(self.tag_classes) + '"'
      
      if len(self.tag_attributes) > 0:
        tag_html += ''.join(self.tag_attributes)
      
      if self.self_closing:
        tag_html += ' />'
        if not self.compress:
          self.output += self.current_level * self.indent_token
        self.output += tag_html
        if not self.compress:
          self.output += '\n'
      
      else:
        tag_html += '>'
        
        if self.inner_text is not None:
          tag_html += self.inner_text
        
        if not self.compress:
          self.output += self.current_level * self.indent_token
        self.output += tag_html
        
        if self.inner_text is None:
          if not self.compress:
            self.output += '\n'
          # Add tag data to open_tags list
          self.open_tags.append(
            (self.current_level, self.tag)
          )
    
        else:
          self.output += "</" + self.tag + ">"
          if not self.compress:
            self.output += "\n"
    
    return self
