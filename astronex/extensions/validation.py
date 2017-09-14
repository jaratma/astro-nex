''' Shamelessly stolen and adapted from Kiwi framework '''
import gobject
import pango
import gtk
from gtk import gdk,keysyms
import datetime
from pytz import timezone
import time


class MaskError(Exception):
    pass

class ValidationError(Exception):
    def __init__(self, msg):
        self.msg = msg

def set_background(widget, color, state=gtk.STATE_NORMAL): 
    widget.modify_base(state, gdk.color_parse(color))

(INPUT_ASCII_LETTER,
 INPUT_ALPHA,
 INPUT_ALPHANUMERIC,
 INPUT_DIGIT) = range(4)

INPUT_FORMATS = {
    '0': INPUT_DIGIT,
    'L': INPUT_ASCII_LETTER,
    'A': INPUT_ALPHANUMERIC,
    'a': INPUT_ALPHANUMERIC,
    '&': INPUT_ALPHA,
    }

INPUT_CHAR_MAP = {
    INPUT_ASCII_LETTER: lambda txt: txt in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ',
    INPUT_ALPHA:            unicode.isalpha,
    INPUT_ALPHANUMERIC:     unicode.isalnum,
    INPUT_DIGIT:            unicode.isdigit,
    }


class MaskEntry(gtk.Entry):
    __gproperties__ = { 'mask': (gobject.TYPE_STRING, '','', '' , gobject.PARAM_READWRITE) }

    def __init__(self):

        gtk.Entry.__init__(self)

        self.connect('insert-text', self._on_insert_text)
        self.connect('delete-text', self._on_delete_text)

        #  validators:  str -> static  int -> dynamic
        self._mask_validators = []
        self._mask = None
        self._block_insert = False
        self._block_delete = False
        self.set_property('xalign', 1.0)

    # Public API 
    def set_mask(self, mask):
        mask = unicode(mask)
        if not mask:
            self.modify_font(pango.FontDescription("sans"))
            self._mask = mask
            return

        input_length = len(mask)
        lenght = 0
        pos = 0
        while True:
            if pos >= input_length:
                break
            if mask[pos] in INPUT_FORMATS:
                self._mask_validators += [INPUT_FORMATS[mask[pos]]]
            else:
                self._mask_validators.append(mask[pos])
            pos += 1

        self.modify_font(pango.FontDescription("monospace"))

        self.set_text("")
        self._insert_mask(0, input_length)
        self._mask = mask

    def get_mask(self):
        return self._mask

    def get_field_text(self):
        if not self._mask:
            raise MaskError("a mask must be set before calling get_field_text")

        def append_field(fields, field_type, s):
            if s.count(' ') == len(s):
                s = ''
            if field_type == INPUT_DIGIT:
                try:
                    s = int(s)
                except ValueError:
                    s = None
            fields.append(s)

        fields = []
        pos = 0
        s = ''
        field_type = -1
        text = unicode(self.get_text())
        validators = self._mask_validators
        while True:
            if pos >= len(validators):
                append_field(fields, field_type, s)
                break

            validator = validators[pos]
            if isinstance(validator, int):
                try:
                    s += text[pos]
                except IndexError:
                    s = ''
                field_type = validator
            else:
                append_field(fields, field_type, s)
                s = ''
                field_type = -1
            pos += 1

        return fields

    def get_empty_mask(self, start=None, end=None):
        if start is None:
            start = 0
        if end is None:
            end = len(self._mask_validators)

        s = ''
        for validator in self._mask_validators[start:end]:
            if isinstance(validator, int):
                s += ' '
            elif isinstance(validator, unicode):
                s += validator
            else:
                raise AssertionError
        return s

    # Private 
    def _really_delete_text(self, start, end):
        self._block_delete = True
        self.delete_text(start, end)
        self._block_delete = False

    def _really_insert_text(self, text, position):
        self._block_insert = True
        self.insert_text(text, position)
        self._block_insert = False

    def _insert_mask(self, start, end):
        text = self.get_empty_mask(start, end)
        self._really_insert_text(text, position=start)

    def _confirms_to_mask(self, position, text):
        validators = self._mask_validators
        if position >= len(validators):
            return False

        validator = validators[position]
        if isinstance(validator, int):
            if not INPUT_CHAR_MAP[validator](text):
                return False
        if isinstance(validator, unicode):
            if validator == text:
                return True
            return False

        return True

    # Callbacks 
    def _on_insert_text(self, editable, new, length, position):
        if not self._mask or self._block_insert:
            return

        position = self.get_position()
        new = unicode(new)
        for inc, c in enumerate(new):
            if not self._confirms_to_mask(position + inc, c):
                self.stop_emission('insert-text')
                return

            self._really_delete_text(position, position+1)

        next = position + 1
        validators = self._mask_validators
        if len(validators) > next + 1:
            if (isinstance(validators[next], unicode) and
                isinstance(validators[next+1], int)):
                gobject.idle_add(self.set_position, next+1)

    def _on_delete_text(self, editable, start, end):
        if not self._mask or self._block_delete:
            return
        self._really_delete_text(start, end)
        self._insert_mask(start, end)
        self.stop_emission('delete-text')


