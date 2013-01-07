# -*- coding: utf-8 -*-
import string, copy

class CompilerException(Exception):
  pass

class Compiler(object):
  """
  Compiles WieldyMarkup to HTML. Each line can take one of the following forms:
    1. selector
    2. selector#id.class href=#
    3. selector#id.class <innerText>
    4. selector.class#id.class data-val=`<%= val %>` <innerText>
    5. input type=text value=This tag is self-closing if line ends with "/" /
    6. selector.class#id.class data-val={{val}} <innerText with embedded `<%= val %>`>
    7. selector#adf.asdf.asf href=# target=_blank data-val=`<%= val %>` <text with embedded
       `<%= val %>` that can spill onto subsequent lines>
    8. `<div id='asdf' class='asdf asd asf'>This tag will be untouched, but initial '`' will be removed</div>
  """
  
  # TODO: Add support for multi-line embedded HTML via "```"
  # TODO: Add support for multiple tags in a single line via "\" delimeter
  # TODO: Improve error reporting for bad syntax
  
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
  
  def __init__(self, text="", compress=False):
    self.output = ""
    self.open_tags = []
    self.indent_token = ""
    self.current_level = 0
    self.previous_level = None
    self.text = text
    self.line_number = 0
    self.embedding_token = '`'
    self.compress = compress
    if self.text != "":
      self.compile()
  
  def compile(self):
    while self.text != "":
      self.process_next_line().process_leading_whitespace(
        ).process_current_level().close_lower_level_tags()
      
      if len(self.stripped_line) > 0:
        if not self.line_starts_with_tick:
          self.split_line().process_selector().process_attributes()
        
        self.add_html_to_output()
    
    while len(self.open_tags) > 0:
      self.close_tag()
    
    return self
  
  def process_next_line(self):
    self.previous_level = self.current_level
    self.line = ""
    self.line_starts_with_tick = False
    self.inner_text_exists = False
    self.self_closing = False
    
    if "\n" in self.text:
      line_break_index = self.text.index("\n")
      self.line = self.text[:line_break_index].rstrip()
      self.text = self.text[line_break_index+1:]
    else:
      self.line = self.text.rstrip()
      self.text = ""
    
    self.stripped_line = self.line.strip()
    
    if len(self.stripped_line) > 0:
      self.line_number += 1
    else:
      return self
    
    # Whole line embedded HTML, starting and ending with back ticks:
    # `content here`
    if self.stripped_line[0] == self.embedding_token:
      self.line = self.line.replace('`', '')
      self.line_starts_with_tick = True
    
    else:
      # Standard markup
      line_without_ticked_groups = self.__class__.remove_grouped_text(self.line, self.embedding_token)
      # innerText is present
      if '<' in line_without_ticked_groups:
        self.inner_text_exists = True
        
        # innerText spilling to proceeding lines
        while '>' not in self.__class__.remove_grouped_text(self.line, self.embedding_token):
          if self.text == "":
            raise CompilerException("Unmatched '<' found on line " + str(self.line_number))
          
          elif "\n" in self.text:
            line_break_index = self.text.index("\n")
            # Guarantee only one space between text between lines.
            self.line += ' ' + self.text[:line_break_index].strip()
            if len(self.text) == line_break_index + 1:
              self.text = ""
            else:
              self.text = self.text[line_break_index+1:]
          
          else:
            self.line += self.text
            self.text = ""
    
        self.stripped_line = self.line.strip()
      
      elif self.line[-1] == '/':
          self.self_closing = True
          self.line = self.line[:-1].rstrip()
    
    return self
  
  def process_leading_whitespace(self):
    self.leading_whitespace = ""
    for i, char in enumerate(self.line):
      if char not in " \t":
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
    
    if self.inner_text_exists:
      # Get innerText without removing any embedded text from it
      if self.embedding_token in everything_else:
        text_copy = copy.copy(everything_else)
        temp_attr_string = ""
        while True:
          open_text_marker_index = text_copy.index('<') if '<' in text_copy else None
          first_tick_index = text_copy.index(self.embedding_token) if self.embedding_token in text_copy else None
          
          if None not in [open_text_marker_index, first_tick_index] and first_tick_index < open_text_marker_index:
            temp_split_text = text_copy.split(self.embedding_token)
            text_copy = ''.join(temp_split_text[2:])
            temp_attr_string += '`'.join(temp_split_text[:2]) + '`'
            
          else:
            open_text_marker_index = text_copy.index('<')
            self.inner_text = text_copy[open_text_marker_index:].strip(string.whitespace + '<>').replace('`', '')
            self.attribute_string = (temp_attr_string + text_copy[:open_text_marker_index]).strip()
            break
      
      else:
        open_text_marker_index = everything_else.index('<')
        self.inner_text = everything_else[open_text_marker_index:].strip(string.whitespace + '<>')
        self.attribute_string = everything_else[:open_text_marker_index].strip()
      
    else:
      self.inner_text = None
      self.attribute_string = everything_else
    
    return self
  
  def process_selector(self):
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
            self.tag_classes.append(self.selector[1:next_delimiter_index])
          
          self.selector = self.selector[next_delimiter_index:]
    
    return self
    
  def process_attributes(self):
    self.tag_attributes = []
    while self.attribute_string != "":
      # If '=' doesn't exist, empty attribute string and break from loop
      if '=' not in self.attribute_string:
        self.attribute_string = ""
        break
      
      first_equals_index = self.attribute_string.index('=')
      parse_normal = True
      
      # If '`' exists
      if self.embedding_token in self.attribute_string:
        parse_normal = False
        
        # If '=' occurs after an embedding token, raise CompilerException
        if self.attribute_string.index(self.embedding_token) < first_equals_index:
          raise CompilerException("No '=' before '`' in line " + str(self.line_number))
        
        # If embedding token occurs immediately after '='
        elif self.attribute_string.index(self.embedding_token) == first_equals_index + 1:
          first_tick_index = first_equals_index + 1
          if len(self.attribute_string) == first_tick_index + 1 or self.embedding_token not in self.attribute_string[first_tick_index+1:]:
            raise CompilerException("Unmatched '`' found in line " + str(self.line_number))
          else:
            second_tick_index = self.attribute_string[first_tick_index + 1:].index(self.embedding_token)
            current_attribute = self.attribute_string[:first_tick_index+1+second_tick_index].replace(self.embedding_token, '')
            if len(self.attribute_string) == first_tick_index+1+second_tick_index+1:
              self.attribute_string = ""
            else:
              self.attribute_string = self.attribute_string[first_tick_index+1+second_tick_index+1:]
        
        else:
          parse_normal = True
        
      if parse_normal:
        if len(self.attribute_string) == first_equals_index+1 or '=' not in self.attribute_string[first_equals_index+1:]:
          current_attribute = self.attribute_string.strip()
          self.attribute_string = ""
        
        else:
          second_equals_index = self.attribute_string[first_equals_index+1:].index('=')
          reversed_letters_between_equals = list(self.attribute_string[first_equals_index+1:first_equals_index+1+second_equals_index])
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
          
          current_attribute = self.attribute_string[:whitespace_index].strip()
          self.attribute_string = self.attribute_string[whitespace_index:]
      
      equals_index = current_attribute.index('=')
      self.tag_attributes.append(
        ' ' + current_attribute[:equals_index] + '="' + current_attribute[equals_index+1:] + '"'
      )
    
    return self

  def add_html_to_output(self):
    if self.line_starts_with_tick:
      self.output += self.line
      if not self.compress:
        self.output += "\n"
    
    else:
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
